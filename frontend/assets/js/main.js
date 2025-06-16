// ===================================
// MAIN.JS - Application Entry Point
// AI Agent Galaxy - Main application initialization
// ===================================

class AIAgentGalaxy {
    constructor() {
        this.isInitialized = false;
        this.modules = {};
        this.currentPage = this.detectCurrentPage();
    }

    // ===================================
    // APPLICATION INITIALIZATION
    // ===================================
    
    async init() {
        try {
            console.log('🌌 Initializing AI Agent Galaxy...');
            
            // Wait for DOM to be ready
            await this.waitForDOM();
            
            // Initialize core modules
            await this.initializeCore();
            
            // Initialize page-specific functionality
            await this.initializePage();
            
            // Setup global event listeners
            this.setupGlobalEvents();
            
            // Final setup
            this.finalizeInitialization();
            
            console.log('✅ AI Agent Galaxy initialized successfully');
            
        } catch (error) {
            console.error('❌ Failed to initialize AI Agent Galaxy:', error);
            this.handleInitializationError(error);
        }
    }

    /**
     * Wait for DOM to be ready
     */
    waitForDOM() {
        return new Promise((resolve) => {
            if (document.readyState === 'loading') {
                document.addEventListener('DOMContentLoaded', resolve);
            } else {
                resolve();
            }
        });
    }

    /**
     * Detect current page type
     */
    detectCurrentPage() {
        const path = window.location.pathname;
        
        if (path.includes('admin')) return 'admin';
        if (path.includes('reset-password')) return 'reset-password';
        return 'main';
    }

    /**
     * Initialize core application modules
     */
    async initializeCore() {
        console.log('🔧 Initializing core modules...');
        
        // Initialize UI system first
        if (window.UI) {
            UI.init();
            this.modules.ui = UI;
            console.log('✓ UI module initialized');
        }

        // Initialize authentication system
        if (window.Auth) {
            await Auth.init();
            this.modules.auth = Auth;
            console.log('✓ Auth module initialized');
        }

        // Initialize game system (only for main page)
        if (window.Game && this.currentPage === 'main') {
            Game.init();
            this.modules.game = Game;
            console.log('✓ Game module initialized');
        }

        // Check API health
        if (window.API) {
            const isHealthy = await API.healthCheck();
            if (!isHealthy) {
                console.warn('⚠️ API health check failed - some features may not work');
                UI.showToast('⚠️ Server connection issues detected', 'warning');
            } else {
                console.log('✓ API health check passed');
            }
        }
    }

    /**
     * Initialize page-specific functionality
     */
    async initializePage() {
        console.log(`🎯 Initializing ${this.currentPage} page...`);
        
        switch (this.currentPage) {
            case 'admin':
                await this.initializeAdminPage();
                break;
            case 'reset-password':
                await this.initializeResetPasswordPage();
                break;
            case 'main':
                await this.initializeMainPage();
                break;
        }
    }

    /**
     * Initialize main game page
     */
    async initializeMainPage() {
        console.log('🎮 Setting up main page...');
        
        // Initialize auth modal if present
        if (window.AuthModal) {
            // AuthModal should auto-initialize, but ensure it's ready
            console.log('✓ Auth modal available');
        }

        // Setup form handlers for non-modal auth
        this.setupMainPageEvents();
        
        // Load user preferences
        this.loadUserPreferences();
        
        // Setup keyboard shortcuts
        this.setupKeyboardShortcuts();
        
        console.log('✓ Main page initialized');
    }

    /**
     * Initialize admin page
     */
    async initializeAdminPage() {
        console.log('👑 Setting up admin page...');
        
        // Check admin access first
        if (!Auth.requireAdmin()) {
            console.log('❌ Admin access denied, redirecting...');
            window.location.href = '/';
            return;
        }

        // Initialize admin module
        if (window.Admin) {
            await Admin.init();
            this.modules.admin = Admin;
            console.log('✓ Admin module initialized');
        } else {
            console.error('❌ Admin module not found');
        }
    }

    /**
     * Initialize password reset page
     */
    async initializeResetPasswordPage() {
        console.log('🔐 Setting up password reset page...');
        
        // The reset password page should have its own initialization
        // Just ensure basic modules are available
        console.log('✓ Reset password page ready');
    }

    // ===================================
    // EVENT SETUP
    // ===================================
    
    /**
     * Setup global event listeners
     */
    setupGlobalEvents() {
        console.log('🎯 Setting up global events...');
        
        // Handle visibility changes (tab switching)
        document.addEventListener('visibilitychange', this.handleVisibilityChange.bind(this));
        
        // Handle online/offline status
        window.addEventListener('online', this.handleOnlineStatus.bind(this));
        window.addEventListener('offline', this.handleOfflineStatus.bind(this));
        
        // Handle unload
        window.addEventListener('beforeunload', this.handleBeforeUnload.bind(this));
        
        // Global error handling
        window.addEventListener('error', this.handleGlobalError.bind(this));
        window.addEventListener('unhandledrejection', this.handleUnhandledRejection.bind(this));
        
        // Handle auth state changes
        if (Auth) {
            Auth.onAuthChange((type, user) => {
                console.log(`🔐 Auth state changed: ${type}`, user?.username || 'N/A');
            });
        }
        
        console.log('✓ Global events configured');
    }

    /**
     * Setup main page specific events
     */
    setupMainPageEvents() {
        // Legacy auth form handlers (if not using modal)
        const loginForm = document.getElementById('loginForm');
        const registerForm = document.getElementById('registerForm');
        
        if (loginForm) {
            loginForm.addEventListener('submit', this.handleLogin.bind(this));
        }
        
        if (registerForm) {
            registerForm.addEventListener('submit', this.handleRegister.bind(this));
        }

        // Tab switching for legacy auth forms
        document.querySelectorAll('.auth-tab').forEach(tab => {
            tab.addEventListener('click', this.handleTabSwitch.bind(this));
        });
        
        console.log('✓ Main page events configured');
    }

    /**
     * Setup keyboard shortcuts
     */
    setupKeyboardShortcuts() {
        document.addEventListener('keydown', (event) => {
            // Ctrl/Cmd + K for future command palette
            if ((event.ctrlKey || event.metaKey) && event.key === 'k') {
                event.preventDefault();
                console.log('⌨️ Command palette shortcut (future feature)');
            }

            // Escape to close modals/overlays
            if (event.key === 'Escape') {
                // UI module should handle this, but we can add fallbacks here
                console.log('⌨️ Escape key pressed');
            }

            // Quick admin access (Ctrl+Shift+A)
            if (event.ctrlKey && event.shiftKey && event.key === 'A') {
                if (Auth.isAdmin()) {
                    window.location.href = '/admin';
                }
            }
        });
    }

    // ===================================
    // EVENT HANDLERS
    // ===================================
    
    handleVisibilityChange() {
        if (document.hidden) {
            console.log('📱 Page hidden - pausing activities');
        } else {
            console.log('📱 Page visible - resuming activities');
            
            // Refresh auth status when page becomes visible
            if (Auth.isAuthenticated) {
                Auth.checkAuthStatus();
            }
        }
    }

    handleOnlineStatus() {
        console.log('🌐 Back online');
        UI.showToast('🌐 Connection restored', 'success');
    }

    handleOfflineStatus() {
        console.log('📡 Gone offline');
        UI.showToast('📡 You are offline. Some features may not work.', 'warning');
    }

    handleBeforeUnload() {
        console.log('👋 Page unloading - saving data...');
        
        // Save any pending data
        if (Auth.isAuthenticated) {
            Auth.saveUserPreferences();
        }
        
        // Cleanup modules
        if (this.modules.admin && this.modules.admin.cleanup) {
            this.modules.admin.cleanup();
        }
    }

    handleGlobalError(event) {
        Utils.logError('Global error caught:', event.error);
        
        // Don't show toast for every error, just log them
        console.error('🚨 Global error:', event.error);
    }

    handleUnhandledRejection(event) {
        Utils.logError('Unhandled promise rejection:', event.reason);
        
        // Don't show toast for promise rejections, just log them
        console.error('🚨 Unhandled rejection:', event.reason);
    }

    // ===================================
    // LEGACY FORM HANDLERS
    // ===================================
    
    async handleLogin(event) {
        event.preventDefault();
        
        const form = event.target;
        const username = form.querySelector('#loginUsername')?.value;
        const password = form.querySelector('#loginPassword')?.value;
        
        if (!username || !password) {
            this.showError('Please fill in all fields');
            return;
        }
        
        const submitBtn = form.querySelector('button[type="submit"]');
        if (submitBtn) {
            submitBtn.disabled = true;
            submitBtn.textContent = 'Signing in...';
        }
        
        try {
            const result = await Auth.login(username, password);
            
            if (result.success) {
                this.showSuccess(CONFIG.SUCCESS.LOGIN);
            } else {
                this.showError(result.error);
            }
        } catch (error) {
            this.showError('Login failed. Please try again.');
        } finally {
            if (submitBtn) {
                submitBtn.disabled = false;
                submitBtn.textContent = 'Sign In';
            }
        }
    }

    async handleRegister(event) {
        event.preventDefault();
        
        const form = event.target;
        const username = form.querySelector('#registerUsername')?.value;
        const email = form.querySelector('#registerEmail')?.value;
        const password = form.querySelector('#registerPassword')?.value;
        
        if (!username || !email || !password) {
            this.showError('Please fill in all fields');
            return;
        }
        
        const submitBtn = form.querySelector('button[type="submit"]');
        if (submitBtn) {
            submitBtn.disabled = true;
            submitBtn.textContent = 'Creating account...';
        }
        
        try {
            const result = await Auth.register(username, email, password);
            
            if (result.success) {
                this.showSuccess(CONFIG.SUCCESS.REGISTER);
            } else {
                this.showError(result.error);
            }
        } catch (error) {
            this.showError('Registration failed. Please try again.');
        } finally {
            if (submitBtn) {
                submitBtn.disabled = false;
                submitBtn.textContent = 'Create Account';
            }
        }
    }

    handleTabSwitch(event) {
        const tab = event.currentTarget;
        const isLogin = tab.textContent.toLowerCase().includes('login') || 
                       tab.textContent.toLowerCase().includes('sign');
        
        // Update active tab
        document.querySelectorAll('.auth-tab').forEach(t => t.classList.remove('active'));
        tab.classList.add('active');
        
        // Update forms
        const loginForm = document.getElementById('loginForm');
        const registerForm = document.getElementById('registerForm');
        
        if (loginForm && registerForm) {
            if (isLogin) {
                loginForm.style.display = 'block';
                registerForm.style.display = 'none';
            } else {
                loginForm.style.display = 'none';
                registerForm.style.display = 'block';
            }
        }
        
        this.clearMessages();
    }

    // ===================================
    // UI HELPERS
    // ===================================
    
    showError(message) {
        const errorDiv = document.getElementById('errorMessage');
        if (errorDiv) {
            errorDiv.textContent = message;
            errorDiv.style.display = 'block';
        } else if (UI) {
            UI.showToast(message, 'error');
        } else {
            console.error('Error:', message);
        }
        
        this.hideSuccess();
    }

    showSuccess(message) {
        const successDiv = document.getElementById('successMessage');
        if (successDiv) {
            successDiv.textContent = message;
            successDiv.style.display = 'block';
        } else if (UI) {
            UI.showToast(message, 'success');
        } else {
            console.log('Success:', message);
        }
        
        this.hideError();
    }

    clearMessages() {
        this.hideError();
        this.hideSuccess();
    }

    hideError() {
        const errorDiv = document.getElementById('errorMessage');
        if (errorDiv) errorDiv.style.display = 'none';
    }

    hideSuccess() {
        const successDiv = document.getElementById('successMessage');
        if (successDiv) successDiv.style.display = 'none';
    }

    // ===================================
    // USER PREFERENCES
    // ===================================
    
    loadUserPreferences() {
        console.log('⚙️ Loading user preferences...');
        
        // Load theme preference
        const theme = Utils.getStorageItem(CONFIG.STORAGE_KEYS.THEME);
        if (theme && theme !== 'dark') {
            document.body.classList.toggle('light-theme', theme === 'light');
        }
        
        // Other preferences will be handled by individual modules
        console.log('✓ User preferences loaded');
    }

    // ===================================
    // ERROR HANDLING
    // ===================================
    
    handleInitializationError(error) {
        console.error('💥 Initialization failed:', error);
        
        // Show fallback UI
        const fallbackHTML = `
            <div style="
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                background: linear-gradient(135deg, #0c0c0c 0%, #1a1a2e 50%, #16213e 100%);
                color: white;
                font-family: 'Space Grotesk', sans-serif;
                text-align: center;
                padding: 2rem;
                z-index: 10000;
            ">
                <h1 style="font-size: 2rem; margin-bottom: 1rem; color: #ff6b6b;">
                    🚧 Initialization Error
                </h1>
                <p style="margin-bottom: 2rem; opacity: 0.8; max-width: 500px;">
                    Something went wrong while loading AI Agent Galaxy. 
                    Please check your internet connection and try again.
                </p>
                <button onclick="window.location.reload()" style="
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    border: none;
                    padding: 1rem 2rem;
                    border-radius: 0.5rem;
                    font-size: 1rem;
                    cursor: pointer;
                    transition: transform 0.2s;
                    font-family: inherit;
                    font-weight: 600;
                " onmouseover="this.style.transform='translateY(-2px)'"
                   onmouseout="this.style.transform='translateY(0)'">
                    🔄 Reload Page
                </button>
                <div style="margin-top: 2rem; font-size: 0.8rem; opacity: 0.6;">
                    Error: ${Utils.escapeHtml(error.message || 'Unknown error')}
                </div>
            </div>
        `;
        
        // Create fallback element
        const fallback = document.createElement('div');
        fallback.innerHTML = fallbackHTML;
        document.body.appendChild(fallback);
    }

    // ===================================
    // FINALIZATION
    // ===================================
    
    finalizeInitialization() {
        this.isInitialized = true;
        
        // Dispatch custom event
        const event = new CustomEvent('aiagalaxy:ready', {
            detail: { 
                app: this, 
                modules: this.modules,
                page: this.currentPage
            }
        });
        document.dispatchEvent(event);
        
        // Remove loading screen if present
        const loader = document.querySelector('.loading-screen, [data-loading-screen]');
        if (loader) {
            Utils.animateVisibility(loader, false, 300);
            setTimeout(() => loader.remove(), 300);
        }
        
        // Show main content
        const mainContent = document.querySelector('.main-content, .container');
        if (mainContent && mainContent.style.display === 'none') {
            Utils.animateVisibility(mainContent, true, 300);
        }
        
        console.log(`🎉 ${this.currentPage} page ready!`);
    }

    // ===================================
    // PUBLIC API
    // ===================================
    
    getModule(name) {
        return this.modules[name];
    }

    isReady() {
        return this.isInitialized;
    }

    getCurrentPage() {
        return this.currentPage;
    }

    restart() {
        console.log('🔄 Restarting application...');
        window.location.reload();
    }
}

// ===================================
// APPLICATION STARTUP
// ===================================

// Create global app instance
const app = new AIAgentGalaxy();

// Initialize when ready
app.init();

// Make app globally available
window.AIAgentGalaxy = app;

// ===================================
// LEGACY FUNCTION SUPPORT
// ===================================

// Global functions for backward compatibility with existing HTML
window.switchTab = function(tab) {
    if (window.AuthModal && AuthModal.switchTab) {
        AuthModal.switchTab(tab);
    } else {
        // Fallback for main page tabs
        app.handleTabSwitch({ currentTarget: { textContent: tab } });
    }
};

window.updateRiskDisplay = function() {
    if (app.modules.game && app.modules.game.updateRiskDisplay) {
        app.modules.game.updateRiskDisplay();
    }
};

window.logout = function() {
    if (Auth) {
        Auth.logout();
    }
};

window.resetGame = function() {
    if (app.modules.game && app.modules.game.resetGame) {
        app.modules.game.resetGame();
    }
};

window.toggleStepsLog = function() {
    if (app.modules.game && app.modules.game.toggleStepsLog) {
        app.modules.game.toggleStepsLog();
    }
};

// ===================================
// DEVELOPMENT HELPERS
// ===================================

if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
    // Development utilities
    window.dev = {
        app,
        modules: () => app.modules,
        config: CONFIG,
        utils: Utils,
        api: API,
        auth: Auth,
        ui: UI,
        // Quick actions
        quickLogin: (username = 'testuser', password = 'testpass') => 
            Auth.login(username, password),
        clearStorage: () => {
            localStorage.clear();
            sessionStorage.clear();
            console.log('🧹 Storage cleared');
        },
        state: () => ({
            page: app.currentPage,
            authenticated: Auth.isAuthenticated,
            user: Auth.currentUser,
            modules: Object.keys(app.modules),
            ready: app.isReady()
        }),
        restart: () => app.restart()
    };
    
    console.log('🛠️ Development mode - use window.dev for utilities');
    console.log('💡 Try: dev.state(), dev.quickLogin(), dev.clearStorage()');
}