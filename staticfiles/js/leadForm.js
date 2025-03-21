// ✅ Ensure DOM is fully loaded before executing
document.addEventListener("DOMContentLoaded", function () {
    // ✅ Select form and input elements
    const leadForm = document.getElementById("leadForm");
    const emailInput = document.getElementById("email");
    const emailError = document.getElementById("email-error");

    // ✅ Check if form elements exist
    if (!leadForm) {
        console.error("❌ Form not found: leadForm is missing from the DOM.");
        return;
    }

    if (!emailInput || !emailError) {
        console.error("❌ Email input or error message container is missing.");
        return;
    }

    // ✅ Email validation on form submit
    leadForm.addEventListener("submit", function (event) {
        if (!emailInput.value.includes("@")) {
            event.preventDefault();
            emailError.textContent = "Invalid email address.";
            emailError.style.display = "block"; // ✅ Show error message
        }
    });

    // ✅ Auto-close menu after clicking a link (Navbar behavior fix)
    document.querySelectorAll(".nav-link").forEach(item => {
        item.addEventListener("click", () => {
            document.querySelector(".navbar-collapse").classList.remove("show");
        });
    });
});
