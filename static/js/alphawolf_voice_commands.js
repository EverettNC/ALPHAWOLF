/**
 * AlphaWolf Voice Commands System
 * Handles the processing of voice commands for AlphaWolf
 */

// Command handler for voice input
function handleVoiceCommand(transcript) {
    // Strip out the wake word and normalize the command
    const command = transcript.replace(/alpha|wolf|alphawolf/g, '').trim();
    
    console.log('Processing command:', command);
    
    // Display a notification that a command was recognized
    showNotification(`Command recognized: "${command}"`, 'info');
    
    // Check for navigation commands
    if (commandMatches(command, ['go to home', 'show home', 'home page'])) {
        navigateTo('/home');
    }
    else if (commandMatches(command, ['exercises', 'cognitive exercises', 'brain exercises', 'show exercises'])) {
        navigateTo('/cognitive_exercises');
    }
    else if (commandMatches(command, ['safety', 'safety zones', 'show safety', 'safe zones'])) {
        navigateTo('/safety_zones');
    }
    else if (commandMatches(command, ['reminders', 'show reminders', 'my reminders'])) {
        navigateTo('/reminders');
    }
    else if (commandMatches(command, ['memories', 'memory lane', 'show memories', 'photos'])) {
        navigateTo('/memory_lane');
    }
    else if (commandMatches(command, ['learning', 'learning corner', 'show learning'])) {
        navigateTo('/learning_corner');
    }
    else if (commandMatches(command, ['caregiver', 'caregiver tools', 'caregiver page'])) {
        navigateTo('/caregivers_page');
    }
    
    // Check for information commands
    else if (commandMatches(command, ['tell me about today', "what's today", 'today information'])) {
        fetchTodayInformation();
    }
    else if (commandMatches(command, ['schedule', "what's my schedule", 'my appointments', 'today events'])) {
        fetchScheduleInformation();
    }
    
    // Check for action commands
    else if (commandMatches(command, ['add reminder', 'new reminder', 'create reminder'])) {
        navigateTo('/add_reminder');
    }
    else if (commandMatches(command, ['start exercises', 'begin exercises', 'cognitive training'])) {
        startCognitiveExercises();
    }
    else if (commandMatches(command, ['call caregiver', 'contact caregiver', 'help me'])) {
        initiateCaregiver();
    }
    
    // Check for system commands
    else if (commandMatches(command, ['mute', 'stop listening', 'turn off voice'])) {
        if (voiceControlEnabled) {
            toggleVoiceControl(); // Function from voice_control.js
        }
    }
    else if (commandMatches(command, ['unmute', 'start listening', 'turn on voice'])) {
        if (!voiceControlEnabled) {
            toggleVoiceControl(); // Function from voice_control.js
        }
    }
    
    // Status commands
    else if (commandMatches(command, ['how am i doing', 'my status', 'cognitive status'])) {
        fetchCognitiveStatus();
    }
    else if (commandMatches(command, ['where am i', 'my location', 'current location'])) {
        checkCurrentLocation();
    }
    
    // No recognized command
    else {
        // Attempt a more general intent match
        const generalIntent = detectGeneralIntent(command);
        
        if (generalIntent) {
            handleGeneralIntent(generalIntent, command);
        } else {
            showNotification("I'm sorry, I didn't understand that command", 'warning');
            
            // Log unrecognized command for improvement
            console.log('Unrecognized command:', command);
        }
    }
}

/**
 * Check if the user's command matches any of the phrases
 */
function commandMatches(command, phrases) {
    return phrases.some(phrase => command.includes(phrase));
}

/**
 * Navigate to a specific URL
 */
function navigateTo(url) {
    showNotification(`Navigating to ${url}`, 'success');
    window.location.href = url;
}

/**
 * Fetch today's information
 */
function fetchTodayInformation() {
    showNotification("Here's what's happening today", 'info');
    
    // Get current date information
    const now = new Date();
    const dateString = now.toLocaleDateString('en-US', { 
        weekday: 'long', 
        year: 'numeric', 
        month: 'long', 
        day: 'numeric' 
    });
    
    // Create modal with today's information
    createInformationModal(
        "Today's Information",
        `
        <div class="mb-3">
            <h5 class="cyber-text">Today is ${dateString}</h5>
            <p>Current time: ${now.toLocaleTimeString()}</p>
        </div>
        <div class="mb-3">
            <h6><i class="fas fa-calendar-check me-2 text-info"></i>Today's Reminders</h6>
            <div class="list-group">
                <a href="#" class="list-group-item list-group-item-action bg-dark">
                    <div class="d-flex w-100 justify-content-between">
                        <h6 class="mb-1">Take morning medication</h6>
                        <small>8:00 AM</small>
                    </div>
                </a>
                <a href="#" class="list-group-item list-group-item-action bg-dark">
                    <div class="d-flex w-100 justify-content-between">
                        <h6 class="mb-1">Doctor's appointment</h6>
                        <small>2:30 PM</small>
                    </div>
                </a>
                <a href="#" class="list-group-item list-group-item-action bg-dark">
                    <div class="d-flex w-100 justify-content-between">
                        <h6 class="mb-1">Call Susan</h6>
                        <small>5:00 PM</small>
                    </div>
                </a>
            </div>
        </div>
        <div>
            <h6><i class="fas fa-brain me-2 text-info"></i>Cognitive Exercise Progress</h6>
            <div class="progress-wrapper mb-2">
                <div class="progress-bar" style="width: 65%"></div>
            </div>
            <p class="small text-muted">You've completed 65% of today's exercises</p>
        </div>
        `
    );
}

/**
 * Fetch schedule information
 */
function fetchScheduleInformation() {
    showNotification("Here's your schedule", 'info');
    
    // Create modal with schedule information
    createInformationModal(
        "Your Schedule",
        `
        <div class="mb-3">
            <h6><i class="fas fa-calendar-alt me-2 text-info"></i>Upcoming Events</h6>
            <div class="list-group">
                <a href="#" class="list-group-item list-group-item-action bg-dark">
                    <div class="d-flex w-100 justify-content-between">
                        <h6 class="mb-1">Doctor's appointment</h6>
                        <small>Today, 2:30 PM</small>
                    </div>
                    <p class="mb-1">Dr. Johnson - Regular checkup</p>
                    <small>123 Medical Center</small>
                </a>
                <a href="#" class="list-group-item list-group-item-action bg-dark">
                    <div class="d-flex w-100 justify-content-between">
                        <h6 class="mb-1">Family Visit</h6>
                        <small>Tomorrow, 11:00 AM</small>
                    </div>
                    <p class="mb-1">Susan and the grandkids</p>
                </a>
                <a href="#" class="list-group-item list-group-item-action bg-dark">
                    <div class="d-flex w-100 justify-content-between">
                        <h6 class="mb-1">Community Center - Art Class</h6>
                        <small>Wednesday, 3:00 PM</small>
                    </div>
                </a>
            </div>
        </div>
        `
    );
}

/**
 * Start cognitive exercises
 */
function startCognitiveExercises() {
    showNotification("Starting cognitive exercises", 'success');
    navigateTo('/cognitive_exercises');
}

/**
 * Initiate caregiver contact
 */
function initiateCaregiver() {
    showNotification("Contacting your caregiver", 'info');
    
    // Create modal with caregiver contact options
    createInformationModal(
        "Contact Caregiver",
        `
        <div class="d-flex align-items-center mb-4">
            <div class="me-3">
                <img src="https://via.placeholder.com/60" class="rounded-circle" alt="Caregiver">
            </div>
            <div>
                <h5 class="mb-1">Sarah Johnson</h5>
                <p class="mb-0 small">Primary Caregiver</p>
            </div>
            <div class="ms-auto">
                <span class="badge bg-success">
                    <i class="fas fa-circle me-1"></i>Online
                </span>
            </div>
        </div>
        <div class="row text-center">
            <div class="col-4">
                <a href="#" class="btn btn-outline-primary btn-lg w-100 mb-2">
                    <i class="fas fa-phone-alt"></i>
                </a>
                <div>Call</div>
            </div>
            <div class="col-4">
                <a href="#" class="btn btn-outline-info btn-lg w-100 mb-2">
                    <i class="fas fa-video"></i>
                </a>
                <div>Video</div>
            </div>
            <div class="col-4">
                <a href="#" class="btn btn-outline-success btn-lg w-100 mb-2">
                    <i class="fas fa-comment-alt"></i>
                </a>
                <div>Message</div>
            </div>
        </div>
        <div class="form-group mt-4">
            <label for="message" class="form-label">Quick Message:</label>
            <select class="form-select mb-3" id="message">
                <option>I need help</option>
                <option>Please call me</option>
                <option>I'm feeling confused</option>
                <option>Everything is fine, just checking in</option>
            </select>
            <button class="btn cyber-btn w-100">Send Message</button>
        </div>
        `
    );
}

/**
 * Fetch cognitive status information
 */
function fetchCognitiveStatus() {
    showNotification("Here's your cognitive status", 'info');
    
    // Create modal with cognitive status
    createInformationModal(
        "Cognitive Status",
        `
        <div class="mb-4">
            <h5 class="cyber-text mb-3">Your Cognitive Performance</h5>
            <div class="cognitive-metrics">
                <div class="metric-item">
                    <div class="metric-name">Memory</div>
                    <div class="metric-value">87%</div>
                    <div class="progress-wrapper">
                        <div class="progress-bar" style="width: 87%"></div>
                    </div>
                </div>
                <div class="metric-item">
                    <div class="metric-name">Attention</div>
                    <div class="metric-value">92%</div>
                    <div class="progress-wrapper">
                        <div class="progress-bar" style="width: 92%"></div>
                    </div>
                </div>
                <div class="metric-item">
                    <div class="metric-name">Language</div>
                    <div class="metric-value">78%</div>
                    <div class="progress-wrapper">
                        <div class="progress-bar" style="width: 78%"></div>
                    </div>
                </div>
                <div class="metric-item">
                    <div class="metric-name">Recognition</div>
                    <div class="metric-value">85%</div>
                    <div class="progress-wrapper">
                        <div class="progress-bar" style="width: 85%"></div>
                    </div>
                </div>
                <div class="metric-item">
                    <div class="metric-name">Problem Solving</div>
                    <div class="metric-value">73%</div>
                    <div class="progress-wrapper">
                        <div class="progress-bar" style="width: 73%"></div>
                    </div>
                </div>
            </div>
        </div>
        <div>
            <h6><i class="fas fa-chart-line me-2 text-info"></i>Weekly Progress</h6>
            <p>Your overall cognitive score has improved by 3% this week.</p>
            <div class="text-center mt-3">
                <a href="/cognitive_exercises" class="btn cyber-btn">Continue Training</a>
            </div>
        </div>
        `
    );
}

/**
 * Check current location
 */
function checkCurrentLocation() {
    showNotification("Checking your location", 'info');
    
    // Create modal with location information
    createInformationModal(
        "Your Location",
        `
        <div class="text-center mb-3">
            <i class="fas fa-map-marker-alt fa-3x text-danger mb-3"></i>
            <h5>You are currently at Home</h5>
            <p class="text-muted">Safe zone: Primary Residence</p>
        </div>
        <div class="bg-dark p-3 rounded mb-3">
            <div class="d-flex justify-content-between">
                <div>
                    <i class="fas fa-shield-alt text-success me-2"></i>Status:
                </div>
                <div class="text-success">
                    <strong>Safe</strong>
                </div>
            </div>
            <div class="d-flex justify-content-between mt-2">
                <div>
                    <i class="fas fa-map me-2"></i>Address:
                </div>
                <div>
                    123 Main Street
                </div>
            </div>
            <div class="d-flex justify-content-between mt-2">
                <div>
                    <i class="fas fa-clock me-2"></i>Time at location:
                </div>
                <div>
                    3 hours 42 minutes
                </div>
            </div>
        </div>
        <div class="text-center">
            <a href="/safety_zones" class="btn cyber-btn">View All Safe Zones</a>
        </div>
        `
    );
}

/**
 * Attempt to detect a general intent from the command
 */
function detectGeneralIntent(command) {
    // Intents for help
    if (command.includes('help') || command.includes('assist') || command.includes('support')) {
        return 'help';
    }
    
    // Intents for information about the system
    if (command.includes('what can you do') || command.includes('capabilities') || 
        command.includes('tell me about you') || command.includes('what are you')) {
        return 'system_info';
    }
    
    // Greeting intents
    if (command.includes('hello') || command.includes('hi there') || 
        command.includes('hey') || command.includes('greetings')) {
        return 'greeting';
    }
    
    // No recognized intent
    return null;
}

/**
 * Handle general intent commands
 */
function handleGeneralIntent(intent, command) {
    if (intent === 'help') {
        createInformationModal(
            "AlphaWolf Help",
            `
            <div class="mb-3">
                <h5 class="cyber-text">Voice Commands</h5>
                <p>You can say "Alpha" followed by any of these commands:</p>
                <ul class="list-group">
                    <li class="list-group-item bg-dark">
                        <i class="fas fa-home me-2 text-info"></i> "go to home" - Return to the home page
                    </li>
                    <li class="list-group-item bg-dark">
                        <i class="fas fa-brain me-2 text-info"></i> "exercises" - Access cognitive exercises
                    </li>
                    <li class="list-group-item bg-dark">
                        <i class="fas fa-map-marked-alt me-2 text-info"></i> "safety zones" - Manage safety settings
                    </li>
                    <li class="list-group-item bg-dark">
                        <i class="fas fa-calendar-alt me-2 text-info"></i> "reminders" - View your reminders
                    </li>
                    <li class="list-group-item bg-dark">
                        <i class="fas fa-info-circle me-2 text-info"></i> "tell me about today" - Get today's information
                    </li>
                    <li class="list-group-item bg-dark">
                        <i class="fas fa-phone-alt me-2 text-info"></i> "call caregiver" - Contact your caregiver
                    </li>
                </ul>
            </div>
            <div class="text-center">
                <a href="/voice_control_help" class="btn cyber-btn">View All Commands</a>
            </div>
            `
        );
    }
    else if (intent === 'system_info') {
        createInformationModal(
            "About AlphaWolf",
            `
            <div class="text-center mb-4">
                <i class="fas fa-brain fa-4x text-info mb-3"></i>
                <h4 class="cyber-text">AlphaWolf AI Assistant</h4>
                <p>Version 1.0</p>
            </div>
            <p>AlphaWolf is an AI-powered cognitive care system designed to support individuals with Alzheimer's and dementia. I can help with:</p>
            <ul class="list-group mb-3">
                <li class="list-group-item bg-dark">
                    <i class="fas fa-brain me-2 text-info"></i> Cognitive enhancement exercises
                </li>
                <li class="list-group-item bg-dark">
                    <i class="fas fa-shield-alt me-2 text-info"></i> Safety monitoring and alerts
                </li>
                <li class="list-group-item bg-dark">
                    <i class="fas fa-calendar-check me-2 text-info"></i> Reminders and schedule management
                </li>
                <li class="list-group-item bg-dark">
                    <i class="fas fa-photo-video me-2 text-info"></i> Memory preservation and recall
                </li>
                <li class="list-group-item bg-dark">
                    <i class="fas fa-hands-helping me-2 text-info"></i> Caregiver support and coordination
                </li>
            </ul>
            <p class="text-center font-italic">"HOW CAN I HELP YOU LOVE YOURSELF MORE"</p>
            `
        );
    }
    else if (intent === 'greeting') {
        // Get current time to provide appropriate greeting
        const hour = new Date().getHours();
        let greeting = "Hello";
        
        if (hour < 12) {
            greeting = "Good morning";
        } else if (hour < 18) {
            greeting = "Good afternoon";
        } else {
            greeting = "Good evening";
        }
        
        showNotification(`${greeting}! How can I help you today?`, 'success');
    }
}

/**
 * Create an information modal
 */
function createInformationModal(title, content) {
    // Remove any existing modals
    const existingModal = document.getElementById('information-modal');
    if (existingModal) {
        existingModal.remove();
    }
    
    // Create modal elements
    const modalDiv = document.createElement('div');
    modalDiv.id = 'information-modal';
    modalDiv.className = 'modal fade';
    modalDiv.tabIndex = -1;
    modalDiv.setAttribute('aria-labelledby', 'information-modal-label');
    modalDiv.setAttribute('aria-hidden', 'true');
    
    modalDiv.innerHTML = `
        <div class="modal-dialog modal-dialog-centered">
            <div class="modal-content bg-dark border-0">
                <div class="modal-header border-bottom border-secondary">
                    <h5 class="modal-title" id="information-modal-label">${title}</h5>
                    <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal" aria-label="Close"></button>
                </div>
                <div class="modal-body">
                    ${content}
                </div>
                <div class="modal-footer border-top border-secondary">
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
                </div>
            </div>
        </div>
    `;
    
    // Add modal to body
    document.body.appendChild(modalDiv);
    
    // Create and show Bootstrap modal
    const modal = new bootstrap.Modal(modalDiv);
    modal.show();
    
    // Clean up when modal is hidden
    modalDiv.addEventListener('hidden.bs.modal', function () {
        modalDiv.remove();
    });
}