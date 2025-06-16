// ===================================
// UTILS.JS - Utility Functions
// AI Agent Galaxy - Common helper functions
// ===================================

const Utils = {
    // ===================================
    // DOM MANIPULATION
    // ===================================
    
    /**
     * Safely get element by ID
     */
    getElementById(id) {
        const element = document.getElementById(id);
        if (!element) {
            console.warn(`Element with ID '${id}' not found`);
        }
        return element;
    },

    /**
     * Safely query selector
     */
    querySelector(selector) {
        const element = document.querySelector(selector);
        if (!element) {
            console.warn(`Element with selector '${selector}' not found`);
        }
        return element;
    },

    /**
     * Add multiple event listeners
     */
    addEventListeners(element, events, handler) {
        if (!element) return;
        events.split(' ').forEach(event => {
            element.addEventListener(event, handler);
        });
    },

    /**
     * Show/hide element with animation
     */
    animateVisibility(element, show, duration = 300) {
        if (!element) return;
        
        if (show) {
            element.style.display = 'block';
            element.style.opacity = '0';
            element.style.transform = 'translateY(10px)';
            
            setTimeout(() => {
                element.style.transition = `all ${duration}ms ease`;
                element.style.opacity = '1';
                element.style.transform = 'translateY(0)';
            }, 10);
        } else {
            element.style.transition = `all ${duration}ms ease`;
            element.style.opacity = '0';
            element.style.transform = 'translateY(-10px)';
            
            setTimeout(() => {
                element.style.display = 'none';
            }, duration);
        }
    },

    // ===================================
    // VALIDATION
    // ===================================
    
    /**
     * Validate email format
     */
    isValidEmail(email) {
        return CONFIG.VALIDATION.EMAIL.PATTERN.test(email);
    },

    /**
     * Validate username
     */
    isValidUsername(username) {
        return username && 
               username.length >= CONFIG.VALIDATION.USERNAME.MIN_LENGTH &&
               username.length <= CONFIG.VALIDATION.USERNAME.MAX_LENGTH &&
               CONFIG.VALIDATION.USERNAME.PATTERN.test(username);
    },

    /**
     * Validate password strength
     */
    validatePassword(password) {
        const result = {
            isValid: false,
            strength: 'weak',
            issues: []
        };

        if (!password) {
            result.issues.push('Password is required');
            return result;
        }

        if (password.length < CONFIG.VALIDATION.PASSWORD.MIN_LENGTH) {
            result.issues.push(`Password must be at least ${CONFIG.VALIDATION.PASSWORD.MIN_LENGTH} characters`);
        }

        if (password.length > CONFIG.VALIDATION.PASSWORD.MAX_LENGTH) {
            result.issues.push(`Password must be less than ${CONFIG.VALIDATION.PASSWORD.MAX_LENGTH} characters`);
        }

        // Check password strength
        let score = 0;
        if (password.length >= 8) score++;
        if (/[a-z]/.test(password)) score++;
        if (/[A-Z]/.test(password)) score++;
        if (/\d/.test(password)) score++;
        if (/[^a-zA-Z0-9]/.test(password)) score++;

        if (score < 2) result.strength = 'weak';
        else if (score < 4) result.strength = 'fair';
        else if (score < 5) result.strength = 'good';
        else result.strength = 'strong';

        result.isValid = result.issues.length === 0 && score >= 2;
        return result;
    },

    /**
     * Validate prediction input
     */
    isValidPrediction(prediction) {
        const num = parseInt(prediction);
        return !isNaN(num) && 
               num >= CONFIG.GAME.PREDICTION_LIMITS.MIN && 
               num <= CONFIG.GAME.PREDICTION_LIMITS.MAX;
    },

    // ===================================
    // FORMATTING
    // ===================================
    
    /**
     * Escape HTML to prevent XSS
     */
    escapeHtml(text) {
        if (typeof text !== 'string') return text;
        const map = {
            '&': '&amp;',
            '<': '&lt;',
            '>': '&gt;',
            '"': '&quot;',
            "'": '&#039;'
        };
        return text.replace(/[&<>"']/g, m => map[m]);
    },

    /**
     * Format number with commas
     */
    formatNumber(num) {
        return num.toLocaleString();
    },

    /**
     * Format date relative to now
     */
    formatRelativeTime(date) {
        const now = new Date();
        const target = new Date(date);
        const diffMs = now - target;
        const diffMinutes = Math.floor(diffMs / (1000 * 60));
        const diffHours = Math.floor(diffMs / (1000 * 60 * 60));
        const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));

        if (diffMinutes < 1) return 'Just now';
        if (diffMinutes < 60) return `${diffMinutes}m ago`;
        if (diffHours < 24) return `${diffHours}h ago`;
        if (diffDays < 7) return `${diffDays}d ago`;
        
        return target.toLocaleDateString();
    },

    // ===================================
    // LOCAL STORAGE
    // ===================================
    
    /**
     * Safe localStorage getter
     */
    getStorageItem(key) {
        try {
            const item = localStorage.getItem(key);
            return item ? JSON.parse(item) : null;
        } catch (error) {
            console.warn('Failed to get storage item:', key, error);
            return null;
        }
    },

    /**
     * Safe localStorage setter
     */
    setStorageItem(key, value) {
        try {
            localStorage.setItem(key, JSON.stringify(value));
            return true;
        } catch (error) {
            console.warn('Failed to set storage item:', key, error);
            return false;
        }
    },

    /**
     * Remove storage item
     */
    removeStorageItem(key) {
        try {
            localStorage.removeItem(key);
            return true;
        } catch (error) {
            console.warn('Failed to remove storage item:', key, error);
            return false;
        }
    },

    // ===================================
    // DEBOUNCING & THROTTLING
    // ===================================
    
    /**
     * Debounce function calls
     */
    debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    },

    // ===================================
    // URL & QUERY PARAMS
    // ===================================
    
    /**
     * Get URL parameter
     */
    getUrlParameter(name) {
        const urlParams = new URLSearchParams(window.location.search);
        return urlParams.get(name);
    },

    // ===================================
    // GAME UTILITIES
    // ===================================
    
    /**
     * Calculate risk zone for prediction
     */
    getRiskZone(prediction) {
        const pred = parseInt(prediction);
        
        if (pred === 0) return 'failure';
        if (pred >= CONFIG.GAME.RISK_ZONES.IMPOSSIBLE.min && pred <= CONFIG.GAME.RISK_ZONES.IMPOSSIBLE.max) return 'impossible';
        if (pred >= CONFIG.GAME.RISK_ZONES.MINIMUM.min && pred <= CONFIG.GAME.RISK_ZONES.MINIMUM.max) return 'minimum';
        if (pred >= CONFIG.GAME.RISK_ZONES.SAFE.min && pred <= CONFIG.GAME.RISK_ZONES.SAFE.max) return 'safe';
        if (pred >= CONFIG.GAME.RISK_ZONES.PROBABLE.min && pred <= CONFIG.GAME.RISK_ZONES.PROBABLE.max) return 'probable';
        if (pred >= CONFIG.GAME.RISK_ZONES.STRUGGLE.min && pred <= CONFIG.GAME.RISK_ZONES.STRUGGLE.max) return 'struggle';
        if (pred >= CONFIG.GAME.RISK_ZONES.FAILURE.min && pred <= CONFIG.GAME.RISK_ZONES.FAILURE.max) return 'failure-zone';
        
        return 'unknown';
    },

    /**
     * Get risk message for prediction
     */
    getRiskMessage(prediction) {
        const zone = this.getRiskZone(prediction);
        const messages = {
            'failure': '💀 FAILURE PREDICTION (3 points if correct)',
            'impossible': '🚫 IMPOSSIBLE ZONE - Agent can\'t solve this fast (10% points)',
            'minimum': '⚡ MINIMUM POSSIBLE - Extremely optimistic (70% points)',
            'safe': '🎯 SAFE ZONE - Most predictable range (40% points)',
            'probable': '🟠 PROBABLE ZONE - Still likely (70% points)',
            'struggle': '🔥 STRUGGLE ZONE - Agent having difficulty (150% points!)',
            'failure-zone': '💀 FAILURE ZONE - Approaching timeout (200% points!)',
            'unknown': '❓ Unknown prediction range'
        };
        return messages[zone] || messages.unknown;
    },

    /**
     * Get action name from action ID
     */
    getActionName(actionId) {
        return CONFIG.GAME.ACTION_NAMES[actionId] || `Action ${actionId}`;
    },

    // ===================================
    // ERROR HANDLING
    // ===================================
    
    /**
     * Get user-friendly error message
     */
    getErrorMessage(error, defaultMessage = CONFIG.ERRORS.SERVER_ERROR) {
        if (typeof error === 'string') return error;
        if (error?.message) return error.message;
        if (error?.error) return error.error;
        return defaultMessage;
    },

    /**
     * Log error with context
     */
    logError(error, context = '') {
        console.error(`[AI Agent Galaxy] ${context}:`, error);
    },

    // ===================================
    // PERFORMANCE
    // ===================================
    
    /**
     * Wait for specified time
     */
    wait(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    },

    // ===================================
    // FEATURE DETECTION
    // ===================================
    
    /**
     * Check if device supports touch
     */
    isTouchDevice() {
        return 'ontouchstart' in window || navigator.maxTouchPoints > 0;
    },

    /**
     * Check if user prefers reduced motion
     */
    prefersReducedMotion() {
        return window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    },

    /**
     * Check if device is mobile
     */
    isMobileDevice() {
        return window.innerWidth <= 768 || this.isTouchDevice();
    }
};

// Make Utils globally available
window.Utils = Utils;