console.log("✅ scripts.js is running");

// ✅ Helper: Get CSRF token from meta
function getCSRFToken() {
    const tokenMeta = document.querySelector('meta[name="csrf-token"]');
    return tokenMeta ? tokenMeta.getAttribute("content") : "";
  }
  
  // ✅ On DOM ready
  document.addEventListener("DOMContentLoaded", function () {
    // ✅ Smooth scroll for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
      anchor.addEventListener("click", function (e) {
        e.preventDefault();
        const targetId = this.getAttribute("href").substring(1);
        const targetElement = document.getElementById(targetId);
        if (targetElement) {
          targetElement.scrollIntoView({ behavior: "smooth" });
        }
      });
    });
  
    // ✅ Collapse navbar on link click (mobile)
    const navbarToggler = document.querySelector(".navbar-toggler");
    const navbarCollapse = document.querySelector("#navbarNav");
  
    if (navbarToggler && navbarCollapse) {
      document.querySelectorAll("#navbarNav .nav-link").forEach(link => {
        link.addEventListener("click", function () {
          if (navbarCollapse.classList.contains("show")) {
            const bsCollapse = new bootstrap.Collapse(navbarCollapse, {
              toggle: true
            });
            bsCollapse.hide();
          }
        });
      });
    }
  });
  