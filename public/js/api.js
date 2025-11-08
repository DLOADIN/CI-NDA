const API_BASE_URL = 'http://localhost:5000/api';

class CindaAPI {
  constructor() {
    this.token = localStorage.getItem('authToken');
    this.baseURL = API_BASE_URL;
    this.isRedirectingAuth = false;
  }

  getHeaders() {
    const headers = { 'Content-Type': 'application/json' };
    if (this.token) {
      headers['Authorization'] = `Bearer ${this.token}`;
    }
    return headers;
  }

  async request(endpoint, options = {}) {
    try {
      const response = await fetch(`${this.baseURL}${endpoint}`, {
        ...options,
        headers: {
          ...this.getHeaders(),
          ...(options.headers || {})
        },
        credentials: 'include'
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ message: 'Request failed' }));
        throw new Error(errorData.message || `HTTP ${response.status}: ${response.statusText}`);
      }

      const data = await response.json();
      return data;
    } catch (error) {
      console.error('API Error:', error);
      
      // Handle authentication errors - prevent infinite redirects
      if (error.message.includes('Token is invalid') || error.message.includes('Token is missing')) {
        this.clearAuth();
        // Only redirect if not already on authentication page and not in the middle of authentication
        const currentPath = window.location.pathname;
        const isOnAuthPage = currentPath.includes('authentication.html') || currentPath.includes('signin.html');
        const isRedirecting = window.location.href.includes('redirecting');
        
        if (!isOnAuthPage && !isRedirecting && !this.isRedirectingAuth) {
          this.isRedirectingAuth = true;
          setTimeout(() => {
            window.location.href = 'authentication.html';
          }, 100);
        }
      }
      
      throw error;
    }
  }

  // Auth Methods
  async register(userData) {
    const data = await this.request('/auth/register', {
      method: 'POST',
      body: JSON.stringify(userData)
    });
    
    if (data.success) {
      this.saveAuth(data);
      return data;
    }
    throw new Error(data.message || 'Registration failed');
  }

  async login(credentials) {
    const data = await this.request('/auth/login', {
      method: 'POST',
      body: JSON.stringify(credentials)
    });
    
    if (data.success) {
      this.saveAuth(data);
      return data;
    }
    throw new Error(data.message || 'Login failed');
  }

  async socialLogin(provider, userData) {
    const data = await this.request('/auth/social-login', {
      method: 'POST',
      body: JSON.stringify({ ...userData, provider })
    });
    
    if (data.success) {
      this.saveAuth(data);
      return data;
    }
    throw new Error(data.message || 'Social login failed');
  }

  async logout() {
    try {
      await this.request('/auth/logout', { method: 'POST' });
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      this.clearAuth();
    }
  }

  saveAuth(data) {
    this.token = data.token;
    localStorage.setItem('authToken', data.token);
    localStorage.setItem('user', JSON.stringify(data.user));
    sessionStorage.setItem('userLoggedIn', 'true');
    sessionStorage.setItem('userType', data.user.userType);
    sessionStorage.setItem('userEmail', data.user.email);
    sessionStorage.setItem('userName', data.user.name);
  }

  clearAuth() {
    this.token = null;
    this.isRedirectingAuth = false; // Reset redirect flag
    localStorage.removeItem('authToken');
    localStorage.removeItem('user');
    sessionStorage.clear();
  }

  // Course Methods
  async getCourses(filters = {}) {
    const params = new URLSearchParams();
    Object.entries(filters).forEach(([key, value]) => {
      if (value !== undefined && value !== '') {
        params.append(key, value);
      }
    });
    
    const data = await this.request(`/courses?${params}`);
    return data.success ? data : { success: false, message: data.message };
  }

  async getCourse(id) {
    const data = await this.request(`/courses/${id}`);
    return data.success ? data : { success: false, message: data.message };
  }

  async enrollInCourse(courseId) {
    const data = await this.request(`/courses/${courseId}/enroll`, {
      method: 'POST'
    });
    return data.success ? data : { success: false, message: data.message };
  }

  // Opportunity Methods
  async getOpportunities(filters = {}) {
    const params = new URLSearchParams();
    Object.entries(filters).forEach(([key, value]) => {
      if (value !== undefined && value !== '') {
        params.append(key, value);
      }
    });
    
    const data = await this.request(`/opportunities?${params}`);
    return data.success ? data : { success: false, message: data.message };
  }

  async applyToOpportunity(opportunityId, coverLetter) {
    const data = await this.request(`/opportunities/${opportunityId}/apply`, {
      method: 'POST',
      body: JSON.stringify({ coverLetter })
    });
    return data.success ? data : { success: false, message: data.message };
  }

  // User Methods
  async getProfile() {
    const data = await this.request('/users/profile');
    return data.success ? data : { success: false, message: data.message };
  }

  async updateProfile(profileData) {
    const data = await this.request('/users/profile', {
      method: 'PUT',
      body: JSON.stringify(profileData)
    });
    return data.success ? data : { success: false, message: data.message };
  }

  // Portfolio Methods
  async getPortfolios(filters = {}) {
    const params = new URLSearchParams();
    Object.entries(filters).forEach(([key, value]) => {
      if (value !== undefined && value !== '') {
        params.append(key, value);
      }
    });
    
    const data = await this.request(`/portfolios?${params}`);
    return data.success ? data : { success: false, message: data.message };
  }

  async createPortfolio(portfolioData) {
    const data = await this.request('/portfolios', {
      method: 'POST',
      body: JSON.stringify(portfolioData)
    });
    return data.success ? data : { success: false, message: data.message };
  }

  // Mentorship Methods
  async getMentorships() {
    const data = await this.request('/mentorships');
    return data.success ? data : { success: false, message: data.message };
  }

  // File Upload Method
  async uploadFile(file) {
    const formData = new FormData();
    formData.append('file', file);
    
    try {
      const response = await fetch(`${this.baseURL}/upload`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${this.token}`
        },
        body: formData
      });
      
      const data = await response.json();
      
      if (!response.ok) {
        throw new Error(data.message || 'Upload failed');
      }
      
      return data.success ? data : { success: false, message: data.message };
    } catch (error) {
      console.error('Upload error:', error);
      throw error;
    }
  }

  // Search Method
  async search(query, category = 'all', page = 1) {
    const params = new URLSearchParams({
      q: query,
      category,
      page: page.toString()
    });
    
    const data = await this.request(`/search?${params}`);
    return data.success ? data : { success: false, message: data.message };
  }

  // Health Check
  async healthCheck() {
    try {
      const data = await this.request('/health');
      return data.success ? data : { success: false, message: data.message };
    } catch (error) {
      return { success: false, message: 'Server is not responding' };
    }
  }
}

// Global API instance
const api = new CindaAPI();

// Check authentication on page load
window.addEventListener('DOMContentLoaded', () => {
  const protectedPages = ['profile.html', 'signin.html'];
  const currentPage = window.location.pathname.split('/').pop();
  
  if (protectedPages.includes(currentPage)) {
    checkAuthentication();
  }
});

function checkAuthentication() {
  const token = localStorage.getItem('authToken');
  const currentPage = window.location.pathname.split('/').pop();
  
  if (!token && currentPage === 'profile.html') {
    alert('Please sign in to access your profile');
    window.location.href = 'authentication.html';
  }
}
