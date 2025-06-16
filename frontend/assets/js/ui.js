// ===================================
// UI.JS - UI Utilities
// AI Agent Galaxy - Toast notifications, modals, animations
// ===================================

const UI = {
    // ===================================
    // INITIALIZATION
    // ===================================
    
    toasts: [],
    modals: new Map(),
    
    init() {
        this.createToastContainer();
        this.bindGlobalEvents();
    },

    // ===================================
    // TOAST NOTIFICATIONS
    // ===================================
    
    /**
     * Create toast container
     */
    createToastContainer() {
        if (document.getElementById('toastContainer')) return;
        
        const container = document.createElement('div');
        container.id = 'toastContainer';
        container.className = 'toast-container';
        container.innerHTML = `
            <style>
                .toast-container {
                    position: fixed;
                    top: 20px;
                    right: 20px;
                    z-index: 10000;
                    pointer-events: none;
                }
                
                .toast {
                    background: var(--surface-glass, rgba(255, 255, 255, 0.1));
                    backdrop-filter: blur(20px);
                    border: 1px solid var(--border-glass, rgba(255, 255, 255, 0.2));
                    border-radius: 12px;
                    padding: 16px 20px;
                    margin-bottom: 12px;
                    color: var(--text-primary, #ffffff);
                    font-weight: 600;
                    min-width: 300px;
                    max-width: 400px;
                    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
                    pointer-events: auto;
                    transform: translateX(100%);
                    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
                    display: flex;
                    align-items: center;
                    gap: 12px;
                    position: relative;
                    overflow: hidden;
                }
                
                .toast.show {
                    transform: translateX(0);
                }
                
                .toast.success {
                    border-left: 4px solid var(--success, #00ff7f);
                }
                
                .toast.error {
                    border-left: 4px solid var(--error, #ff6b6b);
                }
                
                .toast.warning {
                    border-left: 4px solid var(--warning, #ffd700);
                }
                
                .toast.info {
                    border-left: 4px solid var(--text-accent, #00f5ff);
                }
                
                .toast-icon {
                    font-size: 1.2rem;
                    flex-shrink: 0;
                }
                
                .toast-message {
                    flex: 1;
                    font-size: 0.95rem;
                    line-height: 1.4;
                }
                
                .toast-close {
                    background: none;
                    border: none;
                    color: inherit;
                    cursor: pointer;
                    padding: 4px;
                    border-radius: 4px;
                    opacity: 0.7;
                    transition: opacity 0.2s;
                    flex-shrink: 0;
                }
                
                .toast-close:hover {
                    opacity: 1;
                    background: rgba(255, 255, 255, 0.1);
                }
                
                .toast-progress {
                    position: absolute;
                    bottom: 0;
                    left: 0;
                    height: 3px;
                    background: var(--text-accent, #00f5ff);
                    transition: width linear;
                }
                
                @media (max-width: 480px) {
                    .toast-container {
                        top: 10px;
                        right: 10px;
                        left: 10px;
                    }
                    
                    .toast {
                        min-width: auto;
                        margin-bottom: 8px;
                    }
                }
            </style>
        `;
        
        document.body.appendChild(container);
    },

    /**
     * Show toast notification
     */
    showToast(message, type = 'info', duration = CONFIG.UI.TOAST_DURATION) {
        const toastId = Date.now() + Math.random();
        
        const icons = {
            success: '✅',
            error: '❌',
            warning: '⚠️',
            info: 'ℹ️'
        };
        
        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        toast.innerHTML = `
            <div class="toast-icon">${icons[type] || icons.info}</div>
            <div class="toast-message">${Utils.escapeHtml(message)}</div>
            <button class="toast-close" onclick="UI.hideToast(${toastId})">×</button>
            <div class="toast-progress"></div>
        `;
        
        const container = document.getElementById('toastContainer');
        container.appendChild(toast);
        
        // Store toast reference
        this.toasts.push({ id: toastId, element: toast });
        
        // Show with animation
        setTimeout(() => toast.classList.add('show'), 10);
        
        // Auto-hide with progress bar
        if (duration > 0) {
            const progressBar = toast.querySelector('.toast-progress');
            progressBar.style.width = '100%';
            progressBar.style.transitionDuration = `${duration}ms`;
            
            setTimeout(() => {
                progressBar.style.width = '0%';
            }, 50);
            
            setTimeout(() => {
                this.hideToast(toastId);
            }, duration);
        }
        
        return toastId;
    },

    /**
     * Hide specific toast
     */
    hideToast(toastId) {
        const toastIndex = this.toasts.findIndex(t => t.id === toastId);
        if (toastIndex === -1) return;
        
        const toast = this.toasts[toastIndex];
        toast.element.style.transform = 'translateX(100%)';
        toast.element.style.opacity = '0';
        
        setTimeout(() => {
            if (toast.element.parentNode) {
                toast.element.parentNode.removeChild(toast.element);
            }
            this.toasts.splice(toastIndex, 1);
        }, 300);
    },

    /**
     * Clear all toasts
     */
    clearToasts() {
        this.toasts.forEach(toast => {
            if (toast.element.parentNode) {
                toast.element.parentNode.removeChild(toast.element);
            }
        });
        this.toasts = [];
    },

    // ===================================
    // MODAL UTILITIES
    // ===================================
    
    /**
     * Show modal
     */
    showModal(modalId) {
        const modal = document.getElementById(modalId);
        if (!modal) {
            console.warn(`Modal with ID '${modalId}' not found`);
            return false;
        }
        
        modal.classList.add('active');
        document.body.style.overflow = 'hidden';
        
        // Store modal reference
        this.modals.set(modalId, modal);
        
        // Focus trap
        this.trapFocus(modal);
        
        return true;
    },

    /**
     * Hide modal
     */
    hideModal(modalId) {
        const modal = document.getElementById(modalId);
        if (!modal) return false;
        
        modal.classList.remove('active');
        document.body.style.overflow = '';
        
        // Remove from tracking
        this.modals.delete(modalId);
        
        return true;
    },

    /**
     * Toggle modal
     */
    toggleModal(modalId) {
        const modal = document.getElementById(modalId);
        if (!modal) return false;
        
        if (modal.classList.contains('active')) {
            return this.hideModal(modalId);
        } else {
            return this.showModal(modalId);
        }
    },

    /**
     * Create and show dynamic modal
     */
    createModal(content, options = {}) {
        const modalId = 'dynamicModal_' + Date.now();
        const config = {
            title: 'Modal',
            closable: true,
            backdrop: true,
            size: 'medium', // small, medium, large
            ...options
        };
        
        const modal = document.createElement('div');
        modal.id = modalId;
        modal.className = 'modal-overlay';
        modal.innerHTML = `
            <div class="modal-content modal-${config.size}">
                ${config.closable ? `<button class="modal-close" onclick="UI.hideModal('${modalId}')">&times;</button>` : ''}
                <div class="modal-header">
                    <h3>${Utils.escapeHtml(config.title)}</h3>
                </div>
                <div class="modal-body">
                    ${content}
                </div>
            </div>
        `;
        
        document.body.appendChild(modal);
        
        // Close on backdrop click
        if (config.backdrop) {
            modal.addEventListener('click', (e) => {
                if (e.target === modal) {
                    this.hideModal(modalId);
                }
            });
        }
        
        this.showModal(modalId);
        
        return modalId;
    },

    // ===================================
    // LOADING STATES
    // ===================================
    
    /**
     * Show loading spinner
     */
    showLoading(targetElement, message = 'Loading...') {
        if (!targetElement) return;
        
        const loadingHTML = `
            <div class="loading-spinner" data-loading="true">
                <div class="spinner">
                    <div class="spinner-ring"></div>
                    <div class="spinner-ring"></div>
                    <div class="spinner-ring"></div>
                    <div class="spinner-core"></div>
                </div>
                <p class="loading-text">${Utils.escapeHtml(message)}</p>
            </div>
        `;
        
        targetElement.innerHTML = loadingHTML;
    },

    /**
     * Hide loading spinner
     */
    hideLoading(targetElement) {
        if (!targetElement) return;
        
        const loadingElement = targetElement.querySelector('[data-loading="true"]');
        if (loadingElement) {
            loadingElement.remove();
        }
    },

    /**
     * Show overlay loading
     */
    showOverlayLoading(message = 'Loading...') {
        let overlay = document.getElementById('loadingOverlay');
        
        if (!overlay) {
            overlay = document.createElement('div');
            overlay.id = 'loadingOverlay';
            overlay.className = 'loading-overlay';
            overlay.innerHTML = `
                <div class="loading-spinner">
                    <div class="spinner">
                        <div class="spinner-ring"></div>
                        <div class="spinner-ring"></div>
                        <div class="spinner-ring"></div>
                        <div class="spinner-core"></div>
                    </div>
                    <p class="loading-text">${Utils.escapeHtml(message)}</p>
                </div>
                <style>
                    .loading-overlay {
                        position: fixed;
                        top: 0;
                        left: 0;
                        width: 100%;
                        height: 100%;
                        background: rgba(0, 0, 0, 0.8);
                        backdrop-filter: blur(10px);
                        display: flex;
                        align-items: center;
                        justify-content: center;
                        z-index: 9999;
                        opacity: 0;
                        visibility: hidden;
                        transition: all 0.3s ease;
                    }
                    
                    .loading-overlay.active {
                        opacity: 1;
                        visibility: visible;
                    }
                    
                    .loading-spinner {
                        text-align: center;
                        color: var(--text-primary, #ffffff);
                    }
                    
                    .spinner {
                        width: 80px;
                        height: 80px;
                        margin: 0 auto 20px;
                        position: relative;
                    }
                    
                    .spinner-ring {
                        position: absolute;
                        top: 0;
                        left: 0;
                        width: 100%;
                        height: 100%;
                        border-radius: 50%;
                        border: 3px solid transparent;
                        animation: spin 2s linear infinite;
                    }
                    
                    .spinner-ring:nth-child(1) {
                        border-top-color: var(--text-accent, #00f5ff);
                        animation-duration: 2s;
                    }
                    
                    .spinner-ring:nth-child(2) {
                        border-right-color: var(--success, #00ff7f);
                        animation-duration: 3s;
                        animation-direction: reverse;
                        width: 80%;
                        height: 80%;
                        top: 10%;
                        left: 10%;
                    }
                    
                    .spinner-ring:nth-child(3) {
                        border-bottom-color: #ff6b6b;
                        animation-duration: 2.5s;
                        width: 60%;
                        height: 60%;
                        top: 20%;
                        left: 20%;
                    }
                    
                    .spinner-core {
                        position: absolute;
                        top: 50%;
                        left: 50%;
                        width: 20px;
                        height: 20px;
                        background: var(--accent-gradient, linear-gradient(135deg, #4facfe 0%, #00f2fe 100%));
                        border-radius: 50%;
                        transform: translate(-50%, -50%);
                        animation: pulse 1.5s ease-in-out infinite;
                        box-shadow: 0 0 20px rgba(0, 245, 255, 0.5);
                    }
                    
                    @keyframes spin {
                        0% { transform: rotate(0deg); }
                        100% { transform: rotate(360deg); }
                    }
                    
                    @keyframes pulse {
                        0%, 100% { 
                            transform: translate(-50%, -50%) scale(1);
                            opacity: 1;
                        }
                        50% { 
                            transform: translate(-50%, -50%) scale(1.2);
                            opacity: 0.7;
                        }
                    }
                    
                    .loading-text {
                        font-size: 1.1rem;
                        font-weight: 500;
                        animation: fadeInOut 2s ease-in-out infinite;
                    }
                    
                    @keyframes fadeInOut {
                        0%, 100% { opacity: 0.7; }
                        50% { opacity: 1; }
                    }
                </style>
            `;
            
            document.body.appendChild(overlay);
        } else {
            overlay.querySelector('.loading-text').textContent = message;
        }
        
        setTimeout(() => overlay.classList.add('active'), 10);
    },

    /**
     * Hide overlay loading
     */
    hideOverlayLoading() {
        const overlay = document.getElementById('loadingOverlay');
        if (overlay) {
            overlay.classList.remove('active');
            setTimeout(() => {
                if (overlay.parentNode) {
                    overlay.parentNode.removeChild(overlay);
                }
            }, 300);
        }
    },

    // ===================================
    // ANIMATIONS
    // ===================================
    
    /**
     * Fade in element
     */
    fadeIn(element, duration = CONFIG.UI.ANIMATIONS.NORMAL) {
        if (!element) return;
        
        element.style.opacity = '0';
        element.style.display = 'block';
        element.style.transition = `opacity ${duration}ms ease`;
        
        setTimeout(() => {
            element.style.opacity = '1';
        }, 10);
    },

    /**
     * Fade out element
     */
    fadeOut(element, duration = CONFIG.UI.ANIMATIONS.NORMAL) {
        if (!element) return;
        
        element.style.transition = `opacity ${duration}ms ease`;
        element.style.opacity = '0';
        
        setTimeout(() => {
            element.style.display = 'none';
        }, duration);
    },

    /**
     * Slide up element
     */
    slideUp(element, duration = CONFIG.UI.ANIMATIONS.NORMAL) {
        if (!element) return;
        
        element.style.transition = `all ${duration}ms ease`;
        element.style.transform = 'translateY(-20px)';
        element.style.opacity = '0';
        
        setTimeout(() => {
            element.style.display = 'none';
        }, duration);
    },

    /**
     * Slide down element
     */
    slideDown(element, duration = CONFIG.UI.ANIMATIONS.NORMAL) {
        if (!element) return;
        
        element.style.display = 'block';
        element.style.transform = 'translateY(-20px)';
        element.style.opacity = '0';
        element.style.transition = `all ${duration}ms ease`;
        
        setTimeout(() => {
            element.style.transform = 'translateY(0)';
            element.style.opacity = '1';
        }, 10);
    },

    // ===================================
    // UTILITY FUNCTIONS
    // ===================================
    
    /**
     * Trap focus within modal
     */
    trapFocus(modal) {
        const focusableElements = modal.querySelectorAll(
            'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
        );
        
        const firstElement = focusableElements[0];
        const lastElement = focusableElements[focusableElements.length - 1];
        
        modal.addEventListener('keydown', (e) => {
            if (e.key === 'Tab') {
                if (e.shiftKey) {
                    if (document.activeElement === firstElement) {
                        lastElement.focus();
                        e.preventDefault();
                    }
                } else {
                    if (document.activeElement === lastElement) {
                        firstElement.focus();
                        e.preventDefault();
                    }
                }
            }
        });
        
        if (firstElement) {
            firstElement.focus();
        }
    },

    /**
     * Bind global UI events
     */
    bindGlobalEvents() {
        // Close modals on Escape key
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                // Close topmost modal
                const activeModals = Array.from(this.modals.values()).filter(modal => 
                    modal.classList.contains('active')
                );
                
                if (activeModals.length > 0) {
                    const topModal = activeModals[activeModals.length - 1];
                    this.hideModal(topModal.id);
                }
            }
        });
        
        // Handle click outside modals
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('modal-overlay')) {
                this.hideModal(e.target.id);
            }
        });
    }
};

// Make UI globally available
window.UI = UI;