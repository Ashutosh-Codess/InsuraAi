document.addEventListener('DOMContentLoaded', () => {
  Nav.init();
});

const Nav = {
  init() {
    this.protectRoutes();
    this.renderHeader();
  },
  protectRoutes() {
    const path = window.location.pathname;
    const user = Auth.getUser();
    const isPublic = path.endsWith('index.html') || path === '/' || path.includes('/customer/') || path.includes('/agent/');
    if (!isPublic && !Auth.isAuthenticated()) {
      window.location.href = '/index.html';
      return;
    }
    if (path.includes('fraud-monitor.html') && user && !['agent', 'admin'].includes(user.role)) {
      window.location.href = '/pages/dashboard.html';
    }
  },
  renderHeader() {
    const user = Auth.getUser();
    const navUserEl = document.getElementById('nav-user-info');
    if (navUserEl && user) {
      navUserEl.innerHTML = `
        <div class="flex items-center gap-3">
          <div class="w-9 h-9 rounded-full bg-indigo-600 text-white font-bold flex items-center justify-center shadow-md">
            ${user.name ? user.name.charAt(0).toUpperCase() : 'U'}
          </div>
          <div class="hidden sm:block text-left">
            <div class="text-sm font-semibold text-slate-800 dark:text-slate-100">${user.name || 'User'}</div>
            <div class="text-xs text-slate-500 capitalize">${user.role || 'Member'}</div>
          </div>
          <button onclick="Auth.logout()" class="ml-2 text-xs font-semibold text-rose-600 hover:text-rose-700 bg-rose-50 hover:bg-rose-100 px-3 py-1.5 rounded-lg transition-colors">
            Logout
          </button>
        </div>
      `;
    }
  }
};
window.Nav = Nav;
