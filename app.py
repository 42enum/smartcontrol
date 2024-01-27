from flask import Flask, render_template, redirect, url_for, request, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import (
    LoginManager,
    UserMixin,
    login_user,
    login_required,
    logout_user,
    current_user,
)
from flask_migrate import Migrate
from dotenv import load_dotenv
from flask_wtf import FlaskForm
from werkzeug.security import generate_password_hash, check_password_hash
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired
import os
import uuid
from sqlalchemy import cast, String


# Config
load_dotenv()

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URI")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY")

with app.app_context():
    db = SQLAlchemy(app)
    migrate = Migrate(app, db)
    login_manager = LoginManager(app)
    login_manager.login_view = "login"
    db.create_all()


# Models
class User(db.Model, UserMixin):
    id = db.Column(db.String(36), primary_key=True, default=str(uuid.uuid4()))
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), nullable=False, default="user")  # "user" or "admin"


class IRCommand(db.Model):
    id = db.Column(db.String(36), primary_key=True, default=str(uuid.uuid4()))
    model = db.Column(db.String(50), unique=True, nullable=False)
    raw_on = db.Column(db.String(2000), nullable=False)
    raw_off = db.Column(db.String(2000), nullable=False)


class Equipment(db.Model):
    id = db.Column(db.String(36), primary_key=True, default=str(uuid.uuid4()))
    model = db.Column(db.String(50), nullable=False)
    brand = db.Column(db.String(50), nullable=False)
    active = db.Column(db.Boolean, default=True)
    condition = db.Column(
        db.String(20), nullable=False, default="ok"
    )  # "ok" or "maintenance"
    building = db.Column(db.String(20), nullable=False)
    room = db.Column(db.String(20), nullable=False)
    esp_address = db.Column(db.String(128))


# Auth
class LoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Login")


def is_admin() -> bool:
    return current_user.role == "admin"


# This is necessary so is_admin() can be used in the html templates
app.jinja_env.globals.update(is_admin=is_admin)


@login_manager.user_loader
def load_user(user_id):
    try:
        # Try to convert the provided user_id to UUID
        user_uuid = uuid.UUID(user_id)
    except ValueError:
        return None

    # Query the user based on the UUID
    return User.query.filter(cast(User.id, String) == str(user_uuid)).first()


# Routes
@app.route("/")
def home():
    return render_template("home.html", current_user=current_user)


@app.route("/make_post_request", methods=["POST"])
def make_post_request():
    # Get data from the POST request
    data = request.json

    # Perform any processing needed before making the external API request

    # Make the external API request (replace with your actual API endpoint)
    # For example, using the 'requests' library
    # import requests
    # response = requests.post('https://api.example.com/endpoint', json=data)

    # For demonstration purposes, return a JSON response
    return jsonify(
        {"status": "success", "message": "POST request sent to external API"}
    )


@app.route("/admin_page")
@login_required
def admin_page():
    if not is_admin():
        return f"You do not have permission to access this page. Your current role is {current_user.role}"
    return render_template("admin_page.html", user=current_user)


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        # Check if the username already exists
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash("Username already exists. Please choose a different one.", "danger")
            return redirect(url_for("register"))

        # Hash the password before storing it
        password_hash = generate_password_hash(password)

        new_user = User(username=username, password_hash=password_hash)
        db.session.add(new_user)
        db.session.commit()

        flash("Registration successful! You can now log in.", "success")
        return redirect(url_for("login"))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()

    if request.method == "POST" and form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            flash("Login successful!", "success")
            return redirect(url_for("home"))
        else:
            flash("Invalid username or password. Please try again.", "danger")

    return render_template("login.html", form=form)


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("home"))


if __name__ == "__main__":
    app.run(debug=True)
