/**
 * AlphaWolf Voice Control System
 * Provides hands-free voice interaction capabilities
 */

class VoiceControl {
    constructor(options = {}) {
        // Configuration options
        this.options = {
            commandPrefix: 'alpha', // Wake word/prefix for commands
            debug: false,
            autoStart: false,
            continuousListening: true,
            language: 'en-US',
            ...options
        };

        // Command registry
        this.commands = {};
        
        // Speech recognition setup
        this.recognition = null;
        this.isListening = false;
        this.isSpeaking = false;
        this.lastResult = null;
        this.isMuted = false; // Track muted state
        
        // Speech synthesis setup
        this.speechSynthesis = window.speechSynthesis;
        this.voices = [];
        
        // DOM elements for UI feedback
        this.statusElement = null;
        this.feedbackElement = null;
        
        // Initialize the system
        this.init();
    }
    
    /**
     * Initialize the voice control system
     */
    init() {
        // Check browser support
        if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
            console.error('Speech recognition not supported in this browser.');
            return;
        }
        
        // Initialize speech recognition
        this.recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
        this.recognition.continuous = this.options.continuousListening;
        this.recognition.interimResults = false;
        this.recognition.lang = this.options.language;
        
        // Check localStorage for saved mute state
        const savedMuteState = localStorage.getItem('alphaVoiceControlMuted');
        if (savedMuteState !== null) {
            this.isMuted = savedMuteState === 'true';
            if (this.options.debug) {
                console.log('Loaded saved mute state:', this.isMuted);
            }
        }
        
        // Setup recognition event handlers
        this.setupRecognitionEvents();
        
        // Load available voices
        this.loadVoices();
        
        // Auto-start if configured and not muted
        if (this.options.autoStart && !this.isMuted) {
            this.start();
        }
        
        // Setup UI feedback elements
        this.createFeedbackElements();
        
        if (this.options.debug) {
            console.log('Voice control system initialized');
        }
    }
    
    /**
     * Set up event listeners for speech recognition
     */
    setupRecognitionEvents() {
        // Result event
        this.recognition.onresult = (event) => {
            const transcript = event.results[event.results.length - 1][0].transcript.trim().toLowerCase();
            this.lastResult = transcript;
            
            if (this.options.debug) {
                console.log('Speech recognized:', transcript);
            }
            
            this.updateFeedback('heard', transcript);
            
            // Process command if it starts with the command prefix
            if (transcript.startsWith(this.options.commandPrefix)) {
                const commandText = transcript.substring(this.options.commandPrefix.length).trim();
                this.processCommand(commandText);
            }
        };
        
        // Error event
        this.recognition.onerror = (event) => {
            if (this.options.debug) {
                console.error('Recognition error:', event.error);
            }
            this.updateFeedback('error', `Error: ${event.error}`);
            
            // Restart recognition if it's a recoverable error
            if (event.error !== 'aborted' && this.isListening) {
                setTimeout(() => this.restart(), 1000);
            }
        };
        
        // End event
        this.recognition.onend = () => {
            if (this.options.debug) {
                console.log('Recognition ended');
            }
            
            this.isListening = false;
            this.updateStatus();
            
            // Restart recognition if continuous listening is enabled and not muted
            if (this.options.continuousListening && !this.isSpeaking && !this.isMuted) {
                this.restart();
            }
        };
        
        // Start event
        this.recognition.onstart = () => {
            if (this.options.debug) {
                console.log('Recognition started');
            }
            this.isListening = true;
            this.updateStatus();
        };
    }
    
    /**
     * Load available voices for speech synthesis
     */
    loadVoices() {
        // Get voices immediately if available
        this.voices = this.speechSynthesis.getVoices();
        
        // Or wait for them to load
        if (this.speechSynthesis.onvoiceschanged !== undefined) {
            this.speechSynthesis.onvoiceschanged = () => {
                this.voices = this.speechSynthesis.getVoices();
                if (this.options.debug) {
                    console.log('Voices loaded:', this.voices.length);
                }
            };
        }
    }
    
    /**
     * Create UI elements for feedback
     */
    createFeedbackElements() {
        // Create status element if it doesn't exist
        if (!document.getElementById('voice-control-status')) {
            this.statusElement = document.createElement('div');
            this.statusElement.id = 'voice-control-status';
            this.statusElement.className = 'voice-control-status';
            document.body.appendChild(this.statusElement);
        } else {
            this.statusElement = document.getElementById('voice-control-status');
        }
        
        // Create feedback element if it doesn't exist
        if (!document.getElementById('voice-control-feedback')) {
            this.feedbackElement = document.createElement('div');
            this.feedbackElement.id = 'voice-control-feedback';
            this.feedbackElement.className = 'voice-control-feedback';
            document.body.appendChild(this.feedbackElement);
        } else {
            this.feedbackElement = document.getElementById('voice-control-feedback');
        }
        
        // Initial status update
        this.updateStatus();
    }
    
    /**
     * Update the status indicator
     */
    updateStatus() {
        if (!this.statusElement) return;
        
        if (this.isMuted) {
            this.statusElement.innerHTML = '<i class="fas fa-microphone-slash"></i> Microphone Muted';
            this.statusElement.classList.add('muted');
            this.statusElement.classList.remove('listening');
        } else if (this.isListening) {
            this.statusElement.innerHTML = '<span class="pulse"></span> Listening...';
            this.statusElement.classList.add('listening');
            this.statusElement.classList.remove('muted');
        } else {
            this.statusElement.innerHTML = 'Voice Control';
            this.statusElement.classList.remove('listening');
            this.statusElement.classList.remove('muted');
        }
    }
    
    /**
     * Update feedback display
     */
    updateFeedback(type, text) {
        if (!this.feedbackElement) return;
        
        // Clear previous feedback
        clearTimeout(this.feedbackTimeout);
        
        // Update with new feedback
        this.feedbackElement.textContent = text;
        this.feedbackElement.className = 'voice-control-feedback';
        this.feedbackElement.classList.add(`feedback-${type}`);
        this.feedbackElement.style.display = 'block';
        
        // Auto-hide feedback after a delay
        this.feedbackTimeout = setTimeout(() => {
            this.feedbackElement.style.display = 'none';
        }, 5000);
    }
    
    /**
     * Start voice recognition
     */
    start() {
        if (this.isListening || this.isMuted) return;
        
        try {
            this.recognition.start();
            if (this.options.debug) {
                console.log('Starting voice recognition');
            }
        } catch (error) {
            console.error('Error starting recognition:', error);
            // If it fails because it's already running, restart it
            if (error.name === 'InvalidStateError') {
                this.stop();
                setTimeout(() => this.start(), 500);
            }
        }
    }
    
    /**
     * Stop voice recognition
     */
    stop() {
        if (!this.isListening) return;
        
        try {
            this.recognition.stop();
            if (this.options.debug) {
                console.log('Stopping voice recognition');
            }
        } catch (error) {
            console.error('Error stopping recognition:', error);
        }
    }
    
    /**
     * Restart voice recognition
     */
    restart() {
        if (this.isMuted) return; // Don't restart if muted
        
        this.stop();
        setTimeout(() => this.start(), 200);
    }
    
    /**
     * Register a voice command
     * @param {string} command - The command phrase to listen for
     * @param {function} callback - The function to execute when command is recognized
     */
    registerCommand(command, callback) {
        // Convert command to lowercase for case-insensitive matching
        command = command.toLowerCase();
        
        if (this.options.debug) {
            console.log(`Registering command: ${command}`);
        }
        
        this.commands[command] = callback;
    }
    
    /**
     * Process a recognized command
     * @param {string} commandText - The command text to process
     */
    processCommand(commandText) {
        if (this.options.debug) {
            console.log(`Processing command: ${commandText}`);
        }
        
        this.updateFeedback('command', `Command: ${commandText}`);
        
        // Check for exact command matches
        if (this.commands[commandText]) {
            this.commands[commandText]();
            return;
        }
        
        // Check for partial command matches (simple intent matching)
        for (const cmd in this.commands) {
            if (commandText.includes(cmd)) {
                this.commands[cmd]();
                return;
            }
        }
        
        // No command match found
        this.speak("I'm sorry, I didn't understand that command.");
    }
    
    /**
     * Speak text using speech synthesis
     * @param {string} text - The text to speak
     * @param {object} options - Options for speech (voice, rate, pitch, etc.)
     */
    speak(text, options = {}) {
        if (!this.speechSynthesis) return;
        
        // Stop listening while speaking to prevent feedback loops
        this.isSpeaking = true;
        this.stop();
        
        const utterance = new SpeechSynthesisUtterance(text);
        
        // Apply options
        if (options.voice) {
            const voice = this.findVoice(options.voice);
            if (voice) utterance.voice = voice;
        }
        
        utterance.rate = options.rate || 1;
        utterance.pitch = options.pitch || 1;
        utterance.volume = options.volume || 1;
        
        // Event handlers
        utterance.onstart = () => {
            if (this.options.debug) {
                console.log('Speaking:', text);
            }
            this.updateFeedback('speaking', `Speaking: ${text}`);
        };
        
        utterance.onend = () => {
            if (this.options.debug) {
                console.log('Done speaking');
            }
            this.isSpeaking = false;
            
            // Resume listening after speaking if not muted
            if (this.options.continuousListening && !this.isMuted) {
                setTimeout(() => this.start(), 500);
            }
        };
        
        utterance.onerror = (event) => {
            console.error('Speech synthesis error:', event);
            this.isSpeaking = false;
            
            // Resume listening after error if not muted
            if (this.options.continuousListening && !this.isMuted) {
                setTimeout(() => this.start(), 500);
            }
        };
        
        // Speak the text
        this.speechSynthesis.speak(utterance);
    }
    
    /**
     * Find a voice by name or language
     * @param {string} criteria - The voice name or language to search for
     * @returns {SpeechSynthesisVoice|null} - The matching voice or null
     */
    findVoice(criteria) {
        criteria = criteria.toLowerCase();
        
        // First try to find by name
        let voice = this.voices.find(v => 
            v.name.toLowerCase().includes(criteria)
        );
        
        // If not found, try by language
        if (!voice) {
            voice = this.voices.find(v => 
                v.lang.toLowerCase().includes(criteria)
            );
        }
        
        return voice || null;
    }
    
    /**
     * Toggle voice recognition on/off
     */
    toggle() {
        if (this.isListening) {
            this.stop();
        } else {
            this.start();
        }
    }
    
    /**
     * Mute the microphone
     */
    mute() {
        if (!this.isMuted) {
            this.isMuted = true;
            this.stop();
            this.updateFeedback('muted', 'Microphone muted');
            
            // Save mute state to localStorage
            localStorage.setItem('alphaVoiceControlMuted', 'true');
            
            if (this.options.debug) {
                console.log('Microphone muted');
            }
            
            // Update status indicator
            if (this.statusElement) {
                this.statusElement.innerHTML = '<i class="fas fa-microphone-slash"></i> Microphone Muted';
                this.statusElement.classList.add('muted');
                this.statusElement.classList.remove('listening');
            }
            
            this.speak("Microphone muted. Voice commands will not be recognized until unmuted.");
        }
    }
    
    /**
     * Unmute the microphone
     */
    unmute() {
        if (this.isMuted) {
            this.isMuted = false;
            
            // Save mute state to localStorage
            localStorage.setItem('alphaVoiceControlMuted', 'false');
            
            if (this.options.debug) {
                console.log('Microphone unmuted');
            }
            this.updateFeedback('unmuted', 'Microphone active');
            
            // Update status indicator
            if (this.statusElement) {
                this.statusElement.classList.remove('muted');
            }
            
            this.speak("Microphone activated. I'm now listening for voice commands.");
            
            // Restart listening after a delay to avoid feedback loops
            setTimeout(() => {
                if (this.options.continuousListening) {
                    this.start();
                }
            }, 1000);
        }
    }
    
    /**
     * Toggle mute state
     */
    toggleMute() {
        if (this.isMuted) {
            this.unmute();
        } else {
            this.mute();
        }
    }
}

// Create a global instance
const alphaVoiceControl = new VoiceControl({
    commandPrefix: 'alpha',
    debug: true,
    autoStart: false,
    continuousListening: true
});

// Export the instance
window.alphaVoiceControl = alphaVoiceControl;