// AlphaWolf - Main JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Initialize components
    initFeatherIcons();
    initTooltips();
    initLocationTracking();
    
    // Setup event listeners
    setupReminderForm();
    setupSafeZoneForm();
    setupExerciseInteractions();
});

// Initialize Feather icons
function initFeatherIcons() {
    if (typeof feather !== 'undefined') {
        feather.replace();
    }
}

// Initialize Bootstrap tooltips
function initTooltips() {
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

// Setup reminder form
function setupReminderForm() {
    const reminderForm = document.getElementById('reminderForm');
    if (reminderForm) {
        reminderForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const formData = {
                title: document.getElementById('reminderTitle').value,
                description: document.getElementById('reminderDescription').value,
                time: document.getElementById('reminderTime').value,
                recurring: document.getElementById('reminderRecurring').checked,
                patient_id: document.getElementById('patientId') ? document.getElementById('patientId').value : null
            };
            
            fetch('/reminders/add', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(formData),
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Show success message
                    showAlert('Reminder added successfully!', 'success');
                    // Clear form
                    reminderForm.reset();
                    // Reload page to show new reminder
                    setTimeout(() => window.location.reload(), 1500);
                } else {
                    showAlert('Error adding reminder: ' + data.message, 'danger');
                }
            })
            .catch((error) => {
                showAlert('Error: ' + error, 'danger');
            });
        });
    }
}

// Setup safe zone form
function setupSafeZoneForm() {
    const safeZoneForm = document.getElementById('safeZoneForm');
    if (safeZoneForm) {
        safeZoneForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const formData = {
                name: document.getElementById('zoneName').value,
                latitude: parseFloat(document.getElementById('zoneLatitude').value),
                longitude: parseFloat(document.getElementById('zoneLongitude').value),
                radius: parseFloat(document.getElementById('zoneRadius').value)
            };
            
            fetch('/safety/zones/add', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(formData),
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Show success message
                    showAlert('Safety zone added successfully!', 'success');
                    // Clear form
                    safeZoneForm.reset();
                    // Reload map or add zone to existing map
                    if (typeof addZoneToMap === 'function') {
                        addZoneToMap(data.zone_id, formData.name, formData.latitude, formData.longitude, formData.radius);
                    } else {
                        setTimeout(() => window.location.reload(), 1500);
                    }
                } else {
                    showAlert('Error adding safety zone: ' + data.message, 'danger');
                }
            })
            .catch((error) => {
                showAlert('Error: ' + error, 'danger');
            });
        });
    }
}

// Initialize location tracking if user allows
function initLocationTracking() {
    // Check if we should track location (only for patients)
    const locationTrackingEnabled = document.body.getAttribute('data-enable-tracking') === 'true';
    
    if (locationTrackingEnabled && navigator.geolocation) {
        // Get location periodically
        navigator.geolocation.getCurrentPosition(
            function(position) {
                updateLocation(position.coords.latitude, position.coords.longitude);
            },
            function(error) {
                console.error('Error getting location:', error);
            }
        );
        
        // Setup periodic updates
        setInterval(function() {
            navigator.geolocation.getCurrentPosition(
                function(position) {
                    updateLocation(position.coords.latitude, position.coords.longitude);
                },
                function(error) {
                    console.error('Error getting location:', error);
                }
            );
        }, 5 * 60 * 1000); // Update every 5 minutes
    }
}

// Send location update to server
function updateLocation(latitude, longitude) {
    fetch('/location/update', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            latitude: latitude,
            longitude: longitude
        }),
    })
    .then(response => response.json())
    .then(data => {
        console.log('Location updated:', data);
    })
    .catch((error) => {
        console.error('Error updating location:', error);
    });
}

// Setup interactive elements for cognitive exercises
function setupExerciseInteractions() {
    // Memory match game
    const memoryGame = document.getElementById('memoryMatchGame');
    if (memoryGame) {
        setupMemoryMatch();
    }
    
    // Sequence recall game
    const sequenceGame = document.getElementById('sequenceRecallGame');
    if (sequenceGame) {
        setupSequenceRecall();
    }
    
    // Word recall game
    const wordRecallGame = document.getElementById('wordRecallGame');
    if (wordRecallGame) {
        setupWordRecall();
    }
}

// Submit exercise results
function submitExerciseResult(exerciseId, score, completionTime) {
    fetch('/api/exercise/result', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            exercise_id: exerciseId,
            score: score,
            completion_time: completionTime
        }),
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showAlert('Exercise result saved!', 'success');
            // Wait a moment and redirect to exercises list
            setTimeout(() => {
                window.location.href = '/cognitive/exercises';
            }, 2000);
        } else {
            showAlert('Error saving result: ' + data.message, 'danger');
        }
    })
    .catch((error) => {
        showAlert('Error: ' + error, 'danger');
    });
}

// Display alert message
function showAlert(message, type = 'info') {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
    alertDiv.role = 'alert';
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;
    
    // Insert at top of main container
    const container = document.querySelector('.container');
    if (container) {
        container.insertBefore(alertDiv, container.firstChild);
        
        // Auto-dismiss after 5 seconds
        setTimeout(() => {
            alertDiv.classList.remove('show');
            setTimeout(() => alertDiv.remove(), 300);
        }, 5000);
    }
}

// Memory match game setup
function setupMemoryMatch() {
    // Implementation would go here
    console.log('Memory match game initialized');
}

// Sequence recall game setup
function setupSequenceRecall() {
    // Implementation would go here
    console.log('Sequence recall game initialized');
}

// Word recall game setup
function setupWordRecall() {
    // Implementation would go here
    console.log('Word recall game initialized');
}