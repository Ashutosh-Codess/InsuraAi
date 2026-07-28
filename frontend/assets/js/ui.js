const UI = {
  toast(message, type = 'info') {
    let container = document.getElementById('toast-container');
    if (!container) {
      container = document.createElement('div');
      container.id = 'toast-container';
      container.className = 'fixed bottom-5 right-5 z-50 flex flex-col gap-2';
      document.body.appendChild(container);
    }
    const toast = document.createElement('div');
    const colors = {
      success: 'bg-emerald-600 text-white',
      error: 'bg-rose-600 text-white',
      info: 'bg-indigo-600 text-white',
      warning: 'bg-amber-500 text-white'
    };
    toast.className = `px-4 py-3 rounded-xl shadow-lg text-sm font-medium transition-all transform translate-y-2 opacity-0 ${colors[type] || colors.info}`;
    toast.innerText = message;
    container.appendChild(toast);
    setTimeout(() => {
      toast.classList.remove('translate-y-2', 'opacity-0');
    }, 10);
    setTimeout(() => {
      toast.classList.add('opacity-0', 'translate-y-2');
      setTimeout(() => toast.remove(), 300);
    }, 3000);
  },
  showLoading() {
    let loader = document.getElementById('app-loader');
    if (!loader) {
      loader = document.createElement('div');
      loader.id = 'app-loader';
      loader.className = 'fixed inset-0 z-50 flex items-center justify-center bg-slate-900/40 backdrop-blur-sm';
      loader.innerHTML = `<div class="w-10 h-10 border-4 border-indigo-500 border-t-transparent rounded-full animate-spin"></div>`;
      document.body.appendChild(loader);
    }
    loader.classList.remove('hidden');
  },
  hideLoading() {
    const loader = document.getElementById('app-loader');
    if (loader) loader.classList.add('hidden');
  },
  openModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
      modal.classList.remove('hidden');
      modal.classList.add('flex');
    }
  },
  closeModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
      modal.classList.add('hidden');
      modal.classList.remove('flex');
    }
  }
};
window.UI = UI;
