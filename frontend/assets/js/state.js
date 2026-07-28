const Store = {
  state: {
    user: JSON.parse(localStorage.getItem('app_user')) || null,
    token: localStorage.getItem('app_token') || null,
    claims: [],
    activeClaim: null,
    chatHistory: [],
    theme: localStorage.getItem('app_theme') || 'light'
  },
  listeners: [],
  get(key) {
    return this.state[key];
  },
  set(key, value) {
    this.state[key] = value;
    if (key === 'user') {
      localStorage.setItem('app_user', JSON.stringify(value));
    }
    if (key === 'token') {
      if (value) localStorage.setItem('app_token', value);
      else localStorage.removeItem('app_token');
    }
    if (key === 'theme') {
      localStorage.setItem('app_theme', value);
    }
    this.notify(key, value);
  },
  subscribe(listener) {
    this.listeners.push(listener);
    return () => {
      this.listeners = this.listeners.filter(l => l !== listener);
    };
  },
  notify(key, value) {
    this.listeners.forEach(listener => listener(key, value, this.state));
  }
};
window.Store = Store;
