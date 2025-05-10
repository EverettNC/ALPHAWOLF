/**
 * AlphaWolf Main JavaScript
 * General functionality for the AlphaWolf application
 */

document.addEventListener('DOMContentLoaded', function() {
    console.log('AlphaWolf system initializing...');
    
    // Initialize any Bootstrap tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Initialize Bootstrap popovers
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
    
    // Add cyber effects to cards
    const cyberCards = document.querySelectorAll('.cyber-card');
    cyberCards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-5px)';
            this.style.boxShadow = '0 0 25px rgba(83, 92, 236, 0.4)';
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.transform = '';
            this.style.boxShadow = '';
        });
    });
    
    // Handle form submissions with AJAX when needed
    const ajaxForms = document.querySelectorAll('form[data-ajax="true"]');
    ajaxForms.forEach(form => {
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const formData = new FormData(this);
            const url = this.getAttribute('action');
            const method = this.getAttribute('method') || 'POST';
            
            fetch(url, {
                method: method,
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            })
            .then(response => response.json())
            .then(data => {
                console.log('Form submission response:', data);
                
                if (data.success) {
                    showNotification(data.message || 'Success!', 'success');
                    
                    // Handle redirect if provided
                    if (data.redirect) {
                        setTimeout(() => {
                            window.location.href = data.redirect;
                        }, 1000);
                    }
                    
                    // Handle DOM updates if provided
                    if (data.update_element && data.update_content) {
                        const element = document.querySelector(data.update_element);
                        if (element) {
                            element.innerHTML = data.update_content;
                        }
                    }
                    
                    // Reset form if needed
                    if (data.reset_form) {
                        form.reset();
                    }
                } else {
                    showNotification(data.message || 'An error occurred', 'error');
                }
            })
            .catch(error => {
                console.error('Error submitting form:', error);
                showNotification('An error occurred while submitting the form', 'error');
            });
        });
    });
    
    // Handle tabbed interfaces
    const tabLinks = document.querySelectorAll('[data-bs-toggle="tab"]');
    tabLinks.forEach(tabLink => {
        tabLink.addEventListener('shown.bs.tab', function (event) {
            const targetId = event.target.getAttribute('href');
            // Save active tab to sessionStorage if needed
            if (this.closest('[data-store-state]')) {
                const stateKey = this.closest('[data-store-state]').getAttribute('data-store-state');
                sessionStorage.setItem(stateKey, targetId);
            }
        });
        
        // Restore active tab from sessionStorage if needed
        if (tabLink.closest('[data-store-state]')) {
            const stateKey = tabLink.closest('[data-store-state]').getAttribute('data-store-state');
            const savedTab = sessionStorage.getItem(stateKey);
            
            if (savedTab && savedTab === tabLink.getAttribute('href')) {
                const tab = new bootstrap.Tab(tabLink);
                tab.show();
            }
        }
    });
    
    // Futuristic typing effect for designated elements
    const typeElements = document.querySelectorAll('[data-type-effect]');
    typeElements.forEach(element => {
        const text = element.textContent;
        const speed = parseInt(element.getAttribute('data-type-speed')) || 50;
        
        // Clear the element and set up for typing
        element.textContent = '';
        element.style.borderRight = '0.15em solid var(--accent-color)';
        element.style.animation = 'blink-caret 0.75s step-end infinite';
        
        // Add typing animation style if not already in the document
        if (!document.getElementById('typing-animation-style')) {
            const style = document.createElement('style');
            style.id = 'typing-animation-style';
            style.textContent = `
                @keyframes blink-caret {
                    from, to { border-color: transparent }
                    50% { border-color: var(--accent-color) }
                }
            `;
            document.head.appendChild(style);
        }
        
        // Perform typing animation
        let charIndex = 0;
        function typeWriter() {
            if (charIndex < text.length) {
                element.textContent += text.charAt(charIndex);
                charIndex++;
                setTimeout(typeWriter, speed);
            } else {
                // Remove cursor after typing is complete
                setTimeout(() => {
                    element.style.borderRight = 'none';
                    element.style.animation = 'none';
                }, 1000);
            }
        }
        
        // Start the typing effect
        typeWriter();
    });
    
    // Dynamic content loaders
    const contentLoaders = document.querySelectorAll('[data-load-content]');
    contentLoaders.forEach(loader => {
        const url = loader.getAttribute('data-load-content');
        const target = loader.getAttribute('data-target') || loader;
        const auto = loader.hasAttribute('data-auto-load');
        
        const loadContent = () => {
            if (target) {
                const targetElement = target === loader ? loader : document.querySelector(target);
                if (targetElement) {
                    targetElement.innerHTML = '<div class="text-center p-3"><i class="fas fa-spinner fa-spin"></i> Loading...</div>';
                    
                    fetch(url)
                        .then(response => response.text())
                        .then(html => {
                            targetElement.innerHTML = html;
                        })
                        .catch(error => {
                            console.error('Error loading content:', error);
                            targetElement.innerHTML = '<div class="alert alert-danger">Error loading content</div>';
                        });
                }
            }
        };
        
        if (auto) {
            loadContent();
        } else {
            loader.addEventListener('click', function(e) {
                e.preventDefault();
                loadContent();
            });
        }
    });
    
    console.log('AlphaWolf system initialized');
});