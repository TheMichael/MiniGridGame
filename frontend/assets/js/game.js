// ===================================
// GAME.JS - Game Logic
// AI Agent Galaxy - Game-specific functionality
// ===================================

const Game = {
    // ===================================
    // STATE MANAGEMENT
    // ===================================
    
    selectedAgent: null,
    currentPrediction: null,
    isRunning: false,
    lastResult: null,
    
    // ===================================
    // INITIALIZATION
    // ===================================
    
    init() {
        this.bindEvents();
        this.loadLastAgent();
        this.setupRiskDisplay();
    },

    /**
     * Bind game-related events
     */
    bindEvents() {
        // Agent selection buttons
        document.querySelectorAll('.agent-btn').forEach(btn => {
            btn.addEventListener('click', (e) => this.handleAgentSelection(e));
        });

        // Prediction input
        const predictionInput = document.getElementById('predictionInput');
        if (predictionInput) {
            predictionInput.addEventListener('input', () => this.updateRiskDisplay());
            predictionInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') {
                    e.preventDefault();
                    this.handleRunPrediction();
                }
            });
        }

        // Prediction form
        const predictionForm = document.getElementById('predictionForm');
        if (predictionForm) {
            predictionForm.addEventListener('submit', (e) => {
                e.preventDefault();
                this.handleRunPrediction();
            });
        }

        // Play again button
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('play-again-btn') || 
                e.target.closest('.play-again-btn')) {
                this.resetGame();
            }
        });

        // Steps toggle
        const stepsToggle = document.querySelector('.steps-toggle');
        if (stepsToggle) {
            stepsToggle.addEventListener('click', () => this.toggleStepsLog());
        }
    },

    // ===================================
    // AGENT SELECTION
    // ===================================
    
    /**
     * Handle agent selection
     */
    handleAgentSelection(event) {
        const btn = event.currentTarget;
        const agent = btn.dataset.agent;
        
        if (!agent) return;
        
        // Update selection UI
        document.querySelectorAll('.agent-btn').forEach(b => b.classList.remove('selected'));
        btn.classList.add('selected');
        
        // Update state
        this.selectedAgent = agent;
        
        // Save preference
        Utils.setStorageItem(CONFIG.STORAGE_KEYS.LAST_AGENT, agent);
        
        // Enable prediction input if disabled
        const predictionInput = document.getElementById('predictionInput');
        if (predictionInput) {
            predictionInput.disabled = false;
            predictionInput.focus();
        }
        
        console.log(`Selected agent: ${agent.toUpperCase()}`);
    },

    /**
     * Load last selected agent
     */
    loadLastAgent() {
        const lastAgent = Utils.getStorageItem(CONFIG.STORAGE_KEYS.LAST_AGENT);
        if (lastAgent) {
            const agentBtn = document.querySelector(`[data-agent="${lastAgent}"]`);
            if (agentBtn) {
                agentBtn.click();
            }
        }
    },

    // ===================================
    // RISK DISPLAY
    // ===================================
    
    /**
     * Setup risk display functionality
     */
    setupRiskDisplay() {
        // Initial hide
        const riskIndicator = document.getElementById('riskIndicator');
        if (riskIndicator) {
            riskIndicator.style.display = 'none';
        }
    },

    /**
     * Update risk display based on prediction input
     */
    updateRiskDisplay() {
        const predictionInput = document.getElementById('predictionInput');
        const riskIndicator = document.getElementById('riskIndicator');
        const riskText = document.getElementById('riskText');
        
        if (!predictionInput || !riskIndicator || !riskText) return;
        
        const value = parseInt(predictionInput.value);
        
        if (isNaN(value) || value < 0 || value > 120) {
            riskIndicator.style.display = 'none';
            return;
        }
        
        const zone = Utils.getRiskZone(value);
        const message = Utils.getRiskMessage(value);
        
        // Map zones to CSS classes
        const zoneClasses = {
            'failure': 'risk-medium',
            'impossible': 'risk-impossible',
            'minimum': 'risk-medium', 
            'safe': 'risk-safe',
            'probable': 'risk-medium',
            'struggle': 'risk-high',
            'failure-zone': 'risk-high'
        };
        
        riskIndicator.className = `risk-indicator ${zoneClasses[zone] || 'risk-safe'}`;
        riskText.textContent = message;
        riskIndicator.style.display = 'block';
    },

    // ===================================
    // GAME EXECUTION
    // ===================================
    
    /**
     * Handle run prediction button click
     */
    async handleRunPrediction() {
        if (!Auth.requireLogin()) return;
        
        const predictionInput = document.getElementById('predictionInput');
        const prediction = predictionInput ? predictionInput.value : null;
        
        // Validate inputs
        if (!this.selectedAgent) {
            UI.showToast('🤖 Please select an AI agent first!', 'warning');
            return;
        }
        
        if (!prediction || !Utils.isValidPrediction(prediction)) {
            UI.showToast('🎯 Please enter a valid prediction (0-120)!', 'warning');
            if (predictionInput) predictionInput.focus();
            return;
        }
        
        await this.runPrediction(this.selectedAgent, prediction);
    },

    /**
     * Run prediction with selected agent
     */
    async runPrediction(agentType, prediction) {
        if (this.isRunning) {
            UI.showToast('⏳ Please wait for current prediction to complete', 'info');
            return;
        }
        
        this.isRunning = true;
        this.currentPrediction = parseInt(prediction);
        
        // Update UI state
        this.showLoadingState();
        
        try {
            const result = await API.runValidation(agentType, prediction);
            
            if (result.success) {
                this.lastResult = result;
                this.displayResults(result);
                this.updateUserStats(result.user_stats);
            } else {
                throw new Error(result.error || 'Prediction failed');
            }
            
        } catch (error) {
            Utils.logError('Game prediction failed:', error);
            this.handleGameError(error);
        } finally {
            this.isRunning = false;
            this.hideLoadingState();
        }
    },

    // ===================================
    // UI STATE MANAGEMENT
    // ===================================
    
    /**
     * Show loading state
     */
    showLoadingState() {
        // Hide form and results
        const predictionSection = document.querySelector('.prediction-section');
        const resultsSection = document.getElementById('results');
        
        if (predictionSection) predictionSection.style.display = 'none';
        if (resultsSection) resultsSection.style.display = 'none';
        
        // Show loading
        const loadingDiv = document.getElementById('loading');
        if (loadingDiv) {
            loadingDiv.style.display = 'block';
        }
        
        // Disable run button
        const runBtn = document.querySelector('.run-btn');
        if (runBtn) {
            runBtn.disabled = true;
            runBtn.textContent = '🚀 Mission In Progress...';
        }
    },

    /**
     * Hide loading state
     */
    hideLoadingState() {
        const loadingDiv = document.getElementById('loading');
        if (loadingDiv) {
            loadingDiv.style.display = 'none';
        }
        
        // Re-enable run button
        const runBtn = document.querySelector('.run-btn');
        if (runBtn) {
            runBtn.disabled = false;
            runBtn.textContent = '🚀 Launch Mission';
        }
    },

    // ===================================
    // RESULTS DISPLAY
    // ===================================
    
    /**
     * Display game results
     */
    displayResults(result) {
        // Show results section
        const resultsSection = document.getElementById('results');
        if (resultsSection) {
            resultsSection.style.display = 'block';
            resultsSection.scrollIntoView({ behavior: 'smooth' });
        }
        
        // Update score display
        this.updateScoreDisplay(result);
        
        // Update result stats
        this.updateResultStats(result);
        
        // Display video/GIF
        this.displayVideo(result);
        
        // Display steps log
        this.displayStepsLog(result.steps_log || []);
        
        // Show success toast
        UI.showToast(`🎯 Mission complete! Scored ${result.score} points`, 'success');
    },

    /**
     * Update score display
     */
    updateScoreDisplay(result) {
        const scoreElement = document.getElementById('roundScore');
        const explanationElement = document.getElementById('scoreExplanation');
        
        if (scoreElement) {
            scoreElement.textContent = result.score || 0;
        }
        
        if (explanationElement) {
            explanationElement.textContent = this.getScoreExplanation(
                this.currentPrediction, 
                result.steps, 
                result.succeeded, 
                result.score
            );
        }
    },

    /**
     * Update result statistics
     */
    updateResultStats(result) {
        const elements = {
            userPrediction: document.getElementById('userPrediction'),
            actualResult: document.getElementById('actualResult'),
            agentUsed: document.getElementById('agentUsed'),
            successStatus: document.getElementById('successStatus')
        };
        
        if (elements.userPrediction) {
            elements.userPrediction.textContent = this.currentPrediction === 0 ? 
                'Will fail' : `${this.currentPrediction} steps`;
        }
        
        if (elements.actualResult) {
            elements.actualResult.textContent = `${result.steps} steps`;
        }
        
        if (elements.agentUsed) {
            elements.agentUsed.textContent = (result.agent_type || this.selectedAgent).toUpperCase();
        }
        
        if (elements.successStatus) {
            elements.successStatus.textContent = result.succeeded ? '🟢 SUCCESS' : '🔴 FAILED';
        }
    },

    /**
     * Display video/GIF
     */
    displayVideo(result) {
        const videoError = document.getElementById('videoError');
        
        if (!videoError) return;
        
        if (result.gif_url) {
            videoError.innerHTML = `
                <img src="${result.gif_url}" 
                     style="max-width: 100%; border-radius: 15px; cursor: pointer;" 
                     alt="AI Agent Mission" 
                     onclick="this.src=this.src" 
                     title="🔄 Click to restart GIF">
            `;
            videoError.style.display = 'block';
            videoError.style.color = 'inherit';
        } else {
            videoError.style.display = 'block';
            videoError.style.color = 'var(--error)';
            videoError.textContent = '❌ Mission replay failed to generate';
        }
    },

    /**
     * Display steps log
     */
    displayStepsLog(stepsData) {
        const stepsList = document.getElementById('stepsList');
        
        if (!stepsList) return;
        
        if (!stepsData || stepsData.length === 0) {
            stepsList.innerHTML = '<p style="color: var(--text-secondary); text-align: center;">No step data available</p>';
            return;
        }
        
        let stepsHTML = '';
        stepsData.forEach((step, index) => {
            const actionName = Utils.getActionName(step.action);
            const rewardClass = step.reward >= 0 ? '' : 'negative';
            
            stepsHTML += `
                <div class="step-item">
                    <div class="step-number">${index + 1}</div>
                    <div class="step-action">${actionName}</div>
                    <div class="step-result">${step.result || 'Step executed'}</div>
                    <div class="step-reward ${rewardClass}">
                        ${step.reward >= 0 ? '+' : ''}${step.reward.toFixed(1)}
                    </div>
                </div>
            `;
        });
        
        stepsList.innerHTML = stepsHTML;
        
        // Reset steps log visibility
        const stepsContent = document.getElementById('stepsContent');
        const stepsToggle = document.querySelector('.steps-toggle');
        
        if (stepsContent) stepsContent.style.display = 'none';
        if (stepsToggle) stepsToggle.textContent = '📋 Show Detailed Steps Log';
    },

    /**
     * Toggle steps log visibility
     */
    toggleStepsLog() {
        const content = document.getElementById('stepsContent');
        const button = document.querySelector('.steps-toggle');
        
        if (!content || !button) return;
        
        if (content.style.display === 'none') {
            content.style.display = 'block';
            button.textContent = '📋 Hide Detailed Steps Log';
        } else {
            content.style.display = 'none';
            button.textContent = '📋 Show Detailed Steps Log';
        }
    },

    // ===================================
    // USER STATS UPDATE
    // ===================================
    
    /**
     * Update user stats in real-time
     */
    updateUserStats(userStats) {
        if (!userStats) return;
        
        const elements = {
            totalScore: document.getElementById('totalScore'),
            gamesPlayed: document.getElementById('gamesPlayed'),
            successRate: document.getElementById('successRate')
        };
        
        if (elements.totalScore) {
            elements.totalScore.textContent = Utils.formatNumber(userStats.total_score || 0);
        }
        
        if (elements.gamesPlayed) {
            elements.gamesPlayed.textContent = userStats.games_played || 0;
        }
        
        if (elements.successRate) {
            elements.successRate.textContent = (userStats.prediction_accuracy || 0) + '%';
        }
        
        // Update Auth module if available
        if (Auth.currentUser) {
            Auth.currentUser.total_score = userStats.total_score;
            Auth.currentUser.games_played = userStats.games_played;
            Auth.currentUser.prediction_accuracy = userStats.prediction_accuracy;
        }
    },

    // ===================================
    // UTILITY FUNCTIONS
    // ===================================
    
    /**
     * Get score explanation
     */
    getScoreExplanation(prediction, actualSteps, succeeded, actualScore) {
        const predictionNum = parseInt(prediction);
        
        if (predictionNum === 0) {
            return !succeeded ? 
                "🎯 PERFECT! You predicted the failure correctly!" :
                "❌ The agent actually succeeded, no points this time.";
        }
        
        const difference = Math.abs(predictionNum - actualSteps);
        
        // Determine base accuracy
        let accuracy = "";
        if (difference === 0) accuracy = "BULL'S EYE! Perfect prediction!";
        else if (difference <= 5) accuracy = `CLOSE! Only ${difference} steps off.`;
        else if (difference <= 10) accuracy = `DECENT! ${difference} steps off.`;
        else accuracy = `OFF TARGET - ${difference} steps difference.`;
        
        // Add risk zone explanation
        const zone = Utils.getRiskZone(predictionNum);
        let riskExplanation = "";
        
        switch (zone) {
            case 'safe':
                riskExplanation = " (Safe zone penalty applied)";
                break;
            case 'impossible':
                riskExplanation = " (Impossible zone - heavy penalty)";
                break;
            case 'struggle':
                riskExplanation = " (Struggle zone bonus!)";
                break;
            case 'failure-zone':
                riskExplanation = " (Failure zone bonus!)";
                break;
        }
        
        return `🚀 ${accuracy}${riskExplanation}`;
    },

    /**
     * Handle game errors
     */
    handleGameError(error) {
        if (error instanceof APIError && error.isAuthError()) {
            UI.showToast('🚨 Session expired! Please log in again.', 'error');
            Auth.clearUser();
        } else {
            UI.showToast('🚨 Mission failed! Please try again.', 'error');
        }
        
        Utils.logError('Game error:', error);
    },

    // ===================================
    // GAME RESET
    // ===================================
    
    /**
     * Reset game for another round
     */
    resetGame() {
        // Clear form
        const predictionForm = document.getElementById('predictionForm');
        if (predictionForm) {
            predictionForm.reset();
        }
        
        // Hide results
        const resultsSection = document.getElementById('results');
        if (resultsSection) {
            resultsSection.style.display = 'none';
        }
        
        // Show prediction section
        const predictionSection = document.querySelector('.prediction-section');
        if (predictionSection) {
            predictionSection.style.display = 'grid';
        }
        
        // Reset state
        this.currentPrediction = null;
        this.lastResult = null;
        
        // Re-enable run button
        const runBtn = document.querySelector('.run-btn');
        if (runBtn) {
            runBtn.disabled = false;
        }
        
        // Hide risk indicator
        const riskIndicator = document.getElementById('riskIndicator');
        if (riskIndicator) {
            riskIndicator.style.display = 'none';
        }
        
        // Focus on prediction input (keep agent selection)
        const predictionInput = document.getElementById('predictionInput');
        if (predictionInput) {
            predictionInput.focus();
        }
        
        // Scroll to top
        window.scrollTo({ top: 0, behavior: 'smooth' });
    }
};

// ===================================
// GLOBAL FUNCTIONS FOR BACKWARD COMPATIBILITY
// ===================================

// Legacy functions that might be called from HTML
window.updateRiskDisplay = function() {
    Game.updateRiskDisplay();
};

window.resetGame = function() {
    Game.resetGame();
};

window.toggleStepsLog = function() {
    Game.toggleStepsLog();
};

// Make Game globally available
window.Game = Game;