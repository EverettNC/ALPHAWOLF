/**
 * AlphaWolf Voice Commands
 * Implements specific voice commands for the AlphaWolf platform
 */

document.addEventListener('DOMContentLoaded', function() {
    // Check if voice control is available
    if (!window.alphaVoiceControl) {
        console.error('Voice control module not found');
        return;
    }
    
    const voiceControl = window.alphaVoiceControl;
    
    // Create help panel for voice commands
    createCommandsHelpPanel();
    
    // Register navigation commands
    registerNavigationCommands();
    
    // Register feature-specific commands
    registerFeatureCommands();
    
    // Register accessibility commands
    registerAccessibilityCommands();
    
    // Register global commands
    registerGlobalCommands();
    
    // Create toggle button
    createVoiceControlToggle();
    
    // Initialize with welcome message
    setTimeout(() => {
        voiceControl.speak("Voice control is ready. Say 'Alpha help' for available commands.");
    }, 1000);
});

/**
 * Create commands help panel
 */
function createCommandsHelpPanel() {
    const helpPanel = document.createElement('div');
    helpPanel.className = 'voice-commands-help';
    helpPanel.id = 'voice-commands-help';
    helpPanel.innerHTML = `
        <button class="close-help" id="close-voice-help">&times;</button>
        <h3>Voice Commands</h3>
        <p>All commands start with "Alpha" followed by:</p>
        <h4>Navigation</h4>
        <ul>
            <li><span class="command-phrase">go home</span> - <span class="command-description">Go to the home page</span></li>
            <li><span class="command-phrase">go to [page name]</span> - <span class="command-description">Navigate to a specific page</span></li>
            <li><span class="command-phrase">go back</span> - <span class="command-description">Go back to the previous page</span></li>
        </ul>
        
        <h4>Content Control</h4>
        <ul>
            <li><span class="command-phrase">scroll down</span> - <span class="command-description">Scroll down the page</span></li>
            <li><span class="command-phrase">scroll up</span> - <span class="command-description">Scroll up the page</span></li>
            <li><span class="command-phrase">scroll to top</span> - <span class="command-description">Scroll to the top of the page</span></li>
            <li><span class="command-phrase">scroll to bottom</span> - <span class="command-description">Scroll to the bottom of the page</span></li>
        </ul>
        
        <h4>Memory Lane</h4>
        <ul>
            <li><span class="command-phrase">show albums</span> - <span class="command-description">Show memory albums</span></li>
            <li><span class="command-phrase">show timeline</span> - <span class="command-description">Show life timeline</span></li>
            <li><span class="command-phrase">play music memories</span> - <span class="command-description">Go to music memories section</span></li>
        </ul>
        
        <h4>Learning Corner</h4>
        <ul>
            <li><span class="command-phrase">show research</span> - <span class="command-description">Show latest research</span></li>
            <li><span class="command-phrase">show daily tip</span> - <span class="command-description">Show daily tip</span></li>
            <li><span class="command-phrase">show resources</span> - <span class="command-description">Show learning resources</span></li>
        </ul>
        
        <h4>Caregiver Page</h4>
        <ul>
            <li><span class="command-phrase">show patient status</span> - <span class="command-description">Show patient overview</span></li>
            <li><span class="command-phrase">show care plan</span> - <span class="command-description">Show daily care plan</span></li>
            <li><span class="command-phrase">show medications</span> - <span class="command-description">Show medication schedule</span></li>
        </ul>
        
        <h4>General</h4>
        <ul>
            <li><span class="command-phrase">help</span> - <span class="command-description">Show this help panel</span></li>
            <li><span class="command-phrase">stop listening</span> - <span class="command-description">Turn off voice control</span></li>
            <li><span class="command-phrase">start listening</span> - <span class="command-description">Turn on voice control</span></li>
            <li><span class="command-phrase">mute microphone</span> - <span class="command-description">Mute the microphone (won't listen until unmuted)</span></li>
            <li><span class="command-phrase">unmute microphone</span> - <span class="command-description">Unmute the microphone</span></li>
            <li><span class="command-phrase">read page</span> - <span class="command-description">Read the current page content</span></li>
        </ul>
    `;
    document.body.appendChild(helpPanel);
    
    // Add event listener to close button
    document.getElementById('close-voice-help').addEventListener('click', function() {
        document.getElementById('voice-commands-help').style.display = 'none';
    });
}

/**
 * Create voice control toggle button
 */
function createVoiceControlToggle() {
    const toggleButton = document.createElement('button');
    toggleButton.className = 'voice-control-toggle';
    toggleButton.id = 'voice-control-toggle';
    toggleButton.innerHTML = '<i class="fas fa-microphone"></i>';
    toggleButton.title = 'Toggle Voice Control';
    document.body.appendChild(toggleButton);
    
    // Add event listener
    toggleButton.addEventListener('click', function() {
        const voiceControl = window.alphaVoiceControl;
        
        // If already muted, unmute on click
        if (voiceControl.isMuted) {
            voiceControl.unmute();
            this.classList.remove('muted');
            this.classList.add('active');
            this.innerHTML = '<i class="fas fa-microphone"></i>';
        } 
        // If active, mute on click
        else if (this.classList.contains('active')) {
            voiceControl.mute();
            this.classList.remove('active');
            this.classList.add('muted');
            this.innerHTML = '<i class="fas fa-microphone-slash"></i>';
        } 
        // If inactive but not muted, activate
        else {
            voiceControl.toggle();
            this.classList.toggle('active');
        }
    });
}

/**
 * Register navigation commands
 */
function registerNavigationCommands() {
    const voiceControl = window.alphaVoiceControl;
    
    // Home command
    voiceControl.registerCommand('go home', function() {
        voiceControl.speak("Going to home page");
        window.location.href = '/home';
    });
    
    // Go back command
    voiceControl.registerCommand('go back', function() {
        voiceControl.speak("Going back");
        window.history.back();
    });
    
    // Go to specific page commands
    voiceControl.registerCommand('go to learning corner', function() {
        voiceControl.speak("Going to learning corner");
        window.location.href = '/learning-corner';
    });
    
    voiceControl.registerCommand('go to caregivers', function() {
        voiceControl.speak("Going to caregivers page");
        window.location.href = '/caregivers';
    });
    
    voiceControl.registerCommand('go to memory lane', function() {
        voiceControl.speak("Going to memory lane");
        window.location.href = '/memory-lane';
    });
    
    voiceControl.registerCommand('go to exercises', function() {
        voiceControl.speak("Going to cognitive exercises");
        window.location.href = '/cognitive/exercises';
    });
    
    voiceControl.registerCommand('go to reminders', function() {
        voiceControl.speak("Going to reminders");
        window.location.href = '/reminders';
    });
    
    voiceControl.registerCommand('go to safety zones', function() {
        voiceControl.speak("Going to safety zones");
        window.location.href = '/safety/zones';
    });
}

/**
 * Register feature-specific commands
 */
function registerFeatureCommands() {
    const voiceControl = window.alphaVoiceControl;
    
    // Memory Lane commands
    voiceControl.registerCommand('show albums', function() {
        voiceControl.speak("Showing memory albums");
        scrollToSection('memory-albums');
    });
    
    voiceControl.registerCommand('show timeline', function() {
        voiceControl.speak("Showing life timeline");
        scrollToSection('timeline');
    });
    
    voiceControl.registerCommand('play music memories', function() {
        voiceControl.speak("Going to music memories");
        scrollToSection('music-memories');
    });
    
    // Learning Corner commands
    voiceControl.registerCommand('show research', function() {
        voiceControl.speak("Showing latest research");
        scrollToSection('latest-research');
    });
    
    voiceControl.registerCommand('show daily tip', function() {
        voiceControl.speak("Showing daily tip");
        scrollToSection('daily-tips');
    });
    
    voiceControl.registerCommand('show resources', function() {
        voiceControl.speak("Showing learning resources");
        scrollToSection('resources');
    });
    
    // Caregiver Page commands
    voiceControl.registerCommand('show patient status', function() {
        voiceControl.speak("Showing patient overview");
        scrollToSection('patient-overview');
    });
    
    voiceControl.registerCommand('show care plan', function() {
        voiceControl.speak("Showing daily care plan");
        scrollToSection('daily-care-plan');
    });
    
    voiceControl.registerCommand('show medications', function() {
        const medicationsTab = document.getElementById('medications-tab');
        if (medicationsTab) {
            voiceControl.speak("Showing medication schedule");
            medicationsTab.click();
        } else {
            voiceControl.speak("Medication tab not found on this page");
        }
    });
}

/**
 * Register accessibility commands
 */
function registerAccessibilityCommands() {
    const voiceControl = window.alphaVoiceControl;
    
    // Scrolling commands
    voiceControl.registerCommand('scroll down', function() {
        voiceControl.speak("Scrolling down");
        window.scrollBy({
            top: window.innerHeight / 2,
            behavior: 'smooth'
        });
    });
    
    voiceControl.registerCommand('scroll up', function() {
        voiceControl.speak("Scrolling up");
        window.scrollBy({
            top: -window.innerHeight / 2,
            behavior: 'smooth'
        });
    });
    
    voiceControl.registerCommand('scroll to top', function() {
        voiceControl.speak("Scrolling to top");
        window.scrollTo({
            top: 0,
            behavior: 'smooth'
        });
    });
    
    voiceControl.registerCommand('scroll to bottom', function() {
        voiceControl.speak("Scrolling to bottom");
        window.scrollTo({
            top: document.body.scrollHeight,
            behavior: 'smooth'
        });
    });
    
    // Read page content
    voiceControl.registerCommand('read page', function() {
        const mainContent = document.querySelector('main') || document.querySelector('.container');
        if (mainContent) {
            const contentText = extractReadableText(mainContent);
            voiceControl.speak("Reading page content");
            
            // Break content into chunks if it's too long
            const chunks = chunkText(contentText, 200);
            readTextChunks(chunks, 0);
        } else {
            voiceControl.speak("I couldn't find the main content to read");
        }
    });
}

/**
 * Register global commands
 */
function registerGlobalCommands() {
    const voiceControl = window.alphaVoiceControl;
    
    // Help command
    voiceControl.registerCommand('help', function() {
        voiceControl.speak("Showing available voice commands");
        document.getElementById('voice-commands-help').style.display = 'block';
    });
    
    // Stop listening command
    voiceControl.registerCommand('stop listening', function() {
        voiceControl.speak("Voice control deactivated");
        voiceControl.stop();
        document.getElementById('voice-control-toggle').classList.remove('active');
    });
    
    // Start listening command
    voiceControl.registerCommand('start listening', function() {
        voiceControl.speak("Voice control activated");
        voiceControl.start();
        document.getElementById('voice-control-toggle').classList.add('active');
    });
    
    // Mute microphone command
    voiceControl.registerCommand('mute microphone', function() {
        voiceControl.mute();
        const toggleBtn = document.getElementById('voice-control-toggle');
        toggleBtn.classList.remove('active');
        toggleBtn.classList.add('muted');
        toggleBtn.innerHTML = '<i class="fas fa-microphone-slash"></i>';
    });
    
    // Unmute microphone command
    voiceControl.registerCommand('unmute microphone', function() {
        voiceControl.unmute();
        const toggleBtn = document.getElementById('voice-control-toggle');
        toggleBtn.classList.add('active');
        toggleBtn.classList.remove('muted');
        toggleBtn.innerHTML = '<i class="fas fa-microphone"></i>';
    });
}

/**
 * Utility function to scroll to a section by ID
 */
function scrollToSection(sectionId) {
    const section = document.getElementById(sectionId);
    if (section) {
        section.scrollIntoView({
            behavior: 'smooth'
        });
    }
}

/**
 * Extract readable text from an HTML element
 */
function extractReadableText(element) {
    // Clone the element to avoid modifying the original
    const clone = element.cloneNode(true);
    
    // Remove elements that shouldn't be read
    const selectorsToRemove = [
        'script', 'style', 'footer', 'nav',
        '.voice-control-status', '.voice-control-feedback', '.voice-commands-help'
    ];
    
    selectorsToRemove.forEach(selector => {
        const elements = clone.querySelectorAll(selector);
        elements.forEach(el => el.remove());
    });
    
    // Get the text content
    return clone.textContent
        .replace(/\s+/g, ' ')
        .trim();
}

/**
 * Break text into manageable chunks
 */
function chunkText(text, maxWords) {
    const words = text.split(' ');
    const chunks = [];
    let currentChunk = [];
    
    words.forEach(word => {
        currentChunk.push(word);
        if (currentChunk.length >= maxWords) {
            chunks.push(currentChunk.join(' '));
            currentChunk = [];
        }
    });
    
    if (currentChunk.length > 0) {
        chunks.push(currentChunk.join(' '));
    }
    
    return chunks;
}

/**
 * Read text chunks sequentially
 */
function readTextChunks(chunks, index) {
    if (index >= chunks.length) return;
    
    const voiceControl = window.alphaVoiceControl;
    
    // Speak current chunk
    voiceControl.speak(chunks[index], {}, function() {
        // When done speaking, read the next chunk
        readTextChunks(chunks, index + 1);
    });
}