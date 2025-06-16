// ===================================
// CONFIG.JS - Application Configuration
// AI Agent Galaxy - Central configuration
// ===================================

const CONFIG = {
    // API Configuration
    API: {
        BASE_URL: window.location.origin,
        ENDPOINTS: {
            LOGIN: '/api/login',
            REGISTER: '/api/register',
            LOGOUT: '/api/logout',
            ME: '/api/me',
            FORGOT_PASSWORD: '/api/forgot-password',
            RESET_PASSWORD: '/api/reset-password',
            RUN_VALIDATION: '/api/run-validation',
            ADMIN_STATS: '/api/admin/stats',
            ADMIN_USERS: '/api/admin/users',
            ADMIN_GAMES: '/api/admin/games',
            CLEANUP_VIDEOS: '/api/cleanup-old-videos'
        },
        TIMEOUT: 30000, // 30 seconds
        RETRY_ATTEMPTS: 3
    },

    // Game Configuration
    GAME: {
        AGENTS: {
            DDQN: 'ddqn',
            D3QN: 'd3qn'
        },
        PREDICTION_LIMITS: {
            MIN: 0,
            MAX: 120
        },
        RISK_ZONES: {
            IMPOSSIBLE: { min: 1, max: 29 },
            MINIMUM: { min: 30, max: 34 },
            SAFE: { min: 35, max: 55 },
            PROBABLE: { min: 56, max: 65 },
            STRUGGLE: { min: 66, max: 85 },
            FAILURE: { min: 86, max: 120 }
        },
        SCORING: {
            PERFECT: 10,
            CLOSE_RANGE: 8,    // ±5
            DECENT_RANGE: 5,   // ±10
            FAILURE_CORRECT: 3,
            MISS: 0
        },
        ACTION_NAMES: {
            0: 'Turn Left ↶',
            1: 'Turn Right ↷',
            2: 'Move Forward ↑',
            5: 'Open/Close Door 🚪'
        }
    },

    // UI Configuration
    UI: {
        ANIMATIONS: {
            FAST: 200,
            NORMAL: 300,
            SLOW: 500
        },
        PAGINATION: {
            DEFAULT_PER_PAGE: 20,
            MAX_PER_PAGE: 100
        },
        SEARCH_DEBOUNCE: 500,
        AUTO_REFRESH_INTERVAL: 30000, // 30 seconds
        TOAST_DURATION: 5000
    },

    // Validation Rules
    VALIDATION: {
        USERNAME: {
            MIN_LENGTH: 3,
            MAX_LENGTH: 30,
            PATTERN: /^[a-zA-Z0-9_-]+$/
        },
        PASSWORD: {
            MIN_LENGTH: 6,
            MAX_LENGTH: 128
        },
        EMAIL: {
            PATTERN: /^[^\s@]+@[^\s@]+\.[^\s@]+$/
        }
    },

    // Feature Flags
    FEATURES: {
        ADMIN_PANEL: true,
        PASSWORD_RESET: true,
        AUTO_REFRESH: true,
        EXPORT_DATA: true,
        BULK_ACTIONS: false // Future feature
    },

    // Storage Keys
    STORAGE_KEYS: {
        USER_PREFERENCES: 'aiag_user_prefs',
        THEME: 'aiag_theme',
        LAST_AGENT: 'aiag_last_agent'
    },

    // Error Messages
    ERRORS: {
        NETWORK: 'Network error. Please check your connection.',
        TIMEOUT: 'Request timed out. Please try again.',
        UNAUTHORIZED: 'Please log in to continue.',
        FORBIDDEN: 'You do not have permission to perform this action.',
        NOT_FOUND: 'The requested resource was not found.',
        SERVER_ERROR: 'Server error. Please try again later.',
        VALIDATION_FAILED: 'Please check your input and try again.'
    },

    // Success Messages
    SUCCESS: {
        LOGIN: 'Welcome back to the galaxy! 🚀',
        REGISTER: 'Welcome to the galaxy! 🌟',
        LOGOUT: 'Successfully logged out.',
        PASSWORD_RESET: 'Password reset email sent.',
        PROFILE_UPDATED: 'Profile updated successfully.',
        DATA_EXPORTED: 'Data exported successfully.'
    }
};

// Environment-specific overrides
if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
    CONFIG.API.BASE_URL = 'http://localhost:5000';
    CONFIG.UI.AUTO_REFRESH_INTERVAL = 10000; // Faster refresh in development
}

// Make config immutable
Object.freeze(CONFIG);

// Export for ES6 modules (if needed)
if (typeof module !== 'undefined' && module.exports) {
    module.exports = CONFIG;
}

// Make globally available
window.CONFIG = CONFIG;