// Utility to prevent reload loops and manage authentication state
class AuthGuard {
  constructor() {
    this.redirectInProgress = false;
    this.authCheckInProgress = false;
  }

  // Prevent multiple rapid redirects
  safeRedirect(url, delay = 100) {
    if (this.redirectInProgress) return;
    
    this.redirectInProgress = true;
    console.log(`Redirecting to ${url} in ${delay}ms`);
    
    setTimeout(() => {
      window.location.href = url;
    }, delay);
  }

  // Check authentication without causing loops
  checkAuth() {
    if (this.authCheckInProgress) return false;
    
    this.authCheckInProgress = true;
    
    try {
      const token = localStorage.getItem('authToken');
      const currentPath = window.location.pathname;
      const isOnAuthPage = currentPath.includes('authentication.html') || 
                          currentPath.includes('signin.html');
      
      if (!token && !isOnAuthPage) {
        this.safeRedirect('authentication.html');
        return false;
      }
      
      return !!token;
    } catch (error) {
      console.error('Auth check error:', error);
      return false;
    } finally {
      this.authCheckInProgress = false;
    }
  }

  // Initialize auth check for protected pages
  initProtectedPage() {
    // Only check once per page load
    if (window.authChecked) return;
    window.authChecked = true;
    
    return this.checkAuth();
  }

  // Clear auth and redirect safely
  logout() {
    localStorage.removeItem('authToken');
    localStorage.removeItem('user');
    sessionStorage.clear();
    
    this.safeRedirect('index.html');
  }
}

// Global auth guard instance
window.authGuard = new AuthGuard();

// Prevent back button reload loops
window.addEventListener('pageshow', function(event) {
  if (event.persisted) {
    // Page was loaded from cache, reset auth check flag
    window.authChecked = false;
  }
});

// Prevent multiple DOMContentLoaded handlers
if (!window.utilsLoaded) {
  window.utilsLoaded = true;
  console.log('Auth utilities loaded');
}