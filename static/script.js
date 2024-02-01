const route = "/simplified_request_to_esp"; // "/request_to_esp"

document.addEventListener("DOMContentLoaded", () => {
  const buttons = document.querySelectorAll(".toggle-button");
  const toastContainer = document.getElementById("toast-container");

  buttons.forEach((button) => {
    button.addEventListener("click", () => {
      const previousState = button.innerHTML;
      button.innerHTML = `<div class="spinner"></div>`;
      button.setAttribute("disabled", "true");

      const buttonId = button.dataset.id;

      const data = {
        method: "POST",
        body: JSON.stringify({ id: buttonId }),
        headers: {
          "Content-Type": "application/json",
        },
      };

      let message;

      fetch(route, data)
        .then((res) =>
          res.json().then((json) => {
            console.log(json);
            if (json.status === "failed") {
              button.innerHTML = previousState;

              message = json.mensagem;
              createToast(message);
            }

            if (json.status === "success") {
              button.innerHTML = previousState.trim() === "Ligar" ? "Desligar" : "Ligar";

              const statusElem = document.getElementById(`status-${buttonId}`);
              if (previousState.trim() === "Ligar") {
                statusElem.innerHTML = `
                <div
                class="flex items-center gap-2 rounded-full bg-green-200 px-2 py-1 text-sm text-green-800"
              >
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  width="24"
                  height="24"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="2"
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  class="h-4 w-4 text-green-500"
                >
                  <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path>
                  <polyline points="22 4 12 14.01 9 11.01"></polyline>
                </svg>
                <span>Ligado</span>
              </div>
                `;
              } else {
                statusElem.innerHTML = `
                <div
                          class="flex items-center gap-2 rounded-full bg-red-200 px-2 py-1 text-sm text-red-800"
                        >
                          <svg
                            xmlns="http://www.w3.org/2000/svg"
                            width="24"
                            height="24"
                            viewBox="0 0 24 24"
                            fill="none"
                            stroke="currentColor"
                            stroke-width="2"
                            stroke-linecap="round"
                            stroke-linejoin="round"
                            class="h-4 w-4 text-red-500"
                          >
                            <circle cx="12" cy="12" r="10"></circle>
                            <path d="m15 9-6 6"></path>
                            <path d="m9 9 6 6"></path>
                          </svg>
                          <span>Desligado</span>
                        </div>
                `;
              }
            }
          }),
        )
        .catch((error) => {
          console.error("Error:", error);
          button.innerHTML = previousState;
        })
        .finally(() => {
          button.removeAttribute("disabled");
        });

      function createToast(message) {
        const toast = document.createElement("div");
        toast.className = "bg-red-200 text-red-800 font-medium p-4 m-2 border rounded opacity-0 transition-opacity duration-300 ease-in-out";
        toast.innerText = message;

        toastContainer.appendChild(toast);

        setTimeout(() => {
          toast.classList.add("opacity-100");
        }, 10);

        setTimeout(() => {
          toast.classList.remove("opacity-100");
          setTimeout(() => {
            toastContainer.removeChild(toast);
          }, 300); // Wait for the transition to complete before removing the element
        }, 7000); // Adjust the timeout for how long you want the toast to be visible
      }
    });
  });
});
