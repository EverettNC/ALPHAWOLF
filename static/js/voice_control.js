/**
 * AlphaWolf Voice Control System
 * This script manages the voice control interface for AlphaWolf
 */

// Voice control state
let voiceControlEnabled = true;
const voiceToggleBtn = document.getElementById('voiceToggleBtn');
const voiceControlKey = 'alphawolf_voice_control';

// Initialize voice control based on previously saved state
document.addEventListener('DOMContentLoaded', () => {
    // Check if we're on the landing page
    const isLandingPage = !document.querySelector('header');
    
    if (isLandingPage) {
        // Don't show voice controls on landing page
        if (voiceToggleBtn) {
            voiceToggleBtn.style.display = 'none';
        }
        return;
    }
    
    // Load previous voice control state from localStorage
    const savedState = localStorage.getItem(voiceControlKey);
    if (savedState !== null) {
        voiceControlEnabled = savedState === 'true';
    }
    
    // Update UI based on voice control state
    updateVoiceControlUI();
    
    // Set up event listener for voice toggle button
    if (voiceToggleBtn) {
        voiceToggleBtn.addEventListener('click', toggleVoiceControl);
    }
    
    // Initialize voice control system if enabled
    if (voiceControlEnabled) {
        initializeVoiceRecognition();
    }
    
    console.log(`Voice control system initialized. Status: ${voiceControlEnabled ? 'Active' : 'Muted'}`);
});

/**
 * Toggle voice control on/off
 */
function toggleVoiceControl() {
    voiceControlEnabled = !voiceControlEnabled;
    
    // Save state to localStorage for persistence across pages
    localStorage.setItem(voiceControlKey, voiceControlEnabled.toString());
    
    // Update UI
    updateVoiceControlUI();
    
    // Enable or disable voice recognition
    if (voiceControlEnabled) {
        initializeVoiceRecognition();
        showNotification('Voice control activated', 'success');
    } else {
        stopVoiceRecognition();
        showNotification('Voice control deactivated', 'warning');
    }
    
    console.log(`Voice control toggled: ${voiceControlEnabled ? 'Active' : 'Muted'}`);
}

/**
 * Update UI elements based on voice control state
 */
function updateVoiceControlUI() {
    if (!voiceToggleBtn) return;
    
    // Update button appearance
    if (voiceControlEnabled) {
        voiceToggleBtn.classList.remove('muted');
        voiceToggleBtn.innerHTML = '<i class="fas fa-microphone"></i>';
    } else {
        voiceToggleBtn.classList.add('muted');
        voiceToggleBtn.innerHTML = '<i class="fas fa-microphone-slash"></i>';
    }
    
    // Update any voice status indicators
    const voiceStatusElements = document.querySelectorAll('.voice-status');
    voiceStatusElements.forEach(element => {
        if (voiceControlEnabled) {
            element.classList.remove('muted');
            element.classList.add('active');
            const iconElement = element.querySelector('.voice-status-icon');
            if (iconElement) {
                iconElement.className = 'fas fa-microphone voice-status-icon';
            }
            const textElement = element.querySelector('span:not(.voice-status-icon)');
            if (textElement) {
                textElement.textContent = 'Voice control active';
            }
        } else {
            element.classList.remove('active');
            element.classList.add('muted');
            const iconElement = element.querySelector('.voice-status-icon');
            if (iconElement) {
                iconElement.className = 'fas fa-microphone-slash voice-status-icon';
            }
            const textElement = element.querySelector('span:not(.voice-status-icon)');
            if (textElement) {
                textElement.textContent = 'Voice control muted';
            }
        }
    });
}

/**
 * Initialize voice recognition system
 */
function initializeVoiceRecognition() {
    // Check if browser supports speech recognition
    if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
        console.error('Speech recognition not supported in this browser');
        showNotification('Voice control not supported in this browser', 'error');
        return;
    }
    
    // Initialize recognition based on browser support
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    const recognition = new SpeechRecognition();
    
    // Configure recognition
    recognition.continuous = true;
    recognition.interimResults = true;
    recognition.lang = 'en-US';
    
    // Set up event handlers
    recognition.onstart = function() {
        console.log('Voice recognition started');
    };
    
    recognition.onresult = function(event) {
        const result = event.results[event.results.length - 1];
        const transcript = result[0].transcript.trim().toLowerCase();
        
        // Check if this is a final result
        if (result.isFinal) {
            console.log('Final transcript:', transcript);
            
            // Check for wake word "alpha"
            if (transcript.includes('alpha')) {
                handleVoiceCommand(transcript);
            }
        }
    };
    
    recognition.onerror = function(event) {
        console.error('Speech recognition error:', event.error);
        if (event.error === 'no-speech') {
            // Restart recognition if no speech detected
            recognition.stop();
            setTimeout(() => {
                if (voiceControlEnabled) {
                    recognition.start();
                }
            }, 500);
        }
    };
    
    recognition.onend = function() {
        console.log('Voice recognition ended');
        // Restart recognition if still enabled
        if (voiceControlEnabled) {
            recognition.start();
        }
    };
    
    // Start recognition
    try {
        recognition.start();
    } catch (e) {
        console.error('Error starting speech recognition:', e);
    }
    
    // Store reference to recognition object
    window.alphaWolfRecognition = recognition;
}

/**
 * Stop voice recognition
 */
function stopVoiceRecognition() {
    if (window.alphaWolfRecognition) {
        try {
            window.alphaWolfRecognition.stop();
        } catch (e) {
            console.error('Error stopping speech recognition:', e);
        }
    }
}

/**
 * Display notification to the user
 */
function showNotification(message, type = 'info') {
    // Create notification container if it doesn't exist
    let notificationContainer = document.getElementById('notification-container');
    
    if (!notificationContainer) {
        notificationContainer = document.createElement('div');
        notificationContainer.id = 'notification-container';
        notificationContainer.style.position = 'fixed';
        notificationContainer.style.top = '20px';
        notificationContainer.style.right = '20px';
        notificationContainer.style.zIndex = '9999';
        document.body.appendChild(notificationContainer);
    }
    
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.style.backgroundColor = 'rgba(15, 15, 25, 0.9)';
    notification.style.border = '1px solid var(--border-color)';
    notification.style.borderLeft = type === 'success' ? '4px solid #4ade80' : 
                                    type === 'warning' ? '4px solid #fbbf24' : 
                                    type === 'error' ? '4px solid #ef4444' : 
                                    '4px solid #6ea8fe';
    notification.style.color = '#fff';
    notification.style.padding = '12px 20px';
    notification.style.marginBottom = '10px';
    notification.style.borderRadius = '5px';
    notification.style.boxShadow = '0 4px 12px rgba(0, 0, 0, 0.15)';
    notification.style.display = 'flex';
    notification.style.alignItems = 'center';
    notification.style.transition = 'all 0.3s ease';
    notification.style.transform = 'translateX(100%)';
    notification.style.opacity = '0';
    
    // Add icon based on notification type
    const icon = document.createElement('i');
    icon.className = type === 'success' ? 'fas fa-check-circle' : 
                    type === 'warning' ? 'fas fa-exclamation-triangle' : 
                    type === 'error' ? 'fas fa-times-circle' : 
                    'fas fa-info-circle';
    icon.style.marginRight = '10px';
    icon.style.fontSize = '1.25rem';
    icon.style.color = type === 'success' ? '#4ade80' : 
                      type === 'warning' ? '#fbbf24' : 
                      type === 'error' ? '#ef4444' : 
                      '#6ea8fe';
    
    notification.appendChild(icon);
    
    // Add message
    const messageElement = document.createElement('span');
    messageElement.textContent = message;
    notification.appendChild(messageElement);
    
    // Add to container
    notificationContainer.appendChild(notification);
    
    // Animate in
    setTimeout(() => {
        notification.style.transform = 'translateX(0)';
        notification.style.opacity = '1';
    }, 10);
    
    // Remove after 5 seconds
    setTimeout(() => {
        notification.style.transform = 'translateX(100%)';
        notification.style.opacity = '0';
        
        // Remove from DOM after animation
        setTimeout(() => {
            notificationContainer.removeChild(notification);
        }, 300);
    }, 5000);
}