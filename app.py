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
from flask_bcrypt import Bcrypt
from sqlalchemy import cast, String
import requests

# Config
load_dotenv()

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URI")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY")
app.config['ERROR_404_HELP'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)
login_manager = LoginManager(app)
login_manager.login_view = "login"
bcrypt = Bcrypt()

with app.app_context():
    db.create_all()


# Models
class User(db.Model, UserMixin):
    id = db.Column(db.String(36), primary_key=True, default=str(uuid.uuid4()))
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), nullable=False, default="user")  # "user" or "admin"


class IRCommand(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    model = db.Column(db.String(50), unique=True, nullable=False)
    raw_on = db.Column(db.String(2000), nullable=False)
    raw_off = db.Column(db.String(2000), nullable=False)


class Equipment(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
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


# Database
def get_buildings():
    distinct_buildings = (
        Equipment.query.with_entities(Equipment.building).distinct().all()
    )
    distinct_buildings = [buildings[0] for buildings in distinct_buildings]
    distinct_buildings.sort()

    return distinct_buildings


@app.context_processor
def inject_buildings():
    # Make the buildings available to all templates
    buildings = get_buildings()
    return dict(buildings=buildings)


# Routes
@app.route("/")
def home():
    return redirect(url_for("dashboard"))


@app.route("/dashboard")
@login_required
def dashboard():
    return render_template("dashboard.html")


@app.route("/building/<building>")
@login_required
def building_detail(building):
    equipment_in_building = Equipment.query.filter_by(building=building).all()

    return render_template(
        "building_detail.html",
        building=building,
        equipment_list=equipment_in_building,
    )


@app.route("/admin")
@login_required
def admin_page():
    if not is_admin():
        return f"You do not have permission to access this page. Your current role is {current_user.role}"

    equipment_list = Equipment.query.all()
    ir_commands = IRCommand.query.all()

    return render_template(
        "admin.html",
        user=current_user,
        equipment_list=equipment_list,
        ir_commands=ir_commands,
    )


@app.route("/admin/add_ir_command", methods=["GET", "POST"])
@login_required
def add_ir_command():
    if not is_admin():
        return f"You do not have permission to access this page. Your current role is {current_user.role}"

    if request.method == "POST":
        model = request.form.get("model")
        raw_on = request.form.get("raw_on").replace(" ", "")
        raw_off = request.form.get("raw_off").replace(" ", "")

        # Check if the command for the model already exists
        existing_item = IRCommand.query.filter_by(model=model).first()

        if existing_item:
            flash(
                "Command with the same model already exists. Choose a different name.",
                "danger",
            )
            return redirect(url_for("add_ir_command"))

        new_ir_command = IRCommand(model=model, raw_on=raw_on, raw_off=raw_off)
        db.session.add(new_ir_command)
        db.session.commit()

        return redirect(url_for("admin_page"))

    return render_template("add_ir_command.html")


@app.route("/admin/add_equipment", methods=["GET", "POST"])
@login_required
def add_equipment():
    if not is_admin():
        return f"You do not have permission to access this page. Your current role is {current_user.role}"

    if request.method == "POST":
        brand = request.form.get("brand")
        model = request.form.get("model")
        building = request.form.get("building")
        room = request.form.get("room")
        esp_address = request.form.get("esp_address")

        new_equipment = Equipment(
            model=model,
            brand=brand,
            building=building,
            room=room,
            esp_address=esp_address,
        )
        db.session.add(new_equipment)
        db.session.commit()

        return redirect(url_for("admin_page"))

    return render_template("add_equipment.html")


@app.route("/admin/edit_ir_command/<ir_command_id>", methods=["GET", "POST"])
@login_required
def edit_ir_command(ir_command_id):
    if not is_admin():
        return f"You do not have permission to access this page. Your current role is {current_user.role}"

    ir_command = IRCommand.query.get_or_404(ir_command_id)

    if request.method == "POST":
        ir_command.model = request.form.get("model")
        ir_command.raw_on = request.form.get("raw_on").replace(" ", "")
        ir_command.raw_off = request.form.get("raw_off").replace(" ", "")

        db.session.commit()

        return redirect(url_for("admin_page"))

    return render_template("edit_ir_command.html", ir_command=ir_command)


@app.route("/admin/edit_equipment/<equipment_id>", methods=["GET", "POST"])
@login_required
def edit_equipment(equipment_id):
    if not is_admin():
        return f"You do not have permission to access this page. Your current role is {current_user.role}"

    equipment = Equipment.query.get_or_404(equipment_id)

    if request.method == "POST":
        equipment.brand = request.form.get("brand")
        equipment.model = request.form.get("model")
        equipment.building = request.form.get("building")
        equipment.room = request.form.get("room")
        equipment.esp_address = request.form.get("esp_address")

        db.session.commit()

        return redirect(url_for("admin_page"))

    return render_template("edit_equipment.html", equipment=equipment)


@app.route("/request_to_esp", methods=["POST"])
def request_to_esp():
    data = request.json
    equipment_id = data["id"]

    equipment = Equipment.query.get(equipment_id)
    url = equipment.esp_address

    if not url:
        return jsonify(
            {
                "status": "failed",
                "message": "This equipment has no ESP address associated with it",
            }
        )

    ir_command = IRCommand.query.filter_by(model=equipment.model).first()

    data_to_send = ir_command.raw_off if equipment.active else ir_command.raw_on
    data_to_send = data_to_send.strip()

    headers = {
        "Content-Type": "text/plain",
    }

    response = requests.post(url, data=data_to_send, headers=headers)
    if response.status_code == 200:
        return jsonify({"status": "success", "message": "POST request sent to ESP"})
    else:
        return jsonify({"status": "failed", "message": "POST request to ESP failed"})


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

        # The first user will be an admin
        if User.query.count() == 0:
            new_user.role = "admin"

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


@app.errorhandler(404)
def page_not_found(error):
    return render_template("404.html"), 404


if __name__ == "__main__":
    app.run(debug=True)
