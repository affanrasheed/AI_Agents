/**
 * Agentic RAG System - Main JavaScript
 */

document.addEventListener('DOMContentLoaded', () => {
    // DOM Elements
    const elements = {
        // Forms and inputs
        queryForm: document.getElementById('queryForm'),
        queryInput: document.getElementById('queryInput'),
        sendBtn: document.getElementById('sendBtn'),
        urlsInput: document.getElementById('urlsInput'),
        
        // Chat UI
        chatHistory: document.getElementById('chatHistory'),
        typingIndicator: document.getElementById('typingIndicator'),
        clearBtn: document.getElementById('clearBtn'),
        
        // Settings modal
        settingsBtn: document.getElementById('settingsBtn'),
        settingsModal: document.getElementById('settingsModal'),
        closeSettingsBtn: document.getElementById('closeSettingsBtn'),
        saveSettingsBtn: document.getElementById('saveSettingsBtn'),
        
        // Debug and status UI
        pipelineStatus: document.getElementById('pipelineStatus'),
        stepCards: document.querySelectorAll('.step-card'),
        debugToggleBtn: document.getElementById('debugToggleBtn'),
        debugLogs: document.getElementById('debugLogs'),
    };
    
    // State
    const state = {
        initialized: false,
        processing: false,
        currentStep: null,
        debugVisible: false
    };
    
    // Initialize
    init();
    
    /**
     * Initialize the application
     */
    function init() {
        // Check pipeline status
        checkPipelineStatus();
        
        // Get conversation history
        fetchHistory();
        
        // Set up event listeners
        setupEventListeners();
        
        // Poll for status updates
        setInterval(checkPipelineStatus, 5000);
    }
    
    /**
     * Set up event listeners
     */
    function setupEventListeners() {
        // Query form submission
        elements.queryForm.addEventListener('submit', handleQuerySubmit);
        
        // Clear chat history
        elements.clearBtn.addEventListener('click', handleClearHistory);
        
        // Settings modal
        elements.settingsBtn.addEventListener('click', () => toggleModal(true));
        elements.closeSettingsBtn.addEventListener('click', () => toggleModal(false));
        
        // Initialize pipeline with custom URLs
        elements.saveSettingsBtn.addEventListener('click', handleInitializePipeline);
        
        // Toggle debug logs
        elements.debugToggleBtn.addEventListener('click', toggleDebugLogs);
    }
    
    /**
     * Handle query form submission
     * @param {Event} e - Form submission event
     */
    async function handleQuerySubmit(e) {
        e.preventDefault();
        
        const query = elements.queryInput.value.trim();
        if (!query) return;
        
        // Clear input
        elements.queryInput.value = '';
        
        // Disable send button during processing
        toggleSendButton(false);
        
        // Add user message to chat
        addMessage('user', query);
        
        // Show typing indicator
        toggleTypingIndicator(true);
        
        // Reset step statuses
        resetStepStatuses();
        
        try {
            // Send query to server
            const response = await fetch('/query', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ query }),
            });
            
            const data = await response.json();
            
            if (data.status === 'success') {
                // Add assistant message to chat
                addMessage('assistant', data.answer);
                
                // Update debug logs
                updateDebugLogs(data.steps);
            } else {
                // Show error message
                addErrorMessage(data.message || 'An error occurred');
            }
        } catch (error) {
            console.error('Error:', error);
            addErrorMessage('Failed to process query');
        } finally {
            // Hide typing indicator
            toggleTypingIndicator(false);
            
            // Re-enable send button
            toggleSendButton(true);
        }
    }
    
    /**
     * Handle clear history button click
     */
    async function handleClearHistory() {
        const confirmed = confirm('Are you sure you want to clear the chat history?');
        if (!confirmed) return;
        
        try {
            const response = await fetch('/clear', {
                method: 'POST',
            });
            
            const data = await response.json();
            
            if (data.status === 'success') {
                elements.chatHistory.innerHTML = '';
                elements.debugLogs.innerHTML = '';
                resetStepStatuses();
            }
        } catch (error) {
            console.error('Error:', error);
        }
    }
    
    /**
     * Handle initialize pipeline button click
     */
    async function handleInitializePipeline() {
        const urls = elements.urlsInput.value.trim().split('\n').filter(url => url.trim());
        
        if (urls.length === 0) {
            alert('Please enter at least one URL');
            return;
        }
        
        try {
            // Update button state
            elements.saveSettingsBtn.disabled = true;
            elements.saveSettingsBtn.textContent = 'Initializing...';
            
            // Initialize pipeline
            const response = await fetch('/initialize', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ urls }),
            });
            
            const data = await response.json();
            
            if (data.status === 'success') {
                alert('Pipeline initialized successfully');
                toggleModal(false);
                updatePipelineStatus(true);
            } else {
                alert(data.message || 'Failed to initialize pipeline');
            }
        } catch (error) {
            console.error('Error:', error);
            alert('Failed to initialize pipeline');
        } finally {
            // Reset button state
            elements.saveSettingsBtn.disabled = false;
            elements.saveSettingsBtn.textContent = 'Initialize Pipeline';
        }
    }
    
    /**
     * Add a message to the chat history
     * @param {string} role - Message role (user or assistant)
     * @param {string} content - Message content
     */
    function addMessage(role, content) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `${role}-message fade-in`;
        
        const roleLabel = role === 'user' ? 'You' : 'Assistant';
        
        messageDiv.innerHTML = `
            <div class="flex items-start">
                <div class="flex-shrink-0 mr-3">
                    <div class="w-8 h-8 rounded-full flex items-center justify-center ${role === 'user' ? 'bg-blue-500' : 'bg-green-500'} text-white">
                        <i class="fas ${role === 'user' ? 'fa-user' : 'fa-robot'}"></i>
                    </div>
                </div>
                <div class="flex-1">
                    <p class="font-medium">${roleLabel}</p>
                    <div class="mt-1">${formatContent(content)}</div>
                </div>
            </div>
        `;
        
        elements.chatHistory.appendChild(messageDiv);
        elements.chatHistory.scrollTop = elements.chatHistory.scrollHeight;
    }
    
    /**
     * Add an error message to the chat history
     * @param {string} message - Error message
     */
    function addErrorMessage(message) {
        const errorDiv = document.createElement('div');
        errorDiv.className = 'p-3 bg-red-100 text-red-700 rounded-lg my-3 fade-in';
        errorDiv.innerHTML = `<i class="fas fa-exclamation-circle mr-2"></i>${message}`;
        elements.chatHistory.appendChild(errorDiv);
        elements.chatHistory.scrollTop = elements.chatHistory.scrollHeight;
    }
    
    /**
     * Format message content for display
     * @param {string} content - Message content
     * @returns {string} Formatted content
     */
    function formatContent(content) {
        // Replace newlines with <br>
        return content.replace(/\n/g, '<br>');
    }
    
    /**
     * Fetch conversation history from the server
     */
    async function fetchHistory() {
        try {
            const response = await fetch('/history');
            const data = await response.json();
            
            if (data.history && data.history.length > 0) {
                elements.chatHistory.innerHTML = '';
                
                data.history.forEach(msg => {
                    addMessage(msg.role, msg.content);
                });
            }
        } catch (error) {
            console.error('Error fetching history:', error);
        }
    }
    
    /**
     * Check the pipeline status
     */
    async function checkPipelineStatus() {
        try {
            const response = await fetch('/status');
            const data = await response.json();
            
            updatePipelineStatus(data.initialized);
            
            if (data.processing) {
                toggleTypingIndicator(true);
            } else {
                toggleTypingIndicator(false);
            }
            
            if (data.current_step) {
                updateStepStatus(data.current_step, 'active');
            }
        } catch (error) {
            console.error('Error checking pipeline status:', error);
        }
    }
    
    /**
     * Update the pipeline status display
     * @param {boolean} initialized - Whether the pipeline is initialized
     */
    function updatePipelineStatus(initialized) {
        state.initialized = initialized;
        
        if (initialized) {
            elements.pipelineStatus.textContent = 'Initialized';
            elements.pipelineStatus.classList.remove('bg-gray-200');
            elements.pipelineStatus.classList.add('bg-green-100', 'text-green-800');
        } else {
            elements.pipelineStatus.textContent = 'Not Initialized';
            elements.pipelineStatus.classList.remove('bg-green-100', 'text-green-800');
            elements.pipelineStatus.classList.add('bg-gray-200');
        }
    }
    
    /**
     * Reset all step statuses
     */
    function resetStepStatuses() {
        elements.stepCards.forEach(card => {
            card.classList.remove('active');
            const statusEl = card.querySelector('.step-status');
            statusEl.textContent = 'Pending';
            statusEl.className = 'step-status px-2 py-1 rounded-full text-xs font-medium bg-gray-200';
        });
    }
    
    /**
     * Update a step's status
     * @param {string} step - Step name
     * @param {string} status - New status (active, completed, error)
     */
    function updateStepStatus(step, status) {
        let stepCard;
        
        // Find the appropriate step card
        if (step === 'grade_documents') {
            stepCard = document.querySelector('.step-card[data-step="grade"]');
        } else {
            stepCard = document.querySelector(`.step-card[data-step="${step}"]`);
        }
        
        if (!stepCard) return;
        
        const statusEl = stepCard.querySelector('.step-status');
        
        // Reset all cards
        elements.stepCards.forEach(card => {
            card.classList.remove('active');
        });
        
        // Update status based on the state
        if (status === 'active') {
            stepCard.classList.add('active');
            statusEl.textContent = 'In Progress';
            statusEl.className = 'step-status px-2 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800';
        } else if (status === 'completed') {
            stepCard.classList.remove('active');
            statusEl.textContent = 'Completed';
            statusEl.className = 'step-status px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800';
        } else if (status === 'error') {
            stepCard.classList.remove('active');
            statusEl.textContent = 'Error';
            statusEl.className = 'step-status px-2 py-1 rounded-full text-xs font-medium bg-red-100 text-red-800';
        }
    }
    
    /**
     * Update debug logs with step information
     * @param {Array} steps - Array of step information objects
     */
    function updateDebugLogs(steps) {
        if (!steps || steps.length === 0) return;
        
        elements.debugLogs.innerHTML = '';
        
        steps.forEach((step, index) => {
            const stepDiv = document.createElement('div');
            stepDiv.className = 'mb-2 pb-2 border-b border-gray-200';
            
            // Get step name from the step object
            const stepName = step.step;
            
            // Update step status
            if (index === steps.length - 1) {
                updateStepStatus(stepName, 'active');
            } else {
                updateStepStatus(stepName, 'completed');
            }
            
            // Format the step content
            const content = step.content || 'No content';
            
            stepDiv.innerHTML = `
                <div class="font-bold text-xs text-blue-600 mb-1">${stepName}</div>
                <pre class="text-xs whitespace-pre-wrap">${content}</pre>
            `;
            
            elements.debugLogs.appendChild(stepDiv);
        });
        
        // Scroll to the bottom of the debug logs
        elements.debugLogs.scrollTop = elements.debugLogs.scrollHeight;
    }
    
    /**
     * Toggle the visibility of the settings modal
     * @param {boolean} show - Whether to show the modal
     */
    function toggleModal(show) {
        if (show) {
            elements.settingsModal.classList.remove('hidden');
        } else {
            elements.settingsModal.classList.add('hidden');
        }
    }
    
    /**
     * Toggle the visibility of debug logs
     */
    function toggleDebugLogs() {
        state.debugVisible = !state.debugVisible;
        
        if (state.debugVisible) {
            elements.debugLogs.classList.remove('hidden');
            elements.debugToggleBtn.innerHTML = '<i class="fas fa-chevron-up"></i>';
        } else {
            elements.debugLogs.classList.add('hidden');
            elements.debugToggleBtn.innerHTML = '<i class="fas fa-chevron-down"></i>';
        }
    }
    
    /**
     * Toggle the typing indicator
     * @param {boolean} show - Whether to show the typing indicator
     */
    function toggleTypingIndicator(show) {
        if (show) {
            elements.typingIndicator.classList.remove('hidden');
        } else {
            elements.typingIndicator.classList.add('hidden');
        }
    }
    
    /**
     * Toggle the send button state
     * @param {boolean} enabled - Whether the button should be enabled
     */
    function toggleSendButton(enabled) {
        elements.sendBtn.disabled = !enabled;
        
        if (enabled) {
            elements.sendBtn.classList.remove('opacity-50');
        } else {
            elements.sendBtn.classList.add('opacity-50');
        }
    }
});