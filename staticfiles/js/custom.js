// ✅ Unified DOMContentLoaded logic
document.addEventListener("DOMContentLoaded", function () {
  // Add layout classes
  document.body.classList.add("sidebar-mini", "layout-fixed");

  // Init AdminLTE PushMenu if available
  const $pushButton = document.querySelector('[data-widget="pushmenu"]');
  
  if ($pushButton && typeof $ === "function" && typeof $.fn.PushMenu === "function") {
    $('[data-widget="pushmenu"]').PushMenu();

    // Manually toggle a custom sidebar-open class if needed
    $pushButton.addEventListener("click", () => {
      console.log("Sidebar toggled ✅");
    });
  } else {
    console.warn("Sidebar toggle or PushMenu not available ❌");
  }
});

document.addEventListener('DOMContentLoaded', function () {
  if (typeof $ !== 'undefined' && typeof $.fn.PushMenu !== 'undefined') {
    const $pushButton = document.querySelector('[data-widget="pushmenu"]');
    if ($pushButton) {
      $('[data-widget="pushmenu"]').PushMenu();
      console.log("✅ PushMenu activated");
    } else {
      console.warn("❌ PushMenu button not found.");
    }
  } else {
    console.warn("❌ AdminLTE PushMenu not initialized.");
  }
});
