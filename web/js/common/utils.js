// ========================================
// DECEPTRON - COMMON UTILITIES
// Shared helper functions used across pages
// ========================================

/**
 * Format bytes to human-readable file size
 * @param {number} bytes - File size in bytes
 * @returns {string} Formatted size (e.g., "2.5 MB")
 */
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round((bytes / Math.pow(k, i)) * 100) / 100 + ' ' + sizes[i];
}

/**
 * Format timestamp to readable date/time
 * @param {string|Date} date - Date to format
 * @returns {string} Formatted date
 */
function formatTimestamp(date) {
    if (!date) return 'N/A';
    const d = new Date(date);
    return d.toLocaleString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

/**
 * Show toast notification
 * @param {string} message - Message to display
 * @param {string} type - Type: 'success', 'error', 'info'
 */
function showToast(message, type = 'info') {
    const toast = document.getElementById('toast');
    if (!toast) return;
    
    const messageEl = toast.querySelector('div');
    if (messageEl) {
        messageEl.innerText = message;
    }
    
    // Show toast
    toast.classList.remove('opacity-0', 'translate-y-4');
    toast.classList.add('opacity-1', 'translate-y-0');
    
    // Hide after 3 seconds
    setTimeout(() => {
        toast.classList.add('opacity-0', 'translate-y-4');
        toast.classList.remove('opacity-1', 'translate-y-0');
    }, 3000);
}

/**
 * Update status UI elements
 * @param {string} status - Status type
 * @param {string} message - Status message
 */
function updateStatusUI(status, message) {
    const statusBadge = document.getElementById('status-badge');
    const statusText = document.getElementById('status-text');
    
    if (!statusBadge || !statusText) return;
    
    // Remove all status classes
    statusBadge.classList.remove('status-ready', 'status-live', 'status-recording', 'status-analyzing');
    
    // Add new status class
    statusBadge.classList.add(`status-${status}`);
    statusText.textContent = message;
}

/**
 * Toggle sidebar visibility
 */
function toggleSidebar() {
    const sidebar = document.querySelector('.sidebar');
    const restoreBtn = document.getElementById('restore-sidebar');
    
    if (!sidebar) return;
    
    if (sidebar.classList.contains('collapsed')) {
        sidebar.classList.remove('collapsed');
        if (restoreBtn) restoreBtn.classList.remove('visible');
    } else {
        sidebar.classList.add('collapsed');
        if (restoreBtn) restoreBtn.classList.add('visible');
    }
}

/**
 * Validate email format
 * @param {string} email - Email to validate
 * @returns {boolean} True if valid
 */
function isValidEmail(email) {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
}

/**
 * Debounce function calls
 * @param {Function} func - Function to debounce
 * @param {number} wait - Wait time in ms
 * @returns {Function} Debounced function
 */
function debounce(func, wait) {
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

/**
 * Generate unique ID
 * @returns {string} Unique ID
 */
function generateId() {
    return Date.now().toString(36) + Math.random().toString(36).substr(2);
}
