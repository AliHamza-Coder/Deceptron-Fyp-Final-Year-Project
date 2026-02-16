// ========================================
// DECEPTRON - SIDEBAR COMPONENT
// Reusable Navigation Sidebar
// ========================================

/**
 * Navigation Items Configuration
 * Each item has: id (for active detection), label, icon, and link
 */
const NAV_ITEMS = {
    main: [
        { id: 'dashboard', label: 'Dashboard Hub', icon: 'fas fa-th-large', link: 'dashboard.html' },
        { id: 'live-session', label: 'Live Session', icon: 'fas fa-video', link: 'live-session.html' },
        { id: 'reports', label: 'Reports', icon: 'fas fa-file-alt', link: 'reports.html' },
        { id: 'uploads', label: 'Uploads', icon: 'fas fa-upload', link: 'uploads.html' }
    ],
    modules: [
        { id: 'facial-expression', label: 'Facial Micro-Exp', icon: 'fas fa-user-astronaut', link: 'facial-expression.html' },
        { id: 'voice-analysis', label: 'Voice Analysis', icon: 'fas fa-microphone-lines', link: 'voice-analysis.html' }
    ],
    footer: [
        { id: 'profile', label: 'Profile', icon: 'fas fa-user-circle', link: 'profile.html' },
        { id: 'settings', label: 'Settings', icon: 'fas fa-cog', link: 'settings.html' }
    ]
};

/**
 * Renders the complete sidebar HTML
 * @param {string} activePageId - The ID of the currently active page (e.g., 'dashboard', 'reports')
 * @returns {string} Complete sidebar HTML
 */
function renderSidebar(activePageId) {
    // Generate main navigation items
    const mainNavHTML = NAV_ITEMS.main.map(item => {
        const activeClass = item.id === activePageId ? 'active' : '';
        return `
            <div class="nav-item ${activeClass} cursor-pointer" onclick="window.location.href='${item.link}'">
                <i class="${item.icon}"></i>
                <span>${item.label}</span>
            </div>`;
    }).join('');

    // Generate module navigation items
    const moduleNavHTML = NAV_ITEMS.modules.map(item => {
        const activeClass = item.id === activePageId ? 'active' : '';
        return `
            <div class="nav-item ${activeClass} cursor-pointer" onclick="window.location.href='${item.link}'">
                <i class="${item.icon}"></i>
                <span>${item.label}</span>
            </div>`;
    }).join('');

    // Generate footer navigation items
    const footerNavHTML = NAV_ITEMS.footer.map(item => {
        const activeClass = item.id === activePageId ? 'active' : '';
        return `
            <div class="nav-item ${activeClass} cursor-pointer" onclick="window.location.href='${item.link}'">
                <i class="${item.icon}"></i>
                <span>${item.label}</span>
            </div>`;
    }).join('');

    // Return complete sidebar HTML (EXACT copy from dashboard.html)
    return `
    <button id="restore-sidebar" title="Show Sidebar" onclick="toggleSidebar()">
        <i class="fas fa-chevron-right"></i>
    </button>
    <aside class="sidebar flex flex-col">
        <button class="collapse-btn" onclick="toggleSidebar()" title="Hide Sidebar">
            <i class="fas fa-chevron-left"></i>
        </button>
        <div class="logo-section">
            <img src="../assets/images/Logo2.png" alt="Logo">
        </div>
        <nav class="flex-1">
            ${mainNavHTML}

            <div class="mt-8 px-6 mb-2 nav-category">
                <p class="text-[10px] font-bold tracking-widest text-gray-500 uppercase">Modules</p>
            </div>
            ${moduleNavHTML}
        </nav>

        <div class="p-4 border-t border-white/5">
            ${footerNavHTML}
            <div class="nav-item text-red-400 hover:text-red-300 hover:bg-red-500/5 cursor-pointer"
                onclick="closeApp()">
                <i class="fas fa-sign-out-alt"></i>
                <span>Logout</span>
            </div>

        </div>
    </aside>`;
}

/**
 * Auto-detects the current page and initializes the sidebar
 * Call this function on page load: initSidebar();
 */
function initSidebar() {
    // Get current page filename (e.g., "dashboard.html")
    const currentPage = window.location.pathname.split('/').pop();
    
    // Map filename to page ID
    const pageMap = {
        'dashboard.html': 'dashboard',
        'live-session.html': 'live-session',
        'reports.html': 'reports',
        'uploads.html': 'uploads',
        'facial-expression.html': 'facial-expression',
        'voice-analysis.html': 'voice-analysis',
        'profile.html': 'profile',
        'settings.html': 'settings',
        'report-detail.html': 'reports' // Report detail uses reports as active
    };
    
    const activePageId = pageMap[currentPage] || '';
    
    // Inject sidebar HTML into the page
    const sidebarHTML = renderSidebar(activePageId);
    document.body.insertAdjacentHTML('afterbegin', sidebarHTML);
}

/**
 * Handle user logout globally
 */
async function logout() {
    if(confirm("Are you sure you want to logout?")) {
        try {
            // Find logout button icon to add spinner
            const logoutBtn = document.querySelector('.fa-sign-out-alt');
            if(logoutBtn) {
                logoutBtn.className = 'fas fa-spinner fa-spin';
            }
            
            if (typeof eel !== 'undefined') {
                const result = await eel.logout()();
            }
            
            // Redirect regardless of backend result to ensure user isn't stuck
            window.location.href = 'login.html';
        } catch (error) {
            console.error("Logout failed:", error);
            window.location.href = 'login.html';
        }
    }
}

// Expose logout globally for sidebar button
window.closeApp = logout;

// Export for use in HTML pages
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { renderSidebar, initSidebar };
}
