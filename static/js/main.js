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

// Initialize map with safety zones and patient locations
function initSafetyMap(mapElementId, safeZones, patients) {
    const mapElement = document.getElementById(mapElementId);
    if (!mapElement) return;
    
    // Create map centered at a default location (will adjust based on data)
    const map = L.map(mapElementId).setView([40.7128, -74.0060], 13);
    
    // Add OpenStreetMap tile layer
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        maxZoom: 19,
        attribution: '&copy; <a href="https://openstreetmap.org/copyright">OpenStreetMap contributors</a>'
    }).addTo(map);
    
    // Define zone colors for different types
    const zoneColors = {
        'home': '#4CAF50',  // Green for home
        'regular': '#2196F3', // Blue for regular locations
        'temporary': '#FF9800', // Orange for temporary locations
        'default': '#9C27B0'  // Purple for other zones
    };
    
    // Add safe zones to map
    const zoneMarkers = [];
    if (safeZones && safeZones.length > 0) {
        safeZones.forEach((zone, index) => {
            // Determine zone type and color (if not specified, use zone type pattern)
            const zoneType = zone.type || (
                zone.name.toLowerCase().includes('home') ? 'home' :
                zone.name.toLowerCase().includes('temp') ? 'temporary' : 'regular'
            );
            const color = zoneColors[zoneType] || zoneColors.default;
            
            // Add circle for the safe zone
            const circle = L.circle([zone.latitude, zone.longitude], {
                color: color,
                fillColor: color,
                fillOpacity: 0.2,
                radius: zone.radius
            }).addTo(map);
            
            // Add popup with zone information
            circle.bindPopup(`
                <strong>${zone.name}</strong><br>
                Radius: ${zone.radius}m<br>
                <small>Coordinates: ${zone.latitude.toFixed(6)}, ${zone.longitude.toFixed(6)}</small>
            `);
            
            // Add marker for center point
            const marker = L.marker([zone.latitude, zone.longitude], {
                title: zone.name
            }).addTo(map);
            marker.bindPopup(`<strong>${zone.name}</strong>`);
            
            zoneMarkers.push({ circle, marker });
        });
    }
    
    // Add patient locations to map
    const patientMarkers = [];
    if (patients && patients.length > 0) {
        patients.forEach(patient => {
            if (patient.last_latitude && patient.last_longitude) {
                // Create custom icon based on safety status
                const markerColor = patient.is_in_safe_zone ? '#28a745' : '#dc3545';
                const markerIcon = L.divIcon({
                    html: `<div style="background-color: ${markerColor}; width: 12px; height: 12px; border-radius: 50%; border: 2px solid white;"></div>`,
                    className: 'patient-location-marker',
                    iconSize: [16, 16],
                    iconAnchor: [8, 8]
                });
                
                // Add marker for patient location
                const marker = L.marker([patient.last_latitude, patient.last_longitude], {
                    icon: markerIcon,
                    title: patient.name
                }).addTo(map);
                
                // Add popup with patient information
                marker.bindPopup(`
                    <strong>${patient.name}</strong><br>
                    Status: ${patient.is_in_safe_zone ? 
                        '<span class="text-success">In safe zone</span>' : 
                        '<span class="text-danger">Outside safe zones</span>'
                    }<br>
                    Last update: ${new Date(patient.last_location_update).toLocaleString()}
                `);
                
                patientMarkers.push(marker);
            }
        });
    }
    
    // Fit map to include all zones and patients
    const allPoints = [];
    safeZones.forEach(zone => {
        allPoints.push([zone.latitude, zone.longitude]);
    });
    
    patients.forEach(patient => {
        if (patient.last_latitude && patient.last_longitude) {
            allPoints.push([patient.last_latitude, patient.last_longitude]);
        }
    });
    
    if (allPoints.length > 0) {
        const bounds = L.latLngBounds(allPoints);
        map.fitBounds(bounds.pad(0.2));
    }
    
    // Set up map click handler for adding new zones
    map.on('click', function(e) {
        // Check if add zone form is open
        const addZoneModal = document.getElementById('addZoneModal');
        if (addZoneModal && addZoneModal.classList.contains('show')) {
            // Set latitude and longitude in the form
            document.getElementById('latitude').value = e.latlng.lat.toFixed(6);
            document.getElementById('longitude').value = e.latlng.lng.toFixed(6);
        }
        
        // Check if edit zone form is open
        const editZoneModal = document.getElementById('editZoneModal');
        if (editZoneModal && editZoneModal.classList.contains('show')) {
            // Set latitude and longitude in the form
            document.getElementById('editLatitude').value = e.latlng.lat.toFixed(6);
            document.getElementById('editLongitude').value = e.latlng.lng.toFixed(6);
        }
    });
    
    // Return map and markers for later manipulation
    return {
        map,
        zoneMarkers,
        patientMarkers
    };
}

// Initialize alert map with safe zones and alert locations
function initAlertMap(mapElementId, safeZones, alerts) {
    const mapElement = document.getElementById(mapElementId);
    if (!mapElement) return;
    
    // Create map centered at a default location (will adjust based on data)
    const map = L.map(mapElementId).setView([40.7128, -74.0060], 13);
    
    // Add OpenStreetMap tile layer
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        maxZoom: 19,
        attribution: '&copy; <a href="https://openstreetmap.org/copyright">OpenStreetMap contributors</a>'
    }).addTo(map);
    
    // Add safe zones to map (more transparent than on safety map)
    if (safeZones && safeZones.length > 0) {
        safeZones.forEach(zone => {
            // Add circle for the safe zone
            L.circle([zone.latitude, zone.longitude], {
                color: '#28a745',
                fillColor: '#28a745',
                fillOpacity: 0.1,
                radius: zone.radius
            }).addTo(map).bindPopup(`<strong>${zone.name}</strong><br>Radius: ${zone.radius}m`);
        });
    }
    
    // Add alert locations to map
    const alertMarkers = [];
    if (alerts && alerts.length > 0) {
        alerts.forEach(alert => {
            if (alert.latitude && alert.longitude) {
                // Determine alert icon based on type and resolved status
                const isCritical = alert.message.includes('CRITICAL');
                const iconColor = isCritical ? '#dc3545' : '#ffc107';
                const opacity = alert.is_resolved ? 0.5 : 1.0;
                
                // Create custom icon
                const alertIcon = L.divIcon({
                    html: `<div style="background-color: ${iconColor}; opacity: ${opacity}; width: 14px; height: 14px; border-radius: 50%; border: 2px solid white;"></div>`,
                    className: 'alert-location-marker',
                    iconSize: [18, 18],
                    iconAnchor: [9, 9]
                });
                
                // Add marker for alert location
                const marker = L.marker([alert.latitude, alert.longitude], {
                    icon: alertIcon,
                    title: alert.message
                }).addTo(map);
                
                // Add popup with alert information
                marker.bindPopup(`
                    <strong>${alert.message}</strong><br>
                    Type: ${alert.alert_type}<br>
                    ${alert.is_resolved ? '<span class="text-secondary">Resolved</span>' : '<span class="text-danger">Active</span>'}<br>
                    Time: ${new Date(alert.timestamp).toLocaleString()}
                `);
                
                alertMarkers.push(marker);
            }
        });
    }
    
    // Fit map to include all zones and alerts
    const allPoints = [];
    safeZones.forEach(zone => {
        allPoints.push([zone.latitude, zone.longitude]);
    });
    
    alerts.forEach(alert => {
        if (alert.latitude && alert.longitude) {
            allPoints.push([alert.latitude, alert.longitude]);
        }
    });
    
    if (allPoints.length > 0) {
        const bounds = L.latLngBounds(allPoints);
        map.fitBounds(bounds.pad(0.2));
    }
    
    // Return map and markers for later manipulation
    return {
        map,
        alertMarkers
    };
}

// Function to handle current location request
function getCurrentLocation(callback) {
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(
            function(position) {
                callback({
                    success: true,
                    latitude: position.coords.latitude,
                    longitude: position.coords.longitude
                });
            },
            function(error) {
                callback({
                    success: false,
                    error: error.message
                });
            }
        );
    } else {
        callback({
            success: false,
            error: 'Geolocation is not supported by this browser.'
        });
    }
}