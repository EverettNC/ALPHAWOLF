/**
 * AlphaWolf Voice Command Processor
 * Part of The Christman AI Project - Powered by LumaCognify AI
 */

// Commands configuration
const voiceCommands = {
    navigation: {
        'go home': () => navigateTo('/home'),
        'go to home': () => navigateTo('/home'),
        'homepage': () => navigateTo('/home'),
        'go to login': () => navigateTo('/login'),
        'login page': () => navigateTo('/login'),
        'go to dashboard': () => handleDashboardNavigation(),
        'open dashboard': () => handleDashboardNavigation(),
        'show dashboard': () => handleDashboardNavigation(),
        'go to exercises': () => navigateTo('/cognitive_exercises'),
        'open exercises': () => navigateTo('/cognitive_exercises'),
        'go to reminders': () => navigateTo('/reminders'),
        'open reminders': () => navigateTo('/reminders'),
        'show reminders': () => navigateTo('/reminders'),
        'go to safety zones': () => navigateTo('/safety_zones'),
        'open safety zones': () => navigateTo('/safety_zones'),
        'go to learning corner': () => navigateTo('/learning_corner'),
        'open learning corner': () => navigateTo('/learning_corner'),
        'learning resources': () => navigateTo('/learning_corner'),
        'go to caregivers': () => navigateTo('/caregivers_page'),
        'open caregivers page': () => navigateTo('/caregivers_page'),
        'go to memory lane': () => navigateTo('/memory_lane'),
        'open memories': () => navigateTo('/memory_lane'),
        'view memories': () => navigateTo('/memory_lane'),
        'go to profile': () => navigateTo('/user_profile'),
        'open profile': () => navigateTo('/user_profile'),
        'open my profile': () => navigateTo('/user_profile')
    },
    
    actions: {
        'mute': () => toggleVoiceControl(),
        'unmute': () => {
            if (!isListening) toggleVoiceControl();
        },
        'stop listening': () => {
            if (isListening) toggleVoiceControl();
        },
        'start listening': () => {
            if (!isListening) toggleVoiceControl();
        },
        'toggle voice': () => toggleVoiceControl(),
        'log out': () => navigateTo('/logout'),
        'sign out': () => navigateTo('/logout'),
        'logout': () => navigateTo('/logout'),
        'refresh page': () => window.location.reload(),
        'reload page': () => window.location.reload(),
        'help': () => showHelpModal(),
        'show help': () => showHelpModal(),
        'voice commands': () => showHelpModal(),
        'available commands': () => showHelpModal(),
        'what can i say': () => showHelpModal(),
        'commands': () => showHelpModal()
    },
    
    // Form actions - these require elements to be present on the page
    forms: {
        'submit form': () => submitCurrentForm(),
        'submit': () => submitCurrentForm(),
        'cancel': () => cancelCurrentAction(),
        'clear form': () => clearCurrentForm(),
        'reset form': () => clearCurrentForm()
    }
};

// Process voice commands
function processVoiceCommand(speech) {
    // Don't process if empty
    if (!speech || speech.trim() === '') return;
    
    // Check for "alphawolf" wake word (optional enhancement)
    const hasWakeWord = speech.includes('alpha wolf') || 
                        speech.includes('alphawolf') || 
                        speech.includes('alpha') || 
                        speech.includes('wolf');
    
    // Process command categories
    let commandFound = false;
    
    // Process navigation commands
    for (const [command, action] of Object.entries(voiceCommands.navigation)) {
        if (speech.includes(command)) {
            showFeedback(`Executing: ${command}`, 'info');
            action();
            commandFound = true;
            break;
        }
    }
    
    // Process action commands if no navigation command was found
    if (!commandFound) {
        for (const [command, action] of Object.entries(voiceCommands.actions)) {
            if (speech.includes(command)) {
                showFeedback(`Executing: ${command}`, 'info');
                action();
                commandFound = true;
                break;
            }
        }
    }
    
    // Process form commands if no other command was found
    if (!commandFound) {
        for (const [command, action] of Object.entries(voiceCommands.forms)) {
            if (speech.includes(command)) {
                showFeedback(`Executing: ${command}`, 'info');
                action();
                commandFound = true;
                break;
            }
        }
    }
    
    // If no command was recognized but wake word was used, show help
    if (!commandFound && hasWakeWord) {
        showFeedback("Command not recognized. Try 'help' for available commands.", 'warning');
    }
}

// Navigation helper
function navigateTo(path) {
    window.location.href = path;
}

// Handle dashboard navigation based on user type
function handleDashboardNavigation() {
    // Check if user is a patient or caregiver (you can enhance this based on your authentication system)
    const isPatient = document.body.classList.contains('patient-user');
    const isCaregiver = document.body.classList.contains('caregiver-user');
    
    if (isPatient) {
        navigateTo('/patient_dashboard');
    } else if (isCaregiver) {
        navigateTo('/caregiver_dashboard');
    } else {
        // Default to login if user type is unknown
        navigateTo('/login');
        showFeedback("Please login first to access your dashboard", 'warning');
    }
}

// Form actions
function submitCurrentForm() {
    const form = document.querySelector('form');
    if (form) {
        form.submit();
    } else {
        showFeedback("No form found to submit", 'warning');
    }
}

function clearCurrentForm() {
    const form = document.querySelector('form');
    if (form) {
        const inputs = form.querySelectorAll('input:not([type=submit]):not([type=button]), textarea, select');
        inputs.forEach(input => {
            if (input.type === 'checkbox' || input.type === 'radio') {
                input.checked = false;
            } else {
                input.value = '';
            }
        });
        showFeedback("Form cleared", 'success');
    } else {
        showFeedback("No form found to clear", 'warning');
    }
}

function cancelCurrentAction() {
    // Find cancel button and click it
    const cancelBtn = document.querySelector('button[type="reset"], button.cancel, a.cancel, button.btn-secondary, button.btn-danger');
    if (cancelBtn) {
        cancelBtn.click();
    } else {
        // If no cancel button, try to navigate back
        window.history.back();
    }
}

// Help modal
function showHelpModal() {
    // Check if modal already exists
    let modal = document.getElementById('voice-commands-help-modal');
    
    if (!modal) {
        // Create modal structure
        modal = document.createElement('div');
        modal.id = 'voice-commands-help-modal';
        modal.className = 'voice-commands-modal modal fade';
        modal.tabIndex = '-1';
        modal.setAttribute('aria-labelledby', 'voiceCommandsModalLabel');
        modal.setAttribute('aria-hidden', 'true');
        
        const modalHTML = `
            <div class="modal-dialog modal-lg">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title" id="voiceCommandsModalLabel">
                            <i class="fas fa-microphone text-primary me-2"></i>
                            Available Voice Commands
                        </h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                    </div>
                    <div class="modal-body">
                        <div class="mb-4">
                            <h6 class="cyber-text">Navigation Commands:</h6>
                            <div class="row">
                                ${Object.keys(voiceCommands.navigation).map(cmd => `
                                    <div class="col-md-6 mb-2">
                                        <div class="voice-command-item">
                                            <span class="voice-command">"${cmd}"</span>
                                        </div>
                                    </div>
                                `).join('')}
                            </div>
                        </div>
                        
                        <div class="mb-4">
                            <h6 class="cyber-text">Action Commands:</h6>
                            <div class="row">
                                ${Object.keys(voiceCommands.actions).map(cmd => `
                                    <div class="col-md-6 mb-2">
                                        <div class="voice-command-item">
                                            <span class="voice-command">"${cmd}"</span>
                                        </div>
                                    </div>
                                `).join('')}
                            </div>
                        </div>
                        
                        <div>
                            <h6 class="cyber-text">Form Commands:</h6>
                            <div class="row">
                                ${Object.keys(voiceCommands.forms).map(cmd => `
                                    <div class="col-md-6 mb-2">
                                        <div class="voice-command-item">
                                            <span class="voice-command">"${cmd}"</span>
                                        </div>
                                    </div>
                                `).join('')}
                            </div>
                        </div>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-primary" data-bs-dismiss="modal">Close</button>
                    </div>
                </div>
            </div>
        `;
        
        modal.innerHTML = modalHTML;
        document.body.appendChild(modal);
    }
    
    // Initialize and show the modal
    const bsModal = new bootstrap.Modal(modal);
    bsModal.show();
}