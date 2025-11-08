/**
 * CI-NDA Global JavaScript Utilities
 * Shared functions across the application
 */

// Global state management
window.CI_NDA = {
  user: null,
  token: localStorage.getItem('token'),
  isAuthenticated: false,
  loading: false
};

// API Configuration
const API_BASE = window.location.origin;
const API_ENDPOINTS = {
  auth: {
    register: '/api/auth/register',
    login: '/api/auth/login',
    logout: '/api/auth/logout',
    profile: '/api/auth/profile'
  },
  users: '/api/users',
  courses: '/api/courses',
  opportunities: '/api/opportunities',
  portfolios: '/api/portfolios',
  mentorship: '/api/mentorship'
};

// Authentication utilities
class Auth {
  static getToken() {
    return localStorage.getItem('token');
  }

  static setToken(token) {
    localStorage.setItem('token', token);
    window.CI_NDA.token = token;
    window.CI_NDA.isAuthenticated = true;
  }

  static removeToken() {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    window.CI_NDA.token = null;
    window.CI_NDA.user = null;
    window.CI_NDA.isAuthenticated = false;
  }

  static isAuthenticated() {
    return !!this.getToken();
  }

  static redirectIfNotAuthenticated() {
    if (!this.isAuthenticated()) {
      window.location.href = '/signin.html';
      return false;
    }
    return true;
  }

  static redirectIfAuthenticated() {
    if (this.isAuthenticated()) {
      window.location.href = '/dashboard.html';
      return false;
    }
    return true;
  }

  static async logout() {
    try {
      await ApiClient.post('/api/auth/logout');
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      this.removeToken();
      window.location.href = '/signin.html';
    }
  }

  static async getCurrentUser() {
    if (!this.isAuthenticated()) return null;
    
    try {
      const response = await ApiClient.get('/api/auth/profile');
      if (response.success) {
        window.CI_NDA.user = response.user;
        localStorage.setItem('user', JSON.stringify(response.user));
        return response.user;
      }
    } catch (error) {
      console.error('Failed to get current user:', error);
      if (error.status === 401) {
        this.removeToken();
        window.location.href = '/signin.html';
      }
    }
    return null;
  }
}

// API Client
class ApiClient {
  static async request(endpoint, options = {}) {
    const url = `${API_BASE}${endpoint}`;
    const config = {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers
      },
      ...options
    };

    // Add authorization header if token exists
    const token = Auth.getToken();
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }

    try {
      const response = await fetch(url, config);
      const data = await response.json();
      
      if (!response.ok) {
        throw { status: response.status, message: data.message || 'Request failed', ...data };
      }
      
      return data;
    } catch (error) {
      console.error(`API Error (${endpoint}):`, error);
      throw error;
    }
  }

  static async get(endpoint, params = {}) {
    const url = new URL(`${API_BASE}${endpoint}`);
    Object.keys(params).forEach(key => url.searchParams.append(key, params[key]));
    return this.request(url.pathname + url.search);
  }

  static async post(endpoint, data = {}) {
    return this.request(endpoint, {
      method: 'POST',
      body: JSON.stringify(data)
    });
  }

  static async put(endpoint, data = {}) {
    return this.request(endpoint, {
      method: 'PUT',
      body: JSON.stringify(data)
    });
  }

  static async delete(endpoint) {
    return this.request(endpoint, {
      method: 'DELETE'
    });
  }

  static async upload(endpoint, formData) {
    const url = `${API_BASE}${endpoint}`;
    const config = {
      method: 'POST',
      body: formData
    };

    const token = Auth.getToken();
    if (token) {
      config.headers = {
        'Authorization': `Bearer ${token}`
      };
    }

    try {
      const response = await fetch(url, config);
      const data = await response.json();
      
      if (!response.ok) {
        throw { status: response.status, message: data.message || 'Upload failed', ...data };
      }
      
      return data;
    } catch (error) {
      console.error(`Upload Error (${endpoint}):`, error);
      throw error;
    }
  }
}

// Toast Notification System
class Toast {
  static container = null;

  static init() {
    if (!this.container) {
      this.container = document.createElement('div');
      this.container.id = 'toast-container';
      this.container.className = 'fixed top-4 right-4 z-50 space-y-2';
      document.body.appendChild(this.container);
    }
  }

  static show(message, type = 'info', duration = 5000) {
    this.init();

    const toast = document.createElement('div');
    const toastId = `toast-${Date.now()}`;
    toast.id = toastId;
    
    const typeClasses = {
      success: 'toast-success',
      error: 'toast-error',
      warning: 'toast-warning',
      info: 'toast-info'
    };

    const icons = {
      success: `<svg class="w-5 h-5 text-green-400" fill="currentColor" viewBox="0 0 20 20">
        <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"></path>
      </svg>`,
      error: `<svg class="w-5 h-5 text-red-400" fill="currentColor" viewBox="0 0 20 20">
        <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd"></path>
      </svg>`,
      warning: `<svg class="w-5 h-5 text-yellow-400" fill="currentColor" viewBox="0 0 20 20">
        <path fill-rule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clip-rule="evenodd"></path>
      </svg>`,
      info: `<svg class="w-5 h-5 text-blue-400" fill="currentColor" viewBox="0 0 20 20">
        <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clip-rule="evenodd"></path>
      </svg>`
    };

    toast.className = `toast ${typeClasses[type] || typeClasses.info} fade-in`;
    toast.innerHTML = `
      <div class="p-4">
        <div class="flex items-center">
          <div class="flex-shrink-0">
            ${icons[type] || icons.info}
          </div>
          <div class="ml-3 w-0 flex-1">
            <p class="text-sm font-medium text-white">${message}</p>
          </div>
          <div class="ml-4 flex-shrink-0 flex">
            <button onclick="Toast.hide('${toastId}')" class="bg-transparent rounded-md inline-flex text-gray-400 hover:text-white focus:outline-none">
              <svg class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                <path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd"></path>
              </svg>
            </button>
          </div>
        </div>
      </div>
    `;

    this.container.appendChild(toast);

    if (duration > 0) {
      setTimeout(() => this.hide(toastId), duration);
    }

    return toastId;
  }

  static hide(toastId) {
    const toast = document.getElementById(toastId);
    if (toast) {
      toast.style.transform = 'translateX(100%)';
      toast.style.opacity = '0';
      setTimeout(() => {
        if (toast.parentNode) {
          toast.parentNode.removeChild(toast);
        }
      }, 300);
    }
  }

  static success(message, duration = 5000) {
    return this.show(message, 'success', duration);
  }

  static error(message, duration = 7000) {
    return this.show(message, 'error', duration);
  }

  static warning(message, duration = 6000) {
    return this.show(message, 'warning', duration);
  }

  static info(message, duration = 5000) {
    return this.show(message, 'info', duration);
  }
}

// Loading utilities
class Loading {
  static show(element, text = 'Loading...') {
    if (typeof element === 'string') {
      element = document.querySelector(element);
    }
    
    if (element) {
      element.innerHTML = `
        <div class="flex items-center justify-center space-x-2">
          <div class="spinner w-4 h-4"></div>
          <span class="text-gray-400">${text}</span>
        </div>
      `;
      element.disabled = true;
    }
  }

  static hide(element, originalContent = '') {
    if (typeof element === 'string') {
      element = document.querySelector(element);
    }
    
    if (element) {
      element.innerHTML = originalContent;
      element.disabled = false;
    }
  }
}

// Form utilities
class FormUtils {
  static getFormData(form) {
    const formData = new FormData(form);
    const data = {};
    
    for (let [key, value] of formData.entries()) {
      // Handle multiple values for same key (checkboxes, multiple selects)
      if (data[key]) {
        if (Array.isArray(data[key])) {
          data[key].push(value);
        } else {
          data[key] = [data[key], value];
        }
      } else {
        data[key] = value;
      }
    }
    
    return data;
  }

  static validateRequired(form) {
    const requiredFields = form.querySelectorAll('[required]');
    let isValid = true;
    
    requiredFields.forEach(field => {
      if (!field.value.trim()) {
        this.showFieldError(field, 'This field is required');
        isValid = false;
      } else {
        this.clearFieldError(field);
      }
    });
    
    return isValid;
  }

  static validateEmail(email) {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
  }

  static showFieldError(field, message) {
    this.clearFieldError(field);
    
    field.classList.add('border-red-500');
    
    const errorDiv = document.createElement('div');
    errorDiv.className = 'form-error';
    errorDiv.textContent = message;
    errorDiv.setAttribute('data-error-for', field.name || field.id);
    
    field.parentNode.appendChild(errorDiv);
  }

  static clearFieldError(field) {
    field.classList.remove('border-red-500');
    
    const existingError = field.parentNode.querySelector(`[data-error-for="${field.name || field.id}"]`);
    if (existingError) {
      existingError.remove();
    }
  }

  static clearAllErrors(form) {
    const errorElements = form.querySelectorAll('.form-error');
    errorElements.forEach(error => error.remove());
    
    const fieldWithErrors = form.querySelectorAll('.border-red-500');
    fieldWithErrors.forEach(field => field.classList.remove('border-red-500'));
  }
}

// Modal utilities
class Modal {
  static open(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
      modal.classList.remove('hidden');
      document.body.style.overflow = 'hidden';
      
      // Focus first focusable element
      const firstFocusable = modal.querySelector('button, input, select, textarea, [tabindex]:not([tabindex="-1"])');
      if (firstFocusable) {
        firstFocusable.focus();
      }
    }
  }

  static close(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
      modal.classList.add('hidden');
      document.body.style.overflow = 'auto';
    }
  }

  static closeOnBackdrop(event, modalId) {
    if (event.target === event.currentTarget) {
      this.close(modalId);
    }
  }
}

// Sidebar utilities
class Sidebar {
  static toggle() {
    const sidebar = document.getElementById('sidebar');
    const mainContent = document.getElementById('main-content');
    const toggleBtn = document.getElementById('sidebar-toggle');
    
    if (sidebar && mainContent) {
      const isOpen = !sidebar.classList.contains('-translate-x-full');
      
      if (isOpen) {
        sidebar.classList.add('-translate-x-full');
        mainContent.classList.remove('ml-64');
        if (toggleBtn) toggleBtn.innerHTML = '→';
      } else {
        sidebar.classList.remove('-translate-x-full');
        mainContent.classList.add('ml-64');
        if (toggleBtn) toggleBtn.innerHTML = '←';
      }
    }
  }

  static close() {
    const sidebar = document.getElementById('sidebar');
    const mainContent = document.getElementById('main-content');
    const toggleBtn = document.getElementById('sidebar-toggle');
    
    if (sidebar && mainContent) {
      sidebar.classList.add('-translate-x-full');
      mainContent.classList.remove('ml-64');
      if (toggleBtn) toggleBtn.innerHTML = '→';
    }
  }
}

// Search utilities
class Search {
  static debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
      const later = () => {
        clearTimeout(timeout);
        func(...args);
      };
      clearTimeout(timeout);
      timeout = setTimeout(later, wait);
    };
  }

  static highlight(text, search) {
    if (!search) return text;
    
    const regex = new RegExp(`(${search})`, 'gi');
    return text.replace(regex, '<mark class="bg-yellow-200 text-yellow-900">$1</mark>');
  }
}

// Date utilities
class DateUtils {
  static formatDate(date, format = 'short') {
    const d = new Date(date);
    
    if (format === 'short') {
      return d.toLocaleDateString();
    } else if (format === 'long') {
      return d.toLocaleDateString(undefined, { 
        year: 'numeric', 
        month: 'long', 
        day: 'numeric' 
      });
    } else if (format === 'datetime') {
      return d.toLocaleString();
    } else if (format === 'relative') {
      return this.timeAgo(d);
    }
    
    return d.toString();
  }

  static timeAgo(date) {
    const now = new Date();
    const diffInSeconds = Math.floor((now - date) / 1000);
    
    const intervals = [
      { label: 'year', seconds: 31536000 },
      { label: 'month', seconds: 2592000 },
      { label: 'day', seconds: 86400 },
      { label: 'hour', seconds: 3600 },
      { label: 'minute', seconds: 60 },
      { label: 'second', seconds: 1 }
    ];
    
    for (let interval of intervals) {
      const count = Math.floor(diffInSeconds / interval.seconds);
      if (count >= 1) {
        return `${count} ${interval.label}${count !== 1 ? 's' : ''} ago`;
      }
    }
    
    return 'Just now';
  }
}

// File utilities
class FileUtils {
  static formatFileSize(bytes) {
    if (bytes === 0) return '0 B';
    
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  }

  static getFileExtension(filename) {
    return filename.slice((filename.lastIndexOf('.') - 1 >>> 0) + 2);
  }

  static isImageFile(filename) {
    const imageExtensions = ['jpg', 'jpeg', 'png', 'gif', 'webp', 'svg'];
    return imageExtensions.includes(this.getFileExtension(filename).toLowerCase());
  }

  static isVideoFile(filename) {
    const videoExtensions = ['mp4', 'avi', 'mov', 'wmv', 'flv', 'webm'];
    return videoExtensions.includes(this.getFileExtension(filename).toLowerCase());
  }
}

// Initialize auth state on load
document.addEventListener('DOMContentLoaded', () => {
  if (Auth.isAuthenticated()) {
    Auth.getCurrentUser();
  }
});

// Export for global use
window.Auth = Auth;
window.ApiClient = ApiClient;
window.Toast = Toast;
window.Loading = Loading;
window.FormUtils = FormUtils;
window.Modal = Modal;
window.Sidebar = Sidebar;
window.Search = Search;
window.DateUtils = DateUtils;
window.FileUtils = FileUtils;