/**
 * AlphaWolf Voice Control System
 * Part of The Christman AI Project - Powered by LumaCognify AI
 */

// Initialize variables
let recognition;
let isListening = true;
let lastRecognizedSpeech = '';
const voiceControlStatus = document.getElementById('voice-control-status');
const voiceControlToggle = document.getElementById('voice-control-toggle');

// Speech Recognition setup
function initVoiceControl() {
    try {
        // Check if voice control was previously disabled by user
        const savedVoiceControlState = localStorage.getItem('alphawolf_voice_control');
        isListening = savedVoiceControlState !== 'inactive';
        
        // Setup Web Speech API
        window.SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        recognition = new window.SpeechRecognition();
        recognition.continuous = false;
        recognition.interimResults = false;
        recognition.lang = 'en-US';
        
        // Set initial UI state
        updateVoiceControlUI();
        
        // Start recognition if active
        if (isListening) {
            startVoiceRecognition();
        }
        
        // Add event listener to the toggle button
        if (voiceControlToggle) {
            voiceControlToggle.addEventListener('click', toggleVoiceControl);
        }
        
        console.log("Voice control system initialized. Status: " + (isListening ? "Active" : "Inactive"));
    } catch (error) {
        console.error("Error initializing voice control:", error);
        isListening = false;
        updateVoiceControlUI();
    }
}

// Start voice recognition
function startVoiceRecognition() {
    if (!recognition) return;
    
    try {
        recognition.start();
        console.log("Voice recognition started");
        
        // Recognition events
        recognition.onresult = function(event) {
            const speechResult = event.results[0][0].transcript.toLowerCase();
            lastRecognizedSpeech = speechResult;
            console.log("Speech recognized:", speechResult);
            
            // Process the speech command
            processVoiceCommand(speechResult);
        };
        
        recognition.onerror = function(event) {
            console.error("Speech recognition error:", event.error);
            if (isListening) {
                // Restart recognition after a brief pause on error
                setTimeout(() => {
                    if (isListening) startVoiceRecognition();
                }, 500);
            }
        };
        
        recognition.onend = function() {
            console.log("Voice recognition ended");
            // Restart if still in listening mode
            if (isListening) {
                setTimeout(() => {
                    if (isListening) startVoiceRecognition();
                }, 500);
            }
        };
    } catch (error) {
        console.error("Error starting voice recognition:", error);
    }
}

// Toggle voice control on/off
function toggleVoiceControl() {
    isListening = !isListening;
    
    // Save state to localStorage for persistence
    localStorage.setItem('alphawolf_voice_control', isListening ? 'active' : 'inactive');
    
    // Update UI
    updateVoiceControlUI();
    
    // Start or stop recognition
    if (isListening) {
        startVoiceRecognition();
    } else {
        if (recognition) {
            try {
                recognition.stop();
            } catch (e) {
                console.error("Error stopping recognition:", e);
            }
        }
    }
    
    // Provide feedback to user
    if (isListening) {
        showFeedback("Voice control enabled");
    } else {
        showFeedback("Voice control disabled");
    }
}

// Update the UI to reflect current voice control state
function updateVoiceControlUI() {
    if (!voiceControlStatus) return;
    
    if (isListening) {
        voiceControlStatus.textContent = "Active";
        voiceControlStatus.classList.remove("inactive");
    } else {
        voiceControlStatus.textContent = "Inactive";
        voiceControlStatus.classList.add("inactive");
    }
}

// Display temporary feedback to user
function showFeedback(message, type = 'info') {
    // Check if feedback container exists, otherwise create it
    let feedbackContainer = document.getElementById('voice-feedback-container');
    
    if (!feedbackContainer) {
        feedbackContainer = document.createElement('div');
        feedbackContainer.id = 'voice-feedback-container';
        feedbackContainer.style.position = 'fixed';
        feedbackContainer.style.bottom = '20px';
        feedbackContainer.style.left = '20px';
        feedbackContainer.style.zIndex = '9999';
        document.body.appendChild(feedbackContainer);
    }
    
    // Create feedback element
    const feedback = document.createElement('div');
    feedback.classList.add('voice-feedback', `voice-feedback-${type}`);
    feedback.style.padding = '10px 15px';
    feedback.style.borderRadius = '5px';
    feedback.style.marginTop = '10px';
    feedback.style.backgroundColor = 'rgba(20, 20, 30, 0.9)';
    feedback.style.color = '#fff';
    feedback.style.border = `1px solid var(--${type}-color, #4f46e5)`;
    feedback.style.boxShadow = '0 4px 6px rgba(0, 0, 0, 0.1)';
    feedback.style.fontFamily = "'Share Tech Mono', monospace";
    feedback.style.transition = 'all 0.3s ease';
    feedback.style.opacity = '0';
    feedback.style.transform = 'translateY(20px)';
    
    // Create icon based on type
    const icon = document.createElement('i');
    switch (type) {
        case 'success':
            icon.className = 'fas fa-check-circle';
            icon.style.color = 'var(--success-color, #10b981)';
            break;
        case 'warning':
            icon.className = 'fas fa-exclamation-triangle';
            icon.style.color = 'var(--warning-color, #f59e0b)';
            break;
        case 'error':
            icon.className = 'fas fa-times-circle';
            icon.style.color = 'var(--danger-color, #ef4444)';
            break;
        default:
            icon.className = 'fas fa-info-circle';
            icon.style.color = 'var(--info-color, #3b82f6)';
    }
    
    icon.style.marginRight = '8px';
    feedback.appendChild(icon);
    
    // Add text
    const text = document.createTextNode(message);
    feedback.appendChild(text);
    
    // Add to container and animate in
    feedbackContainer.appendChild(feedback);
    
    // Trigger animation
    setTimeout(() => {
        feedback.style.opacity = '1';
        feedback.style.transform = 'translateY(0)';
    }, 10);
    
    // Remove after timeout
    setTimeout(() => {
        feedback.style.opacity = '0';
        feedback.style.transform = 'translateY(20px)';
        
        setTimeout(() => {
            if (feedback.parentNode === feedbackContainer) {
                feedbackContainer.removeChild(feedback);
            }
        }, 300);
    }, 3000);
}

// Initialize when DOM content is loaded
document.addEventListener('DOMContentLoaded', () => {
    console.log("AlphaWolf system initializing...");
    
    // Initialize UI components
    initVoiceControl();
    
    console.log("AlphaWolf system initialized");
});