/**
 * AlphaWolf Cognitive Enhancement Module
 * 
 * Provides client-side functionality for:
 * - Adaptive learning and self-improvement
 * - Voice mimicry and personalization
 * - Symbol-based communication
 * - AR navigation and reminder system
 */

// Main cognitive enhancement controller
const CognitiveEnhancement = {
    // Patient ID for the current user
    patientId: null,
    
    // Cognitive status and components
    status: null,
    activeComponents: {},
    
    // Initialize the cognitive enhancement features
    init: function(patientId) {
        this.patientId = patientId;
        
        // Initialize components if patient ID is provided
        if (patientId) {
            // Get current cognitive status
            this.fetchCognitiveStatus();
            
            // Initialize submodules
            VoiceMimicry.init(patientId);
            SymbolCommunication.init(patientId);
            ARNavigation.init(patientId);
            
            console.log('Cognitive Enhancement initialized for patient', patientId);
        }
    },
    
    // Fetch cognitive status for the patient
    fetchCognitiveStatus: function() {
        fetch(`/api/cognitive/status/${this.patientId}`)
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    this.status = data.status;
                    this.activeComponents = data.status.active_components;
                    
                    // Trigger status updated event
                    document.dispatchEvent(new CustomEvent('cognitive-status-updated', { 
                        detail: { status: this.status } 
                    }));
                    
                    console.log('Cognitive status loaded:', this.status);
                } else {
                    console.error('Failed to load cognitive status:', data.error);
                }
            })
            .catch(error => {
                console.error('Error fetching cognitive status:', error);
            });
    },
    
    // Process a patient interaction
    processInteraction: function(interactionData) {
        return fetch(`/api/cognitive/interact/${this.patientId}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(interactionData)
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Refresh cognitive status after interaction
                this.fetchCognitiveStatus();
                return data.result;
            } else {
                console.error('Interaction processing failed:', data.error);
                return null;
            }
        })
        .catch(error => {
            console.error('Error processing interaction:', error);
            return null;
        });
    },
    
    // Generate personalized content
    generateContent: function(contentType, parameters) {
        return fetch(`/api/cognitive/generate/${this.patientId}/${contentType}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(parameters)
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                return data[contentType];
            } else {
                console.error(`Content generation failed (${contentType}):`, data.error);
                return null;
            }
        })
        .catch(error => {
            console.error(`Error generating ${contentType}:`, error);
            return null;
        });
    },
    
    // Toggle a cognitive component
    toggleComponent: function(componentName, active) {
        return fetch(`/api/cognitive/component/${this.patientId}/${componentName}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ active: active })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                this.activeComponents = data.active_components;
                return true;
            } else {
                console.error(`Failed to toggle component ${componentName}:`, data.error);
                return false;
            }
        })
        .catch(error => {
            console.error(`Error toggling component ${componentName}:`, error);
            return false;
        });
    }
};

// Voice mimicry module
const VoiceMimicry = {
    patientId: null,
    voiceModel: null,
    
    init: function(patientId) {
        this.patientId = patientId;
        
        // Setup audio recording if microphone is available
        if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
            this.setupAudioRecording();
        }
        
        console.log('Voice Mimicry initialized for patient', patientId);
    },
    
    // Setup audio recording functionality
    setupAudioRecording: function() {
        // Audio context and recorder setup would go here
        this.audioContext = null;
        this.mediaRecorder = null;
        this.audioChunks = [];
        
        // Recording handlers will be set up when recording is started
    },
    
    // Start voice recording
    startRecording: function() {
        if (!navigator.mediaDevices) {
            console.error('Media devices not supported in this browser');
            return Promise.reject('Media devices not supported');
        }
        
        this.audioChunks = [];
        
        return navigator.mediaDevices.getUserMedia({ audio: true })
            .then(stream => {
                this.audioContext = new (window.AudioContext || window.webkitAudioContext)();
                this.mediaRecorder = new MediaRecorder(stream);
                
                this.mediaRecorder.ondataavailable = (event) => {
                    if (event.data.size > 0) {
                        this.audioChunks.push(event.data);
                    }
                };
                
                this.mediaRecorder.start();
                console.log('Voice recording started');
                
                // Trigger recording started event
                document.dispatchEvent(new CustomEvent('voice-recording-started'));
                
                return true;
            })
            .catch(error => {
                console.error('Error starting voice recording:', error);
                return false;
            });
    },
    
    // Stop voice recording
    stopRecording: function() {
        return new Promise((resolve, reject) => {
            if (!this.mediaRecorder) {
                reject('No active recording');
                return;
            }
            
            this.mediaRecorder.onstop = () => {
                const audioBlob = new Blob(this.audioChunks, { type: 'audio/wav' });
                const reader = new FileReader();
                
                reader.onloadend = () => {
                    const base64data = reader.result.split(',')[1];
                    resolve(base64data);
                    
                    // Trigger recording stopped event
                    document.dispatchEvent(new CustomEvent('voice-recording-stopped', {
                        detail: { audio: base64data }
                    }));
                };
                
                reader.readAsDataURL(audioBlob);
                
                // Close the stream tracks
                this.mediaRecorder.stream.getTracks().forEach(track => track.stop());
            };
            
            this.mediaRecorder.stop();
            console.log('Voice recording stopped');
        });
    },
    
    // Add a voice sample
    addVoiceSample: function(audioData, transcript) {
        return fetch(`/api/voice/${this.patientId}/sample`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                audio_data: audioData,
                transcript: transcript
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                console.log('Voice sample added successfully');
                return true;
            } else {
                console.error('Failed to add voice sample:', data.message);
                return false;
            }
        })
        .catch(error => {
            console.error('Error adding voice sample:', error);
            return false;
        });
    },
    
    // Generate speech using the patient's voice model
    generateSpeech: function(text, context) {
        return fetch(`/api/voice/${this.patientId}/generate`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                text: text,
                context: context
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                console.log('Speech generated successfully');
                
                // Play the generated speech
                this.playAudio(data.speech.url);
                
                return data.speech;
            } else {
                console.error('Failed to generate speech:', data.message);
                return null;
            }
        })
        .catch(error => {
            console.error('Error generating speech:', error);
            return null;
        });
    },
    
    // Play audio from URL
    playAudio: function(audioUrl) {
        const audio = new Audio(audioUrl);
        audio.play()
            .then(() => {
                console.log('Playing audio:', audioUrl);
            })
            .catch(error => {
                console.error('Error playing audio:', error);
            });
        
        return audio;
    }
};

// Symbol communication module
const SymbolCommunication = {
    patientId: null,
    symbolBoard: null,
    suggestedSymbols: null,
    
    init: function(patientId) {
        this.patientId = patientId;
        
        // Fetch the patient's symbol board
        this.fetchSymbolBoard();
        
        console.log('Symbol Communication initialized for patient', patientId);
    },
    
    // Fetch the patient's symbol board
    fetchSymbolBoard: function() {
        fetch(`/api/symbols/${this.patientId}`)
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    this.symbolBoard = data.board;
                    
                    // Trigger board loaded event
                    document.dispatchEvent(new CustomEvent('symbol-board-loaded', { 
                        detail: { board: this.symbolBoard } 
                    }));
                    
                    console.log('Symbol board loaded:', this.symbolBoard);
                } else {
                    console.log('No symbol board found, creating default');
                    this.createDefaultBoard();
                }
            })
            .catch(error => {
                console.error('Error fetching symbol board:', error);
            });
    },
    
    // Create a default symbol board
    createDefaultBoard: function() {
        fetch(`/api/symbols/${this.patientId}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                name: 'My Communication Board'
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                this.symbolBoard = data.board;
                
                // Trigger board created event
                document.dispatchEvent(new CustomEvent('symbol-board-created', { 
                    detail: { board: this.symbolBoard } 
                }));
                
                console.log('Default symbol board created:', this.symbolBoard);
            } else {
                console.error('Failed to create default symbol board:', data.message);
            }
        })
        .catch(error => {
            console.error('Error creating default symbol board:', error);
        });
    },
    
    // Get contextual symbol suggestions
    getSymbolSuggestions: function(timeOfDay, location) {
        let url = `/api/symbols/${this.patientId}/suggestions`;
        let params = new URLSearchParams();
        
        if (timeOfDay) params.append('time_of_day', timeOfDay);
        if (location) params.append('location', location);
        
        if (params.toString()) {
            url += '?' + params.toString();
        }
        
        fetch(url)
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    this.suggestedSymbols = data.suggestions;
                    
                    // Trigger suggestions loaded event
                    document.dispatchEvent(new CustomEvent('symbol-suggestions-loaded', { 
                        detail: { suggestions: this.suggestedSymbols } 
                    }));
                    
                    console.log('Symbol suggestions loaded:', this.suggestedSymbols);
                } else {
                    console.error('Failed to get symbol suggestions:', data.message);
                }
            })
            .catch(error => {
                console.error('Error getting symbol suggestions:', error);
            });
    },
    
    // Add a custom symbol
    addCustomSymbol: function(category, name, description, imageData) {
        return fetch(`/api/symbols/${this.patientId}/symbol`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                category: category,
                name: name,
                description: description,
                image_data: imageData
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                console.log('Custom symbol added successfully:', data.symbol);
                
                // Refresh the symbol board
                this.fetchSymbolBoard();
                
                return data.symbol;
            } else {
                console.error('Failed to add custom symbol:', data.message);
                return null;
            }
        })
        .catch(error => {
            console.error('Error adding custom symbol:', error);
            return null;
        });
    },
    
    // Record symbol usage
    recordSymbolUsage: function(symbolId, category) {
        // Process the interaction through the main cognitive module
        return CognitiveEnhancement.processInteraction({
            type: 'symbol_usage',
            symbol_id: symbolId,
            category: category
        });
    }
};

// AR navigation module
const ARNavigation = {
    patientId: null,
    layouts: null,
    
    init: function(patientId) {
        this.patientId = patientId;
        
        // Fetch available layouts
        this.fetchLayouts();
        
        console.log('AR Navigation initialized for patient', patientId);
    },
    
    // Fetch available layouts
    fetchLayouts: function() {
        fetch(`/api/navigation/${this.patientId}/layouts`)
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    this.layouts = data.layouts;
                    
                    // Trigger layouts loaded event
                    document.dispatchEvent(new CustomEvent('navigation-layouts-loaded', { 
                        detail: { layouts: this.layouts } 
                    }));
                    
                    console.log('Navigation layouts loaded:', this.layouts);
                } else {
                    console.error('Failed to load navigation layouts:', data.message);
                }
            })
            .catch(error => {
                console.error('Error fetching navigation layouts:', error);
            });
    },
    
    // Add a new location layout
    addLayout: function(name, layoutData, floorPlanImage) {
        return fetch(`/api/navigation/${this.patientId}/layout`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                name: name,
                rooms: layoutData.rooms || [],
                areas: layoutData.areas || [],
                landmarks: layoutData.landmarks || [],
                floor_plan_image: floorPlanImage
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                console.log('Layout added successfully:', data.layout);
                
                // Refresh layouts
                this.fetchLayouts();
                
                return data.layout;
            } else {
                console.error('Failed to add layout:', data.message);
                return null;
            }
        })
        .catch(error => {
            console.error('Error adding layout:', error);
            return null;
        });
    },
    
    // Generate navigation instructions
    getNavigationInstructions: function(layoutId, startName, endName, complexity) {
        return fetch(`/api/navigation/${this.patientId}/instructions`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                layout_id: layoutId,
                start_name: startName,
                end_name: endName,
                complexity: complexity || 'simple'
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                console.log('Navigation instructions generated:', data.instructions);
                
                // Trigger instructions generated event
                document.dispatchEvent(new CustomEvent('navigation-instructions-generated', { 
                    detail: { instructions: data.instructions } 
                }));
                
                return data.instructions;
            } else {
                console.error('Failed to generate navigation instructions:', data.message);
                return null;
            }
        })
        .catch(error => {
            console.error('Error generating navigation instructions:', error);
            return null;
        });
    }
};

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    // Get patient ID from page data if available
    const patientIdElement = document.getElementById('current-patient-id');
    if (patientIdElement) {
        const patientId = patientIdElement.value;
        CognitiveEnhancement.init(patientId);
    }
});