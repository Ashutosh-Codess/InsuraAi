const Auth = {
  async login(email, password, role = 'customer') {
    UI.showLoading();
    try {
      const response = await API.postForm('/auth/login', { username: email, password });
      Store.set('token', response.access_token);
      const user = await API.get('/auth/me');
      const isAuthorized = role === 'agent'
        ? ['agent', 'admin'].includes(user.role)
        : user.role === role;
      if (!isAuthorized) {
        Store.set('user', null);
        Store.set('token', null);
        throw new Error(`This account is not authorized for the ${role} portal`);
      }
      Store.set('user', user);
      UI.toast('Login successful', 'success');
      if (['agent', 'admin'].includes(user.role)) {
        window.location.href = '/pages/fraud-monitor.html';
      } else {
        window.location.href = '/pages/dashboard.html';
      }
    } catch (err) {
      // API.request already presents connection and response errors. Avoid
      // showing two notifications for a single failed sign-in attempt.
      if (!err.userMessage) {
        UI.toast('Login failed: ' + err.message, 'error');
      }
    } finally {
      UI.hideLoading();
    }
  },
  async register(data) {
    UI.showLoading();
    try {
      await API.post('/auth/register', data);
      await this.login(data.email, data.password, 'customer');
    } catch (err) {
      UI.toast('Registration failed: ' + err.message, 'error');
    } finally {
      UI.hideLoading();
    }
  },
  logout() {
    Store.set('user', null);
    Store.set('token', null);
    localStorage.clear();
    window.location.href = '/index.html';
  },
  isAuthenticated() {
    return !!Store.get('token');
  },
  getUser() {
    return Store.get('user');
  }
};
window.Auth = Auth;
