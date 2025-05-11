/**
 * AlphaWolf - LumaCognify AI
 * Part of The Christman AI Project
 * 
 * VOICE RECOGNITION MODULE
 * Handles speech recognition with fallback options and permissions handling
 */

class AlphaWolfVoiceRecognition {
    constructor(options = {}) {
        // Configuration
        this.options = Object.assign({
            lang: 'en-US',
            continuous: false,
            interimResults: false,
            maxAlternatives: 1,
            wakeWord: 'alpha',
            onResult: null,
            onStart: null,
            onEnd: null,
            onError: null,
            onStatusChange: null,
            autoRestart: true,
            logLevel: 'info' // 'debug', 'info', 'warn', 'error', or 'none'
        }, options);

        // State
        this.isListening = false;
        this.hasPermission = null; // null = unknown, true = granted, false = denied
        this.errorCount = 0;
        this.recognitionSupported = this.checkRecognitionSupport();
        this.recognition = null;
        this.statusElement = document.getElementById(this.options.statusElementId || 'voice-status');
        
        this.log('Voice recognition module initialized');
        
        // If recognition is supported, initialize it
        if (this.recognitionSupported) {
            this.initRecognition();
        } else {
            this.log('Speech recognition not supported in this browser', 'warn');
            this.updateStatus('Speech recognition not supported in this browser');
        }
    }

    /**
     * Check if speech recognition is supported in the current browser
     */
    checkRecognitionSupport() {
        return !!(window.SpeechRecognition || window.webkitSpeechRecognition || 
                window.mozSpeechRecognition || window.msSpeechRecognition);
    }

    /**
     * Initialize the speech recognition object
     */
    initRecognition() {
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition ||
                                window.mozSpeechRecognition || window.msSpeechRecognition;
        
        if (!SpeechRecognition) {
            this.log('Speech Recognition API not available', 'error');
            return false;
        }
        
        this.recognition = new SpeechRecognition();
        this.recognition.lang = this.options.lang;
        this.recognition.continuous = this.options.continuous;
        this.recognition.interimResults = this.options.interimResults;
        this.recognition.maxAlternatives = this.options.maxAlternatives;
        
        // Set up event handlers
        this.recognition.onstart = this.handleStart.bind(this);
        this.recognition.onresult = this.handleResult.bind(this);
        this.recognition.onerror = this.handleError.bind(this);
        this.recognition.onend = this.handleEnd.bind(this);
        
        this.log('Speech recognition initialized');
        return true;
    }

    /**
     * Start listening for voice commands
     */
    start() {
        if (!this.recognitionSupported) {
            this.log('Cannot start: Speech recognition not supported', 'warn');
            return false;
        }
        
        if (this.isListening) {
            this.log('Already listening', 'warn');
            return true;
        }
        
        try {
            // If we don't know permission status yet, request it first
            if (this.hasPermission === null) {
                this.requestMicrophonePermission()
                    .then(granted => {
                        if (granted) {
                            this.startRecognition();
                        } else {
                            this.log('Microphone permission denied', 'error');
                            this.updateStatus('Microphone access denied. Please enable microphone access for this site.');
                        }
                    });
            } else if (this.hasPermission === true) {
                this.startRecognition();
            } else {
                this.log('Cannot start: Microphone permission denied', 'error');
                this.updateStatus('Microphone access denied. Please enable microphone access for this site.');
            }
            
            return true;
        } catch (err) {
            this.log('Error starting voice recognition: ' + err.message, 'error');
            return false;
        }
    }

    /**
     * Actually start the recognition after permissions are granted
     */
    startRecognition() {
        try {
            this.recognition.start();
            this.log('Voice recognition started');
            return true;
        } catch (err) {
            this.log('Error in startRecognition: ' + err.message, 'error');
            return false;
        }
    }

    /**
     * Stop listening for voice commands
     */
    stop() {
        if (!this.isListening) {
            this.log('Not currently listening', 'warn');
            return false;
        }
        
        try {
            this.recognition.stop();
            this.log('Voice recognition stopped');
            return true;
        } catch (err) {
            this.log('Error stopping voice recognition: ' + err.message, 'error');
            return false;
        }
    }

    /**
     * Request microphone permission explicitly
     */
    async requestMicrophonePermission() {
        try {
            // The most reliable way to ensure microphone permission is to actually request the audio stream
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            
            // Stop all audio tracks
            stream.getTracks().forEach(track => track.stop());
            
            this.hasPermission = true;
            this.log('Microphone permission granted');
            return true;
        } catch (err) {
            this.hasPermission = false;
            this.log('Microphone permission error: ' + err.message, 'error');
            return false;
        }
    }

    /**
     * Handle speech recognition start event
     */
    handleStart(event) {
        this.isListening = true;
        this.updateStatus('Listening...');
        
        if (typeof this.options.onStart === 'function') {
            this.options.onStart(event);
        }
    }

    /**
     * Handle speech recognition result event
     */
    handleResult(event) {
        const last = event.results.length - 1;
        const transcript = event.results[last][0].transcript.trim().toLowerCase();
        
        this.log('Recognized: ' + transcript, 'debug');
        
        // Check for wake word if configured
        if (this.options.wakeWord && !transcript.includes(this.options.wakeWord)) {
            return;
        }
        
        // Process the command (remove wake word if present)
        let command = transcript;
        if (this.options.wakeWord) {
            command = transcript.replace(new RegExp(this.options.wakeWord + '[,\\s]*', 'i'), '').trim();
        }
        
        this.updateStatus('Understood: ' + command);
        
        if (typeof this.options.onResult === 'function') {
            this.options.onResult(command, event);
        }
    }

    /**
     * Handle speech recognition error event
     */
    handleError(event) {
        this.isListening = false;
        this.errorCount++;
        
        let errorMessage = 'Speech recognition error';
        
        switch (event.error) {
            case 'not-allowed':
                this.hasPermission = false;
                errorMessage = 'Microphone access denied. Please enable microphone access for this site.';
                break;
            case 'no-speech':
                errorMessage = 'No speech detected';
                break;
            case 'audio-capture':
                errorMessage = 'No microphone detected';
                break;
            case 'network':
                errorMessage = 'Network error occurred';
                break;
            case 'aborted':
                errorMessage = 'Recognition aborted';
                break;
            case 'service-not-allowed':
                errorMessage = 'Speech service not allowed';
                break;
            default:
                errorMessage = 'Speech recognition error: ' + event.error;
        }
        
        this.log('Speech recognition error: ' + event.error, 'error');
        this.updateStatus(errorMessage);
        
        if (typeof this.options.onError === 'function') {
            this.options.onError(event);
        }
        
        // If permission was denied, show instructions to enable it
        if (event.error === 'not-allowed') {
            this.showPermissionInstructions();
        }
    }

    /**
     * Handle speech recognition end event
     */
    handleEnd(event) {
        this.isListening = false;
        this.updateStatus('Voice recognition inactive');
        
        this.log('Voice recognition ended');
        
        if (typeof this.options.onEnd === 'function') {
            this.options.onEnd(event);
        }
        
        // Auto-restart if configured and we don't have too many errors
        if (this.options.autoRestart && this.hasPermission !== false && this.errorCount < 5) {
            // Reset error count after successful recognition
            if (this.errorCount === 0) {
                setTimeout(() => this.start(), 500);
            } else {
                // Add increasing delay based on error count
                setTimeout(() => this.start(), 1000 * this.errorCount);
            }
        } else if (this.errorCount >= 5) {
            this.log('Too many errors, auto-restart disabled', 'warn');
            this.updateStatus('Voice recognition stopped due to too many errors');
        }
    }

    /**
     * Show instructions for enabling microphone permission
     */
    showPermissionInstructions() {
        const permissionsDiv = document.createElement('div');
        permissionsDiv.className = 'microphone-permissions';
        permissionsDiv.innerHTML = `
            <div class="permissions-container">
                <h3>Microphone Access Required</h3>
                <p>AlphaWolf needs microphone access to enable voice commands.</p>
                <p>Please follow these steps:</p>
                <ol>
                    <li>Click the lock/info icon in your browser's address bar</li>
                    <li>Find "Microphone" in the permissions list</li>
                    <li>Change the setting to "Allow" or "Enable"</li>
                    <li>Refresh this page</li>
                </ol>
                <button id="retry-mic-permission" class="btn btn-primary">Try Again</button>
                <button id="dismiss-mic-instructions" class="btn btn-secondary">Dismiss</button>
            </div>
        `;
        
        document.body.appendChild(permissionsDiv);
        
        // Add event listeners
        document.getElementById('retry-mic-permission').addEventListener('click', () => {
            document.body.removeChild(permissionsDiv);
            this.hasPermission = null; // Reset permission status
            this.requestMicrophonePermission().then(granted => {
                if (granted) {
                    this.errorCount = 0;
                    this.start();
                }
            });
        });
        
        document.getElementById('dismiss-mic-instructions').addEventListener('click', () => {
            document.body.removeChild(permissionsDiv);
        });
    }

    /**
     * Update the status display
     */
    updateStatus(message) {
        if (this.statusElement) {
            this.statusElement.textContent = message;
        }
        
        if (typeof this.options.onStatusChange === 'function') {
            this.options.onStatusChange(message);
        }
    }

    /**
     * Log a message to the console
     */
    log(message, level = 'info') {
        if (this.options.logLevel === 'none') return;
        
        // Check if this log level should be shown
        const levels = { debug: 0, info: 1, warn: 2, error: 3 };
        const configLevel = levels[this.options.logLevel] || 1;
        const messageLevel = levels[level] || 1;
        
        if (messageLevel < configLevel) return;
        
        switch (level) {
            case 'debug':
                console.debug(message);
                break;
            case 'info':
                console.log(message);
                break;
            case 'warn':
                console.warn(message);
                break;
            case 'error':
                console.error(message);
                break;
            default:
                console.log(message);
        }
    }
}

// Initialize voice recognition when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Create global instance
    window.alphaWolfVoice = new AlphaWolfVoiceRecognition({
        wakeWord: 'alpha',
        onResult: function(command, event) {
            // Send command to backend or process it here
            console.log('Processing command: ' + command);
            
            // Example of sending to backend
            fetch('/process_voice_command', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ command: command }),
            })
            .then(response => response.json())
            .then(data => {
                console.log('Command processed:', data);
                // Handle response from backend
                if (data.response) {
                    speak(data.response);
                }
            })
            .catch(error => {
                console.error('Error processing command:', error);
            });
        },
        onError: function(event) {
            console.error('Speech recognition error:', event.error);
        },
        statusElementId: 'voice-status'
    });
    
    // Start voice recognition
    setTimeout(function() {
        window.alphaWolfVoice.start();
    }, 1000);
    
    // Add voice control button if it exists
    const voiceButton = document.getElementById('voice-control-button');
    if (voiceButton) {
        voiceButton.addEventListener('click', function() {
            if (window.alphaWolfVoice.isListening) {
                window.alphaWolfVoice.stop();
            } else {
                window.alphaWolfVoice.start();
            }
        });
    }
});

// Simple text-to-speech function
function speak(text) {
    if ('speechSynthesis' in window) {
        const utterance = new SpeechSynthesisUtterance(text);
        utterance.lang = 'en-US';
        speechSynthesis.speak(utterance);
    } else {
        console.warn('Text-to-speech not supported in this browser');
    }
}