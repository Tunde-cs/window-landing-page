function getCSRFToken() {
    const name = "csrftoken";
    const cookies = document.cookie.split(";");

    for (let cookie of cookies) {
        cookie = cookie.trim();
        if (cookie.startsWith(name + "=")) {
            return decodeURIComponent(cookie.substring(name.length + 1));
        }
    }

    return "";
}


console.log("✅ leadForm.js loaded");

// ✅ Ensure DOM is fully loaded before executing
document.addEventListener("DOMContentLoaded", function () {
    // ✅ Select lead form and input elements
    const leadForm = document.getElementById("leadForm");
    const emailInput = document.getElementById("email");
    const emailError = document.getElementById("email-error");

    if (!leadForm) {
        console.error("❌ Form not found: leadForm is missing from the DOM.");
    } else {
        if (!emailInput || !emailError) {
            console.error("❌ Email input or error message container is missing.");
        } else {
            // ✅ Email validation on form submit
            leadForm.addEventListener("submit", function (event) {
                if (!emailInput.value.includes("@")) {
                    event.preventDefault();
                    emailError.textContent = "Invalid email address.";
                    emailError.style.display = "block";
                }
            });
        }
    }

    // ✅ Auto-close menu after clicking a link
    document.querySelectorAll(".nav-link").forEach(item => {
        item.addEventListener("click", () => {
            document.querySelector(".navbar-collapse").classList.remove("show");
        });
    });

    // ✅ Quote Form Handling
    const quoteForm = document.querySelector('form[action="/request-quote/"]');
    if (quoteForm) {
        console.log("✅ Quote form found");

        quoteForm.addEventListener("submit", function (e) {
            e.preventDefault(); // Prevent normal form submission

            const csrfToken = getCSRFToken();

            const data = {
                name: document.querySelector('#name').value,
                email: document.querySelector('#email').value,
                phone: document.querySelector('#phone').value,
                service: document.querySelector('#service').value,
                windowType: document.querySelector('#windowType').value,
                details: document.querySelector('textarea[name="details"]').value
            };

            console.log("🔥 CSRF Token Being Sent:", csrfToken);
            
            fetch('/request-quote/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken
                },
                body: JSON.stringify(data)
            })
            .then(response => {
                const contentType = response.headers.get("content-type");
                if (contentType && contentType.includes("application/json")) {
                    return response.json();
                } else {
                    throw new Error("❌ Response is not JSON");
                }
            })
            .then(result => {
                console.log("✅ Quote response:", result);
                alert("✅ Quote submitted successfully!");
                quoteForm.reset();
            })
            .catch(error => {
                console.error("❌ Error submitting quote:", error);
                });
            
            }); // ✅ closes quoteForm.addEventListener
            
            } else {
                console.warn("⚠️ Quote form not found or not loaded yet.");
            }
            
            }); // ✅ closes DOMContentLoaded