// Theme toggle
(function () {
  function applyTheme(theme) {
    const html = document.getElementById('html-root') || document.documentElement;
    const sun = document.getElementById('icon-sun');
    const moon = document.getElementById('icon-moon');
    if (theme === 'light') {
      html.classList.add('light-mode');
      if (sun) sun.classList.add('hidden');
      if (moon) moon.classList.remove('hidden');
    } else {
      html.classList.remove('light-mode');
      if (sun) sun.classList.remove('hidden');
      if (moon) moon.classList.add('hidden');
    }
  }

  window.toggleTheme = function () {
    const current = localStorage.getItem('theme') || 'dark';
    const next = current === 'dark' ? 'light' : 'dark';
    localStorage.setItem('theme', next);
    applyTheme(next);
  };

  document.addEventListener('DOMContentLoaded', function () {
    applyTheme(localStorage.getItem('theme') || 'dark');
  });
})();

// Sidebar toggle
document.addEventListener('DOMContentLoaded', function () {
  const toggleBtn = document.getElementById('sidebar-toggle');
  const sidebar = document.getElementById('sidebar');

  if (toggleBtn && sidebar) {
    toggleBtn.addEventListener('click', function () {
      sidebar.classList.toggle('hidden');
      sidebar.classList.toggle('open');
    });
  }

  // Auto-hide flash messages after 5 seconds
  const messages = document.querySelectorAll('[class*="bg-green-9"], [class*="bg-red-9"], [class*="bg-blue-9"], [class*="bg-yellow-9"]');
  messages.forEach(function (msg) {
    if (msg.closest('.px-6.pt-4')) {
      setTimeout(function () {
        msg.style.transition = 'opacity 0.5s';
        msg.style.opacity = '0';
        setTimeout(function () { msg.remove(); }, 500);
      }, 5000);
    }
  });

  // Close dropdown menus when clicking outside
  document.addEventListener('click', function (e) {
    const dropdowns = document.querySelectorAll('.dropdown-menu');
    dropdowns.forEach(function (dd) {
      if (!dd.contains(e.target)) {
        dd.classList.add('hidden');
      }
    });
  });
});
