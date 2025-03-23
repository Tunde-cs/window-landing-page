// ✅ Only handles basic email validation and nav collapse
document.addEventListener("DOMContentLoaded", function () {
    const leadForm = document.getElementById("leadForm");
    const emailInput = document.getElementById("email");
    const emailError = document.getElementById("email-error");

    if (leadForm) {
        // ✅ Basic email format check
        leadForm.addEventListener("submit", function (event) {
            if (emailInput && !emailInput.value.includes("@")) {
                event.preventDefault();
                if (emailError) {
                    emailError.textContent = "Invalid email address.";
                    emailError.style.display = "block";
                } else {
                    alert("Please enter a valid email address.");
                }
            }
        });
    }

    // ✅ Auto-close the mobile menu on nav click
    document.querySelectorAll(".nav-link").forEach(link => {
        link.addEventListener("click", () => {
            const nav = document.querySelector(".navbar-collapse");
            if (nav && nav.classList.contains("show")) {
                nav.classList.remove("show");
            }
        });
    });
});
