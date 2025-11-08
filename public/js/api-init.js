// Global API Initialization
// This ensures a single API instance across all pages

(function() {
    // Prevent multiple initializations
    if (window.cindaAPIInitialized) {
        return;
    }

    // Initialize the global API instance
    if (typeof CindaAPI !== 'undefined') {
        window.api = new CindaAPI();
        window.cindaAPIInitialized = true;
        console.log('Global CI-NDA API initialized');
    } else {
        console.error('CindaAPI class not found. Make sure api.js is loaded first.');
    }
})();

// Utility function to get the API instance
function getAPI() {
    if (!window.api) {
        console.warn('API not initialized yet, creating new instance...');
        window.api = new CindaAPI();
    }
    return window.api;
}