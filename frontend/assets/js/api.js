const API = {
  baseURL: 'http://localhost:8000/api/v1',
  async request(endpoint, options = {}) {
    const controller = new AbortController();
    const { timeoutMs = 20000, ...fetchOptions } = options;
    const timeout = window.setTimeout(() => controller.abort(), timeoutMs);
    const token = Store.get('token');
    const headers = { ...options.headers };
    if (!headers['Content-Type'] && !(options.body instanceof FormData)) {
      headers['Content-Type'] = 'application/json';
    }
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }
    const config = {
      ...fetchOptions,
      headers
    };
    try {
      const response = await fetch(`${this.baseURL}${endpoint}`, { ...config, signal: controller.signal });
      // A failed sign-in is a normal error. Only clear an existing session
      // when an authenticated API request is rejected.
      if (response.status === 401 && token) {
        Auth.logout();
      }
      const contentType = response.headers.get('content-type') || '';
      const data = contentType.includes('application/json')
        ? await response.json()
        : await response.text();
      if (!response.ok) {
        throw new Error(data.detail || data.message || data || 'API Request Failed');
      }
      return data;
    } catch (error) {
      const message = error.name === 'AbortError'
        ? 'The server did not respond within 20 seconds. Check that the backend is running.'
        : error instanceof TypeError
          ? 'Cannot reach the backend. Start it with .\\start-backend.ps1, then try again.'
          : (error.message || 'Network Error');
      UI.toast(message, 'error');
      error.userMessage = message;
      throw error;
    } finally {
      window.clearTimeout(timeout);
    }
  },
  get(endpoint) {
    return this.request(endpoint, { method: 'GET' });
  },
  post(endpoint, body, options = {}) {
    return this.request(endpoint, {
      ...options,
      method: 'POST',
      body: JSON.stringify(body)
    });
  },
  postForm(endpoint, fields) {
    const body = new URLSearchParams(fields);
    return this.request(endpoint, {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body
    });
  },
  put(endpoint, body) {
    return this.request(endpoint, {
      method: 'PUT',
      body: JSON.stringify(body)
    });
  },
  delete(endpoint) {
    return this.request(endpoint, { method: 'DELETE' });
  },
  async upload(endpoint, formData) {
    const token = Store.get('token');
    const headers = {};
    if (token) headers['Authorization'] = `Bearer ${token}`;
    const response = await fetch(`${this.baseURL}${endpoint}`, {
      method: 'POST',
      headers,
      body: formData
    });
    if (!response.ok) throw new Error('File Upload Failed');
    return response.json();
  }
};
window.API = API;
