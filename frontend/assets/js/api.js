// ===================================
// API.JS - API Communication Layer
// AI Agent Galaxy - HTTP client and API utilities
// ===================================

const API = {
    // ===================================
    // CONFIGURATION
    // ===================================
    baseURL: CONFIG.API.BASE_URL,
    timeout: CONFIG.API.TIMEOUT,
    retryAttempts: CONFIG.API.RETRY_ATTEMPTS,
    
    // ===================================
    // CORE HTTP METHODS
    // ===================================
    
    /**
     * Make HTTP request with error handling and retries
     */
    async request(endpoint, options = {}) {
        const url = `${this.baseURL}${endpoint}`;
        const defaultOptions = {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
            },
            credentials: 'include', // Include cookies for session management
            ...options
        };

        let lastError;
        
        for (let attempt = 1; attempt <= this.retryAttempts; attempt++) {
            try {
                const controller = new AbortController();
                const timeoutId = setTimeout(() => controller.abort(), this.timeout);
                
                const response = await fetch(url, {
                    ...defaultOptions,
                    signal: controller.signal
                });
                
                clearTimeout(timeoutId);
                
                // Handle HTTP errors
                if (!response.ok) {
                    const errorData = await this.parseErrorResponse(response);
                    throw new APIError(errorData.error || `HTTP ${response.status}`, response.status, errorData);
                }
                
                // Parse response
                const data = await this.parseResponse(response);
                return data;
                
            } catch (error) {
                lastError = error;
                
                // Don't retry on authentication errors or client errors
                if (error instanceof APIError && error.status < 500) {
                    throw error;
                }
                
                // Don't retry on abort (timeout)
                if (error.name === 'AbortError') {
                    throw new APIError(CONFIG.ERRORS.TIMEOUT, 408);
                }
                
                // Log attempt and retry if not last attempt
                if (attempt < this.retryAttempts) {
                    Utils.logError(`API attempt ${attempt} failed, retrying...`, 'API');
                    await Utils.wait(1000 * attempt); // Exponential backoff
                } else {
                    Utils.logError(`API failed after ${this.retryAttempts} attempts`, 'API');
                }
            }
        }
        
        throw lastError || new APIError(CONFIG.ERRORS.NETWORK);
    },

    /**
     * Parse API response
     */
    async parseResponse(response) {
        const contentType = response.headers.get('content-type');
        
        if (contentType && contentType.includes('application/json')) {
            return await response.json();
        }
        
        return await response.text();
    },

    /**
     * Parse error response
     */
    async parseErrorResponse(response) {
        try {
            return await response.json();
        } catch {
            return { error: `HTTP ${response.status} ${response.statusText}` };
        }
    },

    /**
     * GET request
     */
    async get(endpoint, params = {}) {
        const queryString = new URLSearchParams(params).toString();
        const url = queryString ? `${endpoint}?${queryString}` : endpoint;
        return this.request(url);
    },

    /**
     * POST request
     */
    async post(endpoint, data = {}) {
        return this.request(endpoint, {
            method: 'POST',
            body: JSON.stringify(data)
        });
    },

    /**
     * PUT request
     */
    async put(endpoint, data = {}) {
        return this.request(endpoint, {
            method: 'PUT',
            body: JSON.stringify(data)
        });
    },

    /**
     * DELETE request
     */
    async delete(endpoint) {
        return this.request(endpoint, {
            method: 'DELETE'
        });
    },

    // ===================================
    // AUTHENTICATION ENDPOINTS
    // ===================================
    
    /**
     * User login
     */
    async login(username, password, rememberMe = false) {
        return this.post(CONFIG.API.ENDPOINTS.LOGIN, {
            username,
            password,
            remember_me: rememberMe
        });
    },

    /**
     * User registration
     */
    async register(username, email, password) {
        return this.post(CONFIG.API.ENDPOINTS.REGISTER, {
            username,
            email,
            password
        });
    },

    /**
     * User logout
     */
    async logout() {
        return this.post(CONFIG.API.ENDPOINTS.LOGOUT);
    },

    /**
     * Get current user info
     */
    async getCurrentUser() {
        return this.get(CONFIG.API.ENDPOINTS.ME);
    },

    /**
     * Request password reset
     */
    async forgotPassword(identifier) {
        return this.post(CONFIG.API.ENDPOINTS.FORGOT_PASSWORD, {
            identifier
        });
    },

    /**
     * Reset password with token
     */
    async resetPassword(token, password) {
        return this.post(CONFIG.API.ENDPOINTS.RESET_PASSWORD, {
            token,
            password
        });
    },

    /**
     * Validate reset token
     */
    async validateResetToken(token) {
        return this.post('/api/validate-reset-token', { token });
    },

    // ===================================
    // GAME ENDPOINTS
    // ===================================
    
    /**
     * Run AI agent validation
     */
    async runValidation(agentType, prediction) {
        return this.post(CONFIG.API.ENDPOINTS.RUN_VALIDATION, {
            agent_type: agentType,
            prediction: parseInt(prediction)
        });
    },

    // ===================================
    // ADMIN ENDPOINTS
    // ===================================
    
    /**
     * Get admin statistics
     */
    async getAdminStats() {
        return this.get(CONFIG.API.ENDPOINTS.ADMIN_STATS);
    },

    /**
     * Get users list (admin)
     */
    async getUsers(page = 1, perPage = 20, search = '') {
        return this.get(CONFIG.API.ENDPOINTS.ADMIN_USERS, {
            page,
            per_page: perPage,
            search
        });
    },

    /**
     * Update user (admin)
     */
    async updateUser(userId, userData) {
        return this.put(`${CONFIG.API.ENDPOINTS.ADMIN_USERS}/${userId}`, userData);
    },

    /**
     * Get games list (admin)
     */
    async getGames(page = 1, perPage = 20) {
        return this.get(CONFIG.API.ENDPOINTS.ADMIN_GAMES, {
            page,
            per_page: perPage
        });
    },

    /**
     * Cleanup old videos
     */
    async cleanupOldVideos() {
        return this.post(CONFIG.API.ENDPOINTS.CLEANUP_VIDEOS);
    },

    // ===================================
    // HEALTH CHECK
    // ===================================
    
    /**
     * Check API health
     */
    async healthCheck() {
        try {
            const response = await this.get('/api/health');
            return response.status === 'ok';
        } catch {
            return false;
        }
    }
};

// ===================================
// CUSTOM ERROR CLASS
// ===================================

class APIError extends Error {
    constructor(message, status = 500, data = {}) {
        super(message);
        this.name = 'APIError';
        this.status = status;
        this.data = data;
    }

    isAuthError() {
        return this.status === 401 || this.status === 403;
    }

    isNetworkError() {
        return this.status >= 500 || this.status === 0;
    }

    isClientError() {
        return this.status >= 400 && this.status < 500;
    }
}

// ===================================
// GLOBAL ERROR HANDLER
// ===================================

window.addEventListener('unhandledrejection', (event) => {
    if (event.reason instanceof APIError) {
        Utils.logError('Unhandled API error:', event.reason);
        // Prevent the default error handling
        event.preventDefault();
    }
});

// Make API globally available
window.API = API;
window.APIError = APIError;