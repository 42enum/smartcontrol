document.addEventListener("DOMContentLoaded", () => {
  const buttons = document.querySelectorAll(".toggle-button");

  buttons.forEach((button) => {
    button.addEventListener("click", () => {
      const buttonId = button.dataset.id;

      const data = {
        method: "POST",
        body: JSON.stringify({ id: buttonId }),
        headers: {
          "Content-Type": "application/json",
        },
      };
      
      fetch("/request_to_esp", data)
        .then((res) => res.json().then((json) => console.log(json)))
        .catch((error) => console.error("Error:", error));
    });
  });
});
