// ✅ Simple email validation for native form submission (no fetch, no JSON)
document.addEventListener("DOMContentLoaded", function () {
    const leadForm = document.getElementById("leadForm");
    const emailInput = document.getElementById("email");
    const emailError = document.getElementById("email-error");

    if (!leadForm) {
        console.warn("⚠️ leadForm not found in DOM.");
        return;
    }

    // ✅ Basic client-side email check
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

    // ✅ Auto-close mobile nav menu after clicking a link
    document.querySelectorAll(".nav-link").forEach(item => {
        item.addEventListener("click", () => {
            const nav = document.querySelector(".navbar-collapse");
            if (nav && nav.classList.contains("show")) {
                nav.classList.remove("show");
            }
        });
    });
});
