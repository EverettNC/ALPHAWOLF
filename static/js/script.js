/**
 * AlphaWolf Main JavaScript
 * Part of The Christman AI Project - Powered by LumaCognify AI
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    const tooltips = document.querySelectorAll('[data-bs-toggle="tooltip"]');
    if (tooltips.length > 0) {
        Array.from(tooltips).map(tooltip => new bootstrap.Tooltip(tooltip));
    }
    
    // Initialize popovers
    const popovers = document.querySelectorAll('[data-bs-toggle="popover"]');
    if (popovers.length > 0) {
        Array.from(popovers).map(popover => new bootstrap.Popover(popover));
    }
    
    // Automatically dismiss alerts after 5 seconds
    const autoAlerts = document.querySelectorAll('.alert.auto-dismiss');
    if (autoAlerts.length > 0) {
        autoAlerts.forEach(alert => {
            setTimeout(() => {
                const bsAlert = new bootstrap.Alert(alert);
                bsAlert.close();
            }, 5000);
        });
    }
    
    // Add smooth scrolling to all links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            if (this.getAttribute('href') !== '#') {
                e.preventDefault();
                const target = document.querySelector(this.getAttribute('href'));
                if (target) {
                    target.scrollIntoView({
                        behavior: 'smooth',
                        block: 'start'
                    });
                }
            }
        });
    });
    
    // Form validation
    const forms = document.querySelectorAll('.needs-validation');
    if (forms.length > 0) {
        Array.from(forms).forEach(form => {
            form.addEventListener('submit', event => {
                if (!form.checkValidity()) {
                    event.preventDefault();
                    event.stopPropagation();
                }
                form.classList.add('was-validated');
            }, false);
        });
    }
    
    // Toggle password visibility
    const passwordToggles = document.querySelectorAll('.password-toggle');
    if (passwordToggles.length > 0) {
        passwordToggles.forEach(toggle => {
            toggle.addEventListener('click', function() {
                const input = document.querySelector(this.getAttribute('data-bs-target'));
                if (input) {
                    if (input.type === 'password') {
                        input.type = 'text';
                        this.innerHTML = '<i class="fas fa-eye-slash"></i>';
                    } else {
                        input.type = 'password';
                        this.innerHTML = '<i class="fas fa-eye"></i>';
                    }
                }
            });
        });
    }
    
    // Add animation classes when elements enter viewport
    const animatedElements = document.querySelectorAll('.animate-on-scroll');
    if (animatedElements.length > 0) {
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('animated');
                }
            });
        }, { threshold: 0.1 });
        
        animatedElements.forEach(element => {
            observer.observe(element);
        });
    }
    
    // Handle theme toggle if present
    const themeToggle = document.getElementById('theme-toggle');
    if (themeToggle) {
        themeToggle.addEventListener('click', function() {
            document.documentElement.setAttribute('data-bs-theme', 
                document.documentElement.getAttribute('data-bs-theme') === 'dark' ? 'light' : 'dark');
            
            // Save preference to localStorage
            localStorage.setItem('alphawolf-theme', document.documentElement.getAttribute('data-bs-theme'));
        });
        
        // Set initial theme based on user preference
        const savedTheme = localStorage.getItem('alphawolf-theme');
        if (savedTheme) {
            document.documentElement.setAttribute('data-bs-theme', savedTheme);
        }
    }
    
    // Progress bars animation
    const progressBars = document.querySelectorAll('.progress-bar-animated');
    if (progressBars.length > 0) {
        progressBars.forEach(bar => {
            const targetWidth = bar.getAttribute('aria-valuenow') + '%';
            bar.style.width = '0%';
            setTimeout(() => {
                bar.style.width = targetWidth;
            }, 300);
        });
    }
    
    // User menu dropdown enhancement
    const userMenuDropdown = document.querySelector('.user-menu-dropdown');
    if (userMenuDropdown) {
        userMenuDropdown.addEventListener('show.bs.dropdown', function() {
            document.querySelector('.user-avatar').classList.add('pulse');
        });
        
        userMenuDropdown.addEventListener('hide.bs.dropdown', function() {
            document.querySelector('.user-avatar').classList.remove('pulse');
        });
    }
    
    // Countdown timer functionality
    const countdownElements = document.querySelectorAll('[data-countdown]');
    if (countdownElements.length > 0) {
        countdownElements.forEach(element => {
            const targetDate = new Date(element.getAttribute('data-countdown')).getTime();
            
            const interval = setInterval(function() {
                const now = new Date().getTime();
                const distance = targetDate - now;
                
                if (distance < 0) {
                    clearInterval(interval);
                    element.innerHTML = "Expired";
                    return;
                }
                
                const days = Math.floor(distance / (1000 * 60 * 60 * 24));
                const hours = Math.floor((distance % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
                const minutes = Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60));
                const seconds = Math.floor((distance % (1000 * 60)) / 1000);
                
                element.innerHTML = `${days}d ${hours}h ${minutes}m ${seconds}s`;
            }, 1000);
        });
    }
    
    // Initialize any carousels with custom options
    const carousels = document.querySelectorAll('.alphawolf-carousel');
    if (carousels.length > 0) {
        carousels.forEach(carousel => {
            new bootstrap.Carousel(carousel, {
                interval: 5000,
                touch: true,
                pause: 'hover'
            });
        });
    }
    
    // Add pulsing effect to notification icons
    const notificationIcons = document.querySelectorAll('.notification-icon');
    if (notificationIcons.length > 0) {
        notificationIcons.forEach(icon => {
            if (parseInt(icon.getAttribute('data-count') || '0') > 0) {
                icon.classList.add('cyber-pulse');
            }
        });
    }
    
    // Special initialization for home page features
    if (document.body.classList.contains('home-page')) {
        console.log("Initializing home page special features...");
        
        // Feature animation trigger on scroll
        const featureCards = document.querySelectorAll('.feature-card');
        if (featureCards.length > 0) {
            const observer = new IntersectionObserver((entries) => {
                entries.forEach((entry, index) => {
                    if (entry.isIntersecting) {
                        setTimeout(() => {
                            entry.target.classList.add('revealed');
                        }, index * 150); // Staggered animation
                    }
                });
            }, { threshold: 0.2 });
            
            featureCards.forEach(card => {
                observer.observe(card);
            });
        }
    }
    
    // Initialize the mission statement cycler if present
    const missionStatementCycler = document.getElementById('mission-statement-cycler');
    if (missionStatementCycler) {
        const statements = [
            "How can I help you love yourself more?",
            "AI that empowers, protects, and redefines humanity.",
            "Because communication is a human right.",
            "Because no one should lose their memories—or their dignity.",
            "Because learning should be accessible for everyone."
        ];
        
        let currentIndex = 0;
        
        setInterval(() => {
            missionStatementCycler.style.opacity = 0;
            
            setTimeout(() => {
                currentIndex = (currentIndex + 1) % statements.length;
                missionStatementCycler.textContent = statements[currentIndex];
                missionStatementCycler.style.opacity = 1;
            }, 500);
        }, 5000);
    }
    
    // Add class to body based on current page
    const currentPath = window.location.pathname;
    if (currentPath === '/') {
        document.body.classList.add('landing-page');
    } else if (currentPath === '/home') {
        document.body.classList.add('home-page');
    } else if (currentPath.includes('patient_dashboard')) {
        document.body.classList.add('dashboard-page', 'patient-user');
    } else if (currentPath.includes('caregiver_dashboard')) {
        document.body.classList.add('dashboard-page', 'caregiver-user');
    }
});