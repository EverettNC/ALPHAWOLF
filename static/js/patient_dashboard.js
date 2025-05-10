/**
 * AlphaWolf Patient Dashboard Scripts
 * Provides interactive features for the patient dashboard
 */

document.addEventListener('DOMContentLoaded', function() {
  // Initialize visual observation/recognition features
  initVisualRecognition();
  
  // Setup animations for the dashboard elements
  animateDashboard();
  
  // Setup event listeners for reminder checkboxes
  setupReminderEvents();
});

/**
 * Initialize the visual recognition section
 */
function initVisualRecognition() {
  const container = document.getElementById('recognition-container');
  if (!container) return;
  
  // Get the refresh button
  const refreshBtn = document.getElementById('refresh-recognition');
  if (refreshBtn) {
    refreshBtn.addEventListener('click', function() {
      refreshVisualRecognition();
    });
  }
  
  // Register voice commands for recognition assistance
  if (window.alphaVoiceControl) {
    window.alphaVoiceControl.registerCommand('who is this person', function() {
      providePersonAssistance();
    });
  }
}

/**
 * Refresh the visual recognition section with updated data
 */
function refreshVisualRecognition() {
  const container = document.getElementById('recognition-container');
  if (!container) return;
  
  // Show loading state
  container.style.opacity = '0.5';
  
  // In a real implementation, this would fetch data from the server
  // using the cognitive enhancement module or computer vision API
  fetch('/api/cognitive/recognition')
    .then(response => response.json())
    .catch(() => {
      // For demonstration, we'll use mock data if the API isn't implemented yet
      return getSampleRecognitionData();
    })
    .then(data => {
      updateRecognitionCards(data);
      container.style.opacity = '1';
    });
}

/**
 * Update the recognition cards with new data
 */
function updateRecognitionCards(data) {
  const container = document.getElementById('recognition-container');
  if (!container || !data || !data.people) return;
  
  // Clear existing cards
  container.innerHTML = '';
  
  // Add new cards
  data.people.forEach(person => {
    const card = createPersonCard(person);
    container.appendChild(card);
  });
  
  // Add animation to new cards
  animateRecognitionCards();
}

/**
 * Create a person card for the visual recognition section
 */
function createPersonCard(person) {
  const colDiv = document.createElement('div');
  colDiv.className = 'col-md-4 mb-3';
  
  colDiv.innerHTML = `
    <div class="recognition-card position-relative" data-person-id="${person.id}">
      <div class="text-center">
        <img src="${person.photo}" class="recognition-photo" alt="${person.name}">
        <span class="recognition-badge">${person.role}</span>
      </div>
      <h3 class="client-name text-center">${person.name}</h3>
      <p class="client-relation text-center">${person.relation}</p>
      <div class="recognition-details">
        ${person.schedule ? `<p class="mb-1"><small><i class="fas fa-calendar-check me-2"></i> ${person.schedule}</small></p>` : ''}
        ${person.lastVisit ? `<p class="mb-0"><small><i class="fas fa-clock me-2"></i> ${person.lastVisit}</small></p>` : ''}
      </div>
    </div>
  `;
  
  return colDiv;
}

/**
 * Add animations to recognition cards
 */
function animateRecognitionCards() {
  const cards = document.querySelectorAll('.recognition-card');
  cards.forEach((card, index) => {
    card.style.opacity = '0';
    card.style.transform = 'translateY(20px)';
    
    setTimeout(() => {
      card.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
      card.style.opacity = '1';
      card.style.transform = 'translateY(0)';
    }, 100 * index);
  });
}

/**
 * Provide assistance with identifying a person using voice
 */
function providePersonAssistance() {
  if (window.alphaVoiceControl) {
    window.alphaVoiceControl.speak("To identify someone, please look at their photo and ask 'Who is this person?'");
    
    // Highlight all recognition cards to draw attention
    const cards = document.querySelectorAll('.recognition-card');
    cards.forEach(card => {
      card.style.boxShadow = '0 0 0 3px #4CAF50';
      setTimeout(() => {
        card.style.boxShadow = '';
      }, 2000);
    });
  }
}

/**
 * Animate dashboard elements
 */
function animateDashboard() {
  // Animate progress bars
  const progressBars = document.querySelectorAll('.progress-bar');
  progressBars.forEach(bar => {
    const width = bar.style.width;
    bar.style.width = '0%';
    setTimeout(() => {
      bar.style.width = width;
    }, 300);
  });
  
  // Animate cards
  const cards = document.querySelectorAll('.dashboard-card');
  cards.forEach((card, index) => {
    card.style.opacity = '0';
    card.style.transform = 'translateY(20px)';
    
    setTimeout(() => {
      card.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
      card.style.opacity = '1';
      card.style.transform = 'translateY(0)';
    }, 100 * index);
  });
}

/**
 * Setup event listeners for reminder checkboxes
 */
function setupReminderEvents() {
  // No need to add event listeners here as they're already inline in the HTML
  // This function could be used for additional reminder-related functionality
}

/**
 * Get sample recognition data 
 * This would be replaced by actual API data in production
 */
function getSampleRecognitionData() {
  return {
    people: [
      {
        id: 1,
        name: "Susan Williams",
        role: "Caregiver",
        relation: "Primary Nurse",
        photo: "https://randomuser.me/api/portraits/women/65.jpg",
        schedule: "Today: Morning medication",
        lastVisit: "Last visit: 2 hours ago"
      },
      {
        id: 2,
        name: "Robert Johnson",
        role: "Family",
        relation: "Son",
        photo: "https://randomuser.me/api/portraits/men/32.jpg",
        schedule: "Expected visit: Today at 4 PM",
        lastVisit: "Last visit: 2 days ago"
      },
      {
        id: 3,
        name: "Mary Thompson",
        role: "Family",
        relation: "Daughter",
        photo: "https://randomuser.me/api/portraits/women/38.jpg",
        schedule: "Expected visit: Tomorrow at 2 PM",
        lastVisit: "Last visit: 1 week ago"
      }
    ]
  };
}