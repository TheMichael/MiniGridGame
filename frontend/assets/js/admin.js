// ===================================
// ADMIN.JS - Admin Panel Functionality
// AI Agent Galaxy - Admin dashboard and management
// ===================================

const Admin = {
    // ===================================
    // STATE MANAGEMENT
    // ===================================
    
    currentTab: 'overview',
    currentUsersPage: 1,
    currentGamesPage: 1,
    searchTimeout: null,
    autoRefreshInterval: null,
    
    // ===================================
    // INITIALIZATION
    // ===================================
    
    async init() {
        // Check admin access first
        if (!Auth.requireAdmin()) {
            window.location.href = '/';
            return;
        }
        
        this.bindEvents();
        this.setupAutoRefresh();
        await this.loadInitialData();
    },

    /**
     * Bind admin panel events
     */
    bindEvents() {
        // Tab switching
        document.querySelectorAll('.tab').forEach(tab => {
            tab.addEventListener('click', (e) => {
                const tabName = e.target.getAttribute('onclick')?.match(/'([^']+)'/)?.[1];
                if (tabName) {
                    this.switchTab(tabName);
                }
            });
        });

        // User search
        const userSearch = document.getElementById('userSearch');
        if (userSearch) {
            userSearch.addEventListener('input', (e) => {
                clearTimeout(this.searchTimeout);
                this.searchTimeout = setTimeout(() => {
                    this.loadUsersData(1, e.target.value);
                }, CONFIG.UI.SEARCH_DEBOUNCE);
            });
        }

        // Export buttons
        this.bindExportEvents();
        
        // Database operation buttons
        this.bindDatabaseEvents();
        
        // Edit user modal events
        this.bindEditUserEvents();
    },

    /**
     * Bind export-related events
     */
    bindExportEvents() {
        // Export users
        const exportUsersBtn = document.querySelector('[onclick="exportUsers()"]');
        if (exportUsersBtn) {
            exportUsersBtn.addEventListener('click', (e) => {
                e.preventDefault();
                this.exportUsers();
            });
        }

        // Export games
        const exportGamesBtn = document.querySelector('[onclick="exportGames()"]');
        if (exportGamesBtn) {
            exportGamesBtn.addEventListener('click', (e) => {
                e.preventDefault();
                this.exportGames();
            });
        }
    },

    /**
     * Bind database operation events
     */
    bindDatabaseEvents() {
        // Cleanup videos
        const cleanupBtn = document.querySelector('[onclick="cleanupOldVideos()"]');
        if (cleanupBtn) {
            cleanupBtn.addEventListener('click', (e) => {
                e.preventDefault();
                this.cleanupOldVideos();
            });
        }

        // Backup database (placeholder)
        const backupBtn = document.querySelector('[onclick*="backup"]');
        if (backupBtn) {
            backupBtn.addEventListener('click', (e) => {
                e.preventDefault();
                this.confirmDangerousAction('backup');
            });
        }
    },

    /**
     * Bind edit user modal events
     */
    bindEditUserEvents() {
        const editUserForm = document.getElementById('editUserForm');
        if (editUserForm) {
            editUserForm.addEventListener('submit', (e) => this.handleEditUser(e));
        }

        const closeModalBtns = document.querySelectorAll('[onclick="closeEditUserModal()"]');
        closeModalBtns.forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.preventDefault();
                this.closeEditUserModal();
            });
        });
    },

    /**
     * Setup auto-refresh for live data
     */
    setupAutoRefresh() {
        if (CONFIG.FEATURES.AUTO_REFRESH) {
            this.autoRefreshInterval = setInterval(() => {
                if (this.currentTab === 'overview') {
                    this.loadOverviewData();
                }
            }, CONFIG.UI.AUTO_REFRESH_INTERVAL);
        }
    },

    // ===================================
    // DATA LOADING
    // ===================================
    
    /**
     * Load initial data on page load
     */
    async loadInitialData() {
        await this.loadOverviewData();
    },

    /**
     * Switch between admin tabs
     */
    switchTab(tabName) {
        this.currentTab = tabName;
        
        // Update tab UI
        document.querySelectorAll('.tab').forEach(tab => tab.classList.remove('active'));
        document.querySelector(`[onclick="switchTab('${tabName}')"]`)?.classList.add('active');
        
        // Update content
        document.querySelectorAll('.tab-content').forEach(content => content.classList.remove('active'));
        document.getElementById(tabName)?.classList.add('active');
        
        // Load tab-specific data
        switch (tabName) {
            case 'overview':
                this.loadOverviewData();
                break;
            case 'users':
                this.loadUsersData();
                break;
            case 'games':
                this.loadGamesData();
                break;
        }
    },

    /**
     * Load overview statistics
     */
    async loadOverviewData() {
        try {
            UI.showLoading(document.querySelector('#overview .stats-grid'), 'Loading statistics...');
            
            const response = await API.getAdminStats();
            
            if (!response.success) {
                throw new Error(response.error || 'Failed to load stats');
            }
            
            this.updateOverviewStats(response);
            this.updateTopPlayersTable(response.top_players || []);
            
        } catch (error) {
            Utils.logError('Failed to load overview data:', error);
            UI.showToast('❌ Failed to load overview data', 'error');
        } finally {
            UI.hideLoading(document.querySelector('#overview .stats-grid'));
        }
    },

    /**
     * Update overview statistics
     */
    updateOverviewStats(data) {
        const stats = data.overview || {};
        const agentStats = data.agent_stats || {};
        
        const statElements = {
            totalUsers: document.getElementById('totalUsers'),
            activeUsers: document.getElementById('activeUsers'),
            totalGames: document.getElementById('totalGames'),
            totalScore: document.getElementById('totalScore'),
            recentGames: document.getElementById('recentGames'),
            recentUsers: document.getElementById('recentUsers'),
            ddqnGames: document.getElementById('ddqnGames'),
            d3qnGames: document.getElementById('d3qnGames')
        };
        
        if (statElements.totalUsers) statElements.totalUsers.textContent = stats.total_users || 0;
        if (statElements.activeUsers) statElements.activeUsers.textContent = stats.active_users || 0;
        if (statElements.totalGames) statElements.totalGames.textContent = stats.total_games || 0;
        if (statElements.totalScore) statElements.totalScore.textContent = Utils.formatNumber(stats.total_score || 0);
        if (statElements.recentGames) statElements.recentGames.textContent = stats.recent_games || 0;
        if (statElements.recentUsers) statElements.recentUsers.textContent = stats.recent_users || 0;
        if (statElements.ddqnGames) statElements.ddqnGames.textContent = agentStats.ddqn_games || 0;
        if (statElements.d3qnGames) statElements.d3qnGames.textContent = agentStats.d3qn_games || 0;
    },

    /**
     * Update top players table
     */
    updateTopPlayersTable(topPlayers) {
        const table = document.getElementById('topPlayersTable');
        if (!table) return;
        
        if (topPlayers.length === 0) {
            table.innerHTML = '<tr><td colspan="6" style="text-align: center; color: var(--text-secondary);">No players yet</td></tr>';
            return;
        }
        
        table.innerHTML = topPlayers.map((player, index) => `
            <tr>
                <td><span class="status-badge status-${index < 3 ? 'success' : 'active'}">#${index + 1}</span></td>
                <td><strong>${Utils.escapeHtml(player.username)}</strong></td>
                <td><strong>${Utils.formatNumber(player.total_score)}</strong></td>
                <td>${player.games_played}</td>
                <td>${player.prediction_accuracy}%</td>
                <td>${new Date(player.created_at).toLocaleDateString()}</td>
            </tr>
        `).join('');
    },

    /**
     * Load users data with pagination
     */
    async loadUsersData(page = 1, search = '') {
        try {
            const usersTable = document.getElementById('usersTable');
            if (usersTable) {
                UI.showLoading(usersTable.parentNode, 'Loading users...');
            }
            
            const response = await API.getUsers(page, CONFIG.UI.PAGINATION.DEFAULT_PER_PAGE, search);
            
            if (!response.success) {
                throw new Error(response.error || 'Failed to load users');
            }
            
            this.updateUsersTable(response.users || []);
            this.updatePagination('usersPagination', response.pagination, 'loadUsersData');
            this.currentUsersPage = page;
            
        } catch (error) {
            Utils.logError('Failed to load users data:', error);
            UI.showToast('❌ Failed to load users data', 'error');
            
            const usersTable = document.getElementById('usersTable');
            if (usersTable) {
                usersTable.innerHTML = '<tr><td colspan="9" style="text-align: center; color: var(--error);">Failed to load users</td></tr>';
            }
        }
    },

    /**
     * Update users table
     */
    updateUsersTable(users) {
        const table = document.getElementById('usersTable');
        if (!table) return;
        
        if (users.length === 0) {
            table.innerHTML = '<tr><td colspan="9" style="text-align: center; color: var(--text-secondary);">No users found</td></tr>';
            return;
        }
        
        table.innerHTML = users.map(user => `
            <tr>
                <td>${user.id}</td>
                <td><strong>${Utils.escapeHtml(user.username)}</strong></td>
                <td>${Utils.escapeHtml(user.email)}</td>
                <td>${Utils.formatNumber(user.total_score || 0)}</td>
                <td>${user.games_played || 0}</td>
                <td>${user.prediction_accuracy || 0}%</td>
                <td>
                    <span class="status-badge status-${user.is_active ? 'active' : 'inactive'}">
                        ${user.is_active ? 'Active' : 'Inactive'}
                    </span>
                    ${user.is_admin ? '<span class="status-badge status-admin">Admin</span>' : ''}
                </td>
                <td>${new Date(user.created_at).toLocaleDateString()}</td>
                <td>
                    <div class="action-buttons">
                        <button class="btn btn-small" onclick="Admin.editUser(${user.id}, '${Utils.escapeHtml(user.username)}', '${Utils.escapeHtml(user.email)}', ${user.is_active}, ${user.is_admin})">✏️ Edit</button>
                    </div>
                </td>
            </tr>
        `).join('');
    },

    /**
     * Load games data with pagination
     */
    async loadGamesData(page = 1) {
        try {
            const gamesTable = document.getElementById('gamesTable');
            if (gamesTable) {
                UI.showLoading(gamesTable.parentNode, 'Loading games...');
            }
            
            const response = await API.getGames(page, CONFIG.UI.PAGINATION.DEFAULT_PER_PAGE);
            
            if (!response.success) {
                throw new Error(response.error || 'Failed to load games');
            }
            
            this.updateGamesTable(response.games || []);
            this.updatePagination('gamesPagination', response.pagination, 'loadGamesData');
            this.currentGamesPage = page;
            
        } catch (error) {
            Utils.logError('Failed to load games data:', error);
            UI.showToast('❌ Failed to load games data', 'error');
            
            const gamesTable = document.getElementById('gamesTable');
            if (gamesTable) {
                gamesTable.innerHTML = '<tr><td colspan="10" style="text-align: center; color: var(--error);">Failed to load games</td></tr>';
            }
        }
    },

    /**
     * Update games table
     */
    updateGamesTable(games) {
        const table = document.getElementById('gamesTable');
        if (!table) return;
        
        if (games.length === 0) {
            table.innerHTML = '<tr><td colspan="10" style="text-align: center; color: var(--text-secondary);">No games found</td></tr>';
            return;
        }
        
        table.innerHTML = games.map(game => `
            <tr>
                <td>${game.id}</td>
                <td><strong>${Utils.escapeHtml(game.username)}</strong></td>
                <td><span class="status-badge status-active">${(game.agent_type || '').toUpperCase()}</span></td>
                <td>${game.prediction === 0 ? 'Fail' : game.prediction}</td>
                <td>${game.actual_steps}</td>
                <td>
                    <span class="status-badge status-${game.succeeded ? 'success' : 'failed'}">
                        ${game.succeeded ? 'Success' : 'Failed'}
                    </span>
                </td>
                <td><strong>${game.score}</strong></td>
                <td>${(game.total_reward || 0).toFixed(1)}</td>
                <td>${new Date(game.timestamp).toLocaleString()}</td>
                <td>
                    ${game.gif_url ? `<a href="${game.gif_url}" target="_blank" class="btn btn-small">🎬 View</a>` : '-'}
                </td>
            </tr>
        `).join('');
    },

    // ===================================
    // PAGINATION
    // ===================================
    
    /**
     * Update pagination controls
     */
    updatePagination(containerId, pagination, functionName) {
        const container = document.getElementById(containerId);
        if (!container || !pagination) return;
        
        let paginationHTML = `
            <div class="pagination-info">
                Showing ${((pagination.page - 1) * pagination.per_page) + 1}-${Math.min(pagination.page * pagination.per_page, pagination.total)} of ${pagination.total}
            </div>
        `;
        
        if (pagination.pages > 1) {
            paginationHTML += '<div style="display: flex; gap: 8px;">';
            
            if (pagination.has_prev) {
                paginationHTML += `<button class="btn btn-small" onclick="Admin.loadPage('${functionName}', ${pagination.page - 1})">← Prev</button>`;
            }
            
            const startPage = Math.max(1, pagination.page - 2);
            const endPage = Math.min(pagination.pages, pagination.page + 2);
            
            for (let i = startPage; i <= endPage; i++) {
                const activeClass = i === pagination.page ? 'btn-success' : '';
                paginationHTML += `<button class="btn btn-small ${activeClass}" onclick="Admin.loadPage('${functionName}', ${i})">${i}</button>`;
            }
            
            if (pagination.has_next) {
                paginationHTML += `<button class="btn btn-small" onclick="Admin.loadPage('${functionName}', ${pagination.page + 1})">Next →</button>`;
            }
            
            paginationHTML += '</div>';
        }
        
        container.innerHTML = paginationHTML;
    },

    /**
     * Load specific page
     */
    loadPage(functionName, page) {
        if (functionName === 'loadUsersData') {
            const searchValue = document.getElementById('userSearch')?.value || '';
            this.loadUsersData(page, searchValue);
        } else if (functionName === 'loadGamesData') {
            this.loadGamesData(page);
        }
    },

    // ===================================
    // USER MANAGEMENT
    // ===================================
    
    /**
     * Edit user - show modal
     */
    editUser(userId, username, email, isActive, isAdmin) {
        const modal = document.getElementById('editUserModal');
        if (!modal) return;
        
        document.getElementById('editUserId').value = userId;
        document.getElementById('editUsername').value = username;
        document.getElementById('editEmail').value = email;
        document.getElementById('editIsActive').checked = isActive;
        document.getElementById('editIsAdmin').checked = isAdmin;
        
        UI.showModal('editUserModal');
    },

    /**
     * Close edit user modal
     */
    closeEditUserModal() {
        UI.hideModal('editUserModal');
        
        const errorDiv = document.getElementById('editUserError');
        if (errorDiv) errorDiv.style.display = 'none';
        
        const form = document.getElementById('editUserForm');
        if (form) form.reset();
    },

    /**
     * Handle edit user form submission
     */
    async handleEditUser(e) {
        e.preventDefault();
        
        const userId = document.getElementById('editUserId').value;
        const isActive = document.getElementById('editIsActive').checked;
        const isAdmin = document.getElementById('editIsAdmin').checked;
        
        const submitBtn = e.target.querySelector('button[type="submit"]');
        submitBtn.disabled = true;
        
        try {
            const response = await API.updateUser(userId, {
                is_active: isActive,
                is_admin: isAdmin
            });
            
            if (response.success) {
                this.closeEditUserModal();
                this.loadUsersData(this.currentUsersPage, document.getElementById('userSearch')?.value || '');
                UI.showToast('✅ User updated successfully!', 'success');
            } else {
                this.showEditUserError(response.error || 'Failed to update user');
            }
            
        } catch (error) {
            Utils.logError('Failed to update user:', error);
            this.showEditUserError('Failed to update user. Please try again.');
        } finally {
            submitBtn.disabled = false;
        }
    },

    /**
     * Show edit user error
     */
    showEditUserError(message) {
        const errorDiv = document.getElementById('editUserError');
        if (errorDiv) {
            errorDiv.textContent = message;
            errorDiv.style.display = 'block';
        }
    },

    // ===================================
    // DATA EXPORT
    // ===================================
    
    /**
     * Export users to CSV
     */
    async exportUsers() {
        try {
            UI.showOverlayLoading('Exporting users...');
            
            const response = await API.getUsers(1, 10000, ''); // Get all users
            
            if (!response.success) {
                throw new Error('Failed to export users');
            }
            
            const headers = ['ID', 'Username', 'Email', 'Total Score', 'Games Played', 'Prediction Accuracy', 'AI Success Rate', 'Is Admin', 'Is Active', 'Created At'];
            const csvData = response.users.map(user => ({
                'ID': user.id,
                'Username': user.username,
                'Email': user.email,
                'Total Score': user.total_score || 0,
                'Games Played': user.games_played || 0,
                'Prediction Accuracy': user.prediction_accuracy || 0,
                'AI Success Rate': user.ai_success_rate || 0,
                'Is Admin': user.is_admin,
                'Is Active': user.is_active,
                'Created At': user.created_at
            }));
            
            this.downloadCSV(csvData, `users_export_${new Date().toISOString().split('T')[0]}.csv`, headers);
            UI.showToast('✅ Users exported successfully!', 'success');
            
        } catch (error) {
            Utils.logError('Failed to export users:', error);
            UI.showToast('❌ Failed to export users', 'error');
        } finally {
            UI.hideOverlayLoading();
        }
    },

    /**
     * Export games to CSV
     */
    async exportGames() {
        try {
            UI.showOverlayLoading('Exporting games...');
            
            const response = await API.getGames(1, 10000); // Get all games
            
            if (!response.success) {
                throw new Error('Failed to export games');
            }
            
            const headers = ['ID', 'Username', 'Agent Type', 'Prediction', 'Actual Steps', 'Succeeded', 'Score', 'Total Reward', 'Timestamp', 'GIF URL'];
            const csvData = response.games.map(game => ({
                'ID': game.id,
                'Username': game.username,
                'Agent Type': game.agent_type,
                'Prediction': game.prediction,
                'Actual Steps': game.actual_steps,
                'Succeeded': game.succeeded,
                'Score': game.score,
                'Total Reward': game.total_reward || 0,
                'Timestamp': game.timestamp,
                'GIF URL': game.gif_url || ''
            }));
            
            this.downloadCSV(csvData, `games_export_${new Date().toISOString().split('T')[0]}.csv`, headers);
            UI.showToast('✅ Games exported successfully!', 'success');
            
        } catch (error) {
            Utils.logError('Failed to export games:', error);
            UI.showToast('❌ Failed to export games', 'error');
        } finally {
            UI.hideOverlayLoading();
        }
    },

    /**
     * Download data as CSV
     */
    downloadCSV(data, filename, headers) {
        const csvContent = this.convertToCSV(data, headers);
        const blob = new Blob([csvContent], { type: 'text/csv' });
        const url = window.URL.createObjectURL(blob);
        
        const link = document.createElement('a');
        link.href = url;
        link.download = filename;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        
        window.URL.revokeObjectURL(url);
    },

    /**
     * Convert data to CSV format
     */
    convertToCSV(data, headers) {
        if (!data || data.length === 0) return '';
        
        const csvHeaders = headers || Object.keys(data[0]);
        const csvRows = [
            csvHeaders.join(','),
            ...data.map(row => 
                csvHeaders.map(header => {
                    const value = row[header];
                    // Escape quotes and wrap in quotes if contains comma/quote
                    if (typeof value === 'string' && (value.includes(',') || value.includes('"'))) {
                        return `"${value.replace(/"/g, '""')}"`;
                    }
                    return value;
                }).join(',')
            )
        ];
        
        return csvRows.join('\n');
    },

    // ===================================
    // DATABASE OPERATIONS
    // ===================================
    
    /**
     * Cleanup old videos
     */
    async cleanupOldVideos() {
        if (!confirm('🧹 This will remove old MP4 video files to save space. Continue?')) {
            return;
        }
        
        try {
            UI.showOverlayLoading('Cleaning up old videos...');
            
            const response = await API.cleanupOldVideos();
            
            if (response.success) {
                UI.showToast(`✅ Cleanup completed! Removed ${response.removed_files || 0} old video files.`, 'success');
            } else {
                throw new Error(response.error || 'Cleanup failed');
            }
            
        } catch (error) {
            Utils.logError('Failed to cleanup videos:', error);
            UI.showToast('❌ Failed to cleanup videos', 'error');
        } finally {
            UI.hideOverlayLoading();
        }
    },

    /**
     * Confirm dangerous operations
     */
    confirmDangerousAction(action) {
        const messages = {
            backup: '💾 Database backup functionality would be implemented here.\n\nFor now, you can manually backup the SQLite file.'
        };
        
        alert(messages[action] || 'This action is not yet implemented.');
    },

    // ===================================
    // CLEANUP
    // ===================================
    
    /**
     * Cleanup when leaving admin panel
     */
    cleanup() {
        if (this.autoRefreshInterval) {
            clearInterval(this.autoRefreshInterval);
        }
        
        if (this.searchTimeout) {
            clearTimeout(this.searchTimeout);
        }
    }
};

// ===================================
// GLOBAL FUNCTIONS FOR BACKWARD COMPATIBILITY
// ===================================

window.switchTab = function(tabName) {
    Admin.switchTab(tabName);
};

window.exportUsers = function() {
    Admin.exportUsers();
};

window.exportGames = function() {
    Admin.exportGames();
};

window.cleanupOldVideos = function() {
    Admin.cleanupOldVideos();
};

window.confirmDangerousAction = function(action) {
    Admin.confirmDangerousAction(action);
};

window.editUser = function(userId, username, email, isActive, isAdmin) {
    Admin.editUser(userId, username, email, isActive, isAdmin);
};

window.closeEditUserModal = function() {
    Admin.closeEditUserModal();
};

// Cleanup on page unload
window.addEventListener('beforeunload', () => {
    Admin.cleanup();
});

// Make Admin globally available
window.Admin = Admin;