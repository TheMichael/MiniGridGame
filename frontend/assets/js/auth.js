// ===================================
// AUTH.JS - Authentication System
// AI Agent Galaxy - User authentication and session management
// ===================================

const Auth = {
    // ===================================
    // STATE MANAGEMENT
    // ===================================
    currentUser: null,
    isAuthenticated: false,
    authCallbacks: [],
    
    // ===================================
    // INITIALIZATION
    // ===================================
    
    async init() {
        await this.checkAuthStatus();
        this.bindGlobalEvents();
        this.loadUserPreferences();
    },

    /**
     * Check current authentication status
     */
    async checkAuthStatus() {
        try {
            const response = await API.getCurrentUser();
            if (response.success && response.user) {
                this.setUser(response.user);
                return true;
            } else {
                this.clearUser();
                return false;
            }
        } catch (error) {
            Utils.logError('Auth status check failed:', error);
            this.clearUser();
            return false;
        }
    },

    /**
     * Set authenticated user
     */
    setUser(user) {
        this.currentUser = user;
        this.isAuthenticated = true;
        this.saveUserPreferences();
        this.notifyAuthChange('login', user);
        
        // Update UI
        this.updateAuthUI();
    },

    /**
     * Clear user session
     */
    clearUser() {
        this.currentUser = null;
        this.isAuthenticated = false;
        this.notifyAuthChange('logout', null);
        
        // Clear stored preferences
        Utils.removeStorageItem(CONFIG.STORAGE_KEYS.USER_PREFERENCES);
        
        // Update UI
        this.updateAuthUI();
    },

    // ===================================
    // AUTHENTICATION METHODS
    // ===================================
    
    /**
     * User login
     */
    async login(username, password, rememberMe = false) {
        try {
            const response = await API.login(username, password, rememberMe);
            
            if (response.success && response.user) {
                this.setUser(response.user);
                
                // Show success message
                if (response.message && window.UI) {
                    UI.showToast(response.message, 'success');
                }
                
                return { success: true, user: response.user };
            } else {
                return { success: false, error: response.error || 'Login failed' };
            }
        } catch (error) {
            Utils.logError('Login failed:', error);
            return { 
                success: false, 
                error: Utils.getErrorMessage(error, 'Login failed. Please try again.') 
            };
        }
    },

    /**
     * User registration
     */
    async register(username, email, password) {
        try {
            // Validate input
            const validation = this.validateRegistrationInput(username, email, password);
            if (!validation.isValid) {
                return { success: false, error: validation.errors.join(', ') };
            }

            const response = await API.register(username, email, password);
            
            if (response.success && response.user) {
                this.setUser(response.user);
                
                // Show success message
                if (response.message && window.UI) {
                    UI.showToast(response.message, 'success');
                }
                
                return { success: true, user: response.user };
            } else {
                return { success: false, error: response.error || 'Registration failed' };
            }
        } catch (error) {
            Utils.logError('Registration failed:', error);
            return { 
                success: false, 
                error: Utils.getErrorMessage(error, 'Registration failed. Please try again.') 
            };
        }
    },

    /**
     * User logout
     */
    async logout() {
        try {
            await API.logout();
        } catch (error) {
            Utils.logError('Logout request failed:', error);
            // Continue with local logout even if API call fails
        }
        
        this.clearUser();
        
        if (window.UI) {
            UI.showToast('Successfully logged out', 'success');
        }
        
        // Redirect to home page if on admin
        if (window.location.pathname.includes('admin')) {
            window.location.href = '/';
        }
    },

    /**
     * Request password reset
     */
    async forgotPassword(identifier) {
        try {
            const response = await API.forgotPassword(identifier);
            
            if (response.success) {
                return { 
                    success: true, 
                    message: response.message || 'Password reset email sent!' 
                };
            } else {
                return { 
                    success: false, 
                    error: response.error || 'Failed to send reset email' 
                };
            }
        } catch (error) {
            Utils.logError('Password reset failed:', error);
            return { 
                success: false, 
                error: Utils.getErrorMessage(error, 'Failed to send reset email') 
            };
        }
    },

    /**
     * Reset password with token
     */
    async resetPassword(token, password) {
        try {
            const validation = Utils.validatePassword(password);
            if (!validation.isValid) {
                return { 
                    success: false, 
                    error: validation.issues.join(', ') 
                };
            }

            const response = await API.resetPassword(token, password);
            
            if (response.success) {
                return { 
                    success: true, 
                    message: response.message || 'Password updated successfully!' 
                };
            } else {
                return { 
                    success: false, 
                    error: response.error || 'Failed to reset password' 
                };
            }
        } catch (error) {
            Utils.logError('Password reset failed:', error);
            return { 
                success: false, 
                error: Utils.getErrorMessage(error, 'Failed to reset password') 
            };
        }
    },

    // ===================================
    // VALIDATION
    // ===================================
    
    /**
     * Validate registration input
     */
    validateRegistrationInput(username, email, password) {
        const errors = [];
        
        if (!Utils.isValidUsername(username)) {
            errors.push('Invalid username format');
        }
        
        if (!Utils.isValidEmail(email)) {
            errors.push('Invalid email format');
        }
        
        const passwordValidation = Utils.validatePassword(password);
        if (!passwordValidation.isValid) {
            errors.push(...passwordValidation.issues);
        }
        
        return {
            isValid: errors.length === 0,
            errors
        };
    },

    // ===================================
    // UI INTEGRATION
    // ===================================
    
    /**
     * Update authentication UI
     */
    updateAuthUI() {
        const authSection = document.getElementById('authSection');
        const gameInterface = document.getElementById('gameInterface');
        const adminBtn = document.getElementById('adminBtn');
        
        if (this.isAuthenticated) {
            // Show game interface
            if (authSection) authSection.style.display = 'none';
            if (gameInterface) gameInterface.style.display = 'block';
            
            // Update user info
            this.updateUserInfo();
            
            // Show admin button if user is admin
            if (adminBtn && this.currentUser?.is_admin) {
                adminBtn.style.display = 'inline-flex';
            }
        } else {
            // Show auth section
            if (authSection) authSection.style.display = 'block';
            if (gameInterface) gameInterface.style.display = 'none';
            if (adminBtn) adminBtn.style.display = 'none';
        }
    },

    /**
     * Update user information in UI
     */
    updateUserInfo() {
        if (!this.currentUser) return;
        
        const elements = {
            username: document.getElementById('username'),
            totalScore: document.getElementById('totalScore'),
            gamesPlayed: document.getElementById('gamesPlayed'),
            successRate: document.getElementById('successRate')
        };
        
        if (elements.username) {
            elements.username.textContent = this.currentUser.username;
        }
        
        if (elements.totalScore) {
            elements.totalScore.textContent = Utils.formatNumber(this.currentUser.total_score || 0);
        }
        
        if (elements.gamesPlayed) {
            elements.gamesPlayed.textContent = this.currentUser.games_played || 0;
        }
        
        if (elements.successRate) {
            elements.successRate.textContent = (this.currentUser.prediction_accuracy || 0) + '%';
        }
    },

    /**
     * Require authentication
     */
    requireLogin() {
        if (!this.isAuthenticated) {
            if (window.AuthModal) {
                AuthModal.open('login');
            } else {
                // Fallback to redirect
                window.location.href = '/';
            }
            return false;
        }
        return true;
    },

    /**
     * Require admin privileges
     */
    requireAdmin() {
        if (!this.requireLogin()) return false;
        
        if (!this.currentUser?.is_admin) {
            if (window.UI) {
                UI.showToast('Admin privileges required', 'error');
            } else {
                alert('Admin privileges required');
            }
            return false;
        }
        
        return true;
    },

    // ===================================
    // EVENT SYSTEM
    // ===================================
    
    /**
     * Subscribe to auth changes
     */
    onAuthChange(callback) {
        this.authCallbacks.push(callback);
    },

    /**
     * Unsubscribe from auth changes
     */
    offAuthChange(callback) {
        const index = this.authCallbacks.indexOf(callback);
        if (index > -1) {
            this.authCallbacks.splice(index, 1);
        }
    },

    /**
     * Notify auth change subscribers
     */
    notifyAuthChange(type, user) {
        this.authCallbacks.forEach(callback => {
            try {
                callback(type, user);
            } catch (error) {
                Utils.logError('Auth callback error:', error);
            }
        });
    },

    /**
     * Bind global authentication events
     */
    bindGlobalEvents() {
        // Logout buttons
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('logout-btn') || 
                e.target.closest('.logout-btn')) {
                e.preventDefault();
                this.logout();
            }
        });

        // Handle session expiry
        window.addEventListener('storage', (e) => {
            if (e.key === 'session_expired') {
                this.clearUser();
                if (window.UI) {
                    UI.showToast('Session expired. Please log in again.', 'warning');
                }
            }
        });

        // Heartbeat to check session validity
        if (CONFIG.FEATURES.AUTO_REFRESH) {
            setInterval(() => {
                if (this.isAuthenticated) {
                    this.checkAuthStatus();
                }
            }, CONFIG.UI.AUTO_REFRESH_INTERVAL);
        }
    },

    // ===================================
    // USER PREFERENCES
    // ===================================
    
    /**
     * Load user preferences from storage
     */
    loadUserPreferences() {
        const prefs = Utils.getStorageItem(CONFIG.STORAGE_KEYS.USER_PREFERENCES);
        if (prefs && this.isAuthenticated) {
            // Apply saved preferences
            this.applyUserPreferences(prefs);
        }
    },

    /**
     * Save user preferences to storage
     */
    saveUserPreferences() {
        if (!this.isAuthenticated) return;
        
        const prefs = {
            userId: this.currentUser?.id,
            lastAgent: Utils.getStorageItem(CONFIG.STORAGE_KEYS.LAST_AGENT),
            theme: Utils.getStorageItem(CONFIG.STORAGE_KEYS.THEME) || 'dark'
        };
        
        Utils.setStorageItem(CONFIG.STORAGE_KEYS.USER_PREFERENCES, prefs);
    },

    /**
     * Apply user preferences
     */
    applyUserPreferences(prefs) {
        // Apply theme
        if (prefs.theme) {
            document.body.classList.toggle('light-theme', prefs.theme === 'light');
        }
        
        // Restore last selected agent
        if (prefs.lastAgent && document.querySelector(`[data-agent="${prefs.lastAgent}"]`)) {
            const agentBtn = document.querySelector(`[data-agent="${prefs.lastAgent}"]`);
            if (agentBtn) {
                agentBtn.click();
            }
        }
    },

    // ===================================
    // UTILITY METHODS
    // ===================================
    
    /**
     * Get current user
     */
    getUser() {
        return this.currentUser;
    },

    /**
     * Check if user is admin
     */
    isAdmin() {
        return this.isAuthenticated && this.currentUser?.is_admin === true;
    },

    /**
     * Get user display name
     */
    getDisplayName() {
        return this.currentUser?.username || 'Unknown User';
    },

    /**
     * Check permission
     */
    hasPermission(permission) {
        if (!this.isAuthenticated) return false;
        
        if (permission === 'admin') {
            return this.currentUser?.is_admin === true;
        }
        
        return true; // Basic user permissions
    }
};

// Make Auth globally available
window.Auth = Auth;