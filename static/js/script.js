// Portfolio JavaScript

document.addEventListener('DOMContentLoaded', function() {
    
    // iOS Safari Detection
    const isIOS = /iPad|iPhone|iPod/.test(navigator.userAgent) && !window.MSStream;
    const isSafari = /^((?!chrome|android).)*safari/i.test(navigator.userAgent);
    
    // iOS Safari Specific Fixes
    if (isIOS) {
        // Fix for iOS Safari viewport issues
        const viewport = document.querySelector('meta[name=viewport]');
        if (viewport) {
            viewport.setAttribute('content', 'width=device-width, initial-scale=1.0, viewport-fit=cover, user-scalable=no');
        }
        
        // Fix for iOS Safari 100vh issue
        const setVH = () => {
            const vh = window.innerHeight * 0.01;
            document.documentElement.style.setProperty('--vh', `${vh}px`);
        };
        
        setVH();
        window.addEventListener('resize', setVH);
        window.addEventListener('orientationchange', setVH);
        
        // Prevent zoom on double tap
        let lastTouchEnd = 0;
        document.addEventListener('touchend', function (event) {
            const now = (new Date()).getTime();
            if (now - lastTouchEnd <= 300) {
                event.preventDefault();
            }
            lastTouchEnd = now;
        }, false);
    }
    
    // Smooth scrolling per i link interni
    const internalLinks = document.querySelectorAll('a[href^="#"]');
    internalLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const targetId = this.getAttribute('href');
            const targetElement = document.querySelector(targetId);
            
            if (targetElement) {
                targetElement.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });

    // Animazione delle skill bars quando sono visibili
    const skillBars = document.querySelectorAll('.skill-bar');
    const observerOptions = {
        threshold: 0.5,
        rootMargin: '0px 0px -50px 0px'
    };

    const skillObserver = new IntersectionObserver(function(entries) {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const skillBar = entry.target;
                const width = skillBar.style.width;
                skillBar.style.width = '0%';
                
                setTimeout(() => {
                    skillBar.style.width = width;
                }, 100);
                
                skillObserver.unobserve(skillBar);
            }
        });
    }, observerOptions);

    skillBars.forEach(bar => {
        skillObserver.observe(bar);
    });

    // Navbar scroll effect
    const navbar = document.querySelector('.navbar');
    let lastScrollTop = 0;

    window.addEventListener('scroll', function() {
        const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
        
        if (scrollTop > 100) {
            navbar.style.background = 'rgba(255, 255, 255, 0.95)';
            navbar.style.backdropFilter = 'blur(10px)';
            navbar.style.webkitBackdropFilter = 'blur(10px)';
        } else {
            navbar.style.background = 'var(--bg-light)';
            navbar.style.backdropFilter = 'none';
            navbar.style.webkitBackdropFilter = 'none';
        }
        
        lastScrollTop = scrollTop;
    });

    // Form validation
    const contactForm = document.querySelector('.contact-form');
    if (contactForm) {
        contactForm.addEventListener('submit', function(e) {
            const requiredFields = this.querySelectorAll('[required]');
            let isValid = true;

            requiredFields.forEach(field => {
                if (!field.value.trim()) {
                    field.style.borderColor = '#dc3545';
                    isValid = false;
                } else {
                    field.style.borderColor = 'var(--border-color)';
                }
            });

            if (!isValid) {
                e.preventDefault();
                alert('Per favore compila tutti i campi obbligatori.');
            }
        });
    }

    // Typing effect per il titolo hero
    const heroTitle = document.querySelector('.hero h1');
    if (heroTitle) {
        const text = heroTitle.textContent;
        heroTitle.textContent = '';
        
        let i = 0;
        const typeWriter = () => {
            if (i < text.length) {
                heroTitle.textContent += text.charAt(i);
                i++;
                setTimeout(typeWriter, 100);
            }
        };
        
        // Avvia l'effetto dopo un breve delay
        setTimeout(typeWriter, 500);
    }

    // Lazy loading per le immagini
    const images = document.querySelectorAll('img[data-src]');
    const imageObserver = new IntersectionObserver(function(entries) {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const img = entry.target;
                img.src = img.dataset.src;
                img.classList.remove('lazy');
                imageObserver.unobserve(img);
            }
        });
    });

    images.forEach(img => {
        imageObserver.observe(img);
    });

    // Mobile menu toggle
    const mobileMenuToggle = document.getElementById('mobile-menu-toggle');
    const mobileMenu = document.getElementById('mobile-menu');
    const body = document.body;
    
    if (mobileMenuToggle && mobileMenu) {
        mobileMenuToggle.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            
            this.classList.toggle('active');
            mobileMenu.classList.toggle('active');
            
            // Mostra/nascondi il menu mobile
            if (mobileMenu.classList.contains('active')) {
                mobileMenu.style.display = 'block';
                body.style.overflow = 'hidden'; // Previene lo scroll del body
                
                // iOS Safari specific fix
                if (isIOS) {
                    body.style.position = 'fixed';
                    body.style.width = '100%';
                }
            } else {
                mobileMenu.style.display = 'none';
                body.style.overflow = ''; // Ripristina lo scroll
                
                // iOS Safari specific fix
                if (isIOS) {
                    body.style.position = '';
                    body.style.width = '';
                }
            }
        });
        
        // Chiudi il menu quando si clicca su un link
        const mobileNavLinks = mobileMenu.querySelectorAll('a');
        mobileNavLinks.forEach(link => {
            link.addEventListener('click', function() {
                mobileMenuToggle.classList.remove('active');
                mobileMenu.classList.remove('active');
                mobileMenu.style.display = 'none';
                body.style.overflow = '';
                
                // iOS Safari specific fix
                if (isIOS) {
                    body.style.position = '';
                    body.style.width = '';
                }
            });
        });
        
        // Chiudi il menu quando si ridimensiona la finestra
        window.addEventListener('resize', function() {
            if (window.innerWidth > 767) {
                mobileMenuToggle.classList.remove('active');
                mobileMenu.classList.remove('active');
                mobileMenu.style.display = 'none';
                body.style.overflow = '';
                
                // iOS Safari specific fix
                if (isIOS) {
                    body.style.position = '';
                    body.style.width = '';
                }
            }
        });
        
        // Chiudi il menu quando si tocca fuori
        document.addEventListener('click', function(e) {
            if (!mobileMenuToggle.contains(e.target) && !mobileMenu.contains(e.target)) {
                mobileMenuToggle.classList.remove('active');
                mobileMenu.classList.remove('active');
                mobileMenu.style.display = 'none';
                body.style.overflow = '';
                
                // iOS Safari specific fix
                if (isIOS) {
                    body.style.position = '';
                    body.style.width = '';
                }
            }
        });
    }

    // Parallax effect per il hero section
    const hero = document.querySelector('.hero');
    if (hero) {
        window.addEventListener('scroll', function() {
            const scrolled = window.pageYOffset;
            const rate = scrolled * -0.5;
            hero.style.transform = `translateY(${rate}px)`;
        });
    }

    // Tooltip per i social links
    const socialLinks = document.querySelectorAll('.social-links a, .social-links-contact a');
    socialLinks.forEach(link => {
        link.addEventListener('mouseenter', function() {
            this.style.transform = 'scale(1.1)';
        });
        
        link.addEventListener('mouseleave', function() {
            this.style.transform = 'scale(1)';
        });
        
        // iOS Safari touch events
        if (isIOS) {
            link.addEventListener('touchstart', function() {
                this.style.transform = 'scale(1.1)';
            });
            
            link.addEventListener('touchend', function() {
                this.style.transform = 'scale(1)';
            });
        }
    });

    // Counter animation per le statistiche (se aggiunte in futuro)
    const counters = document.querySelectorAll('.counter');
    const counterObserver = new IntersectionObserver(function(entries) {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const counter = entry.target;
                const target = parseInt(counter.getAttribute('data-target'));
                const duration = 2000; // 2 secondi
                const increment = target / (duration / 16);
                let current = 0;

                const updateCounter = () => {
                    current += increment;
                    if (current < target) {
                        counter.textContent = Math.floor(current);
                        requestAnimationFrame(updateCounter);
                    } else {
                        counter.textContent = target;
                    }
                };

                updateCounter();
                counterObserver.unobserve(counter);
            }
        });
    });

    counters.forEach(counter => {
        counterObserver.observe(counter);
    });

    // Preloader (opzionale)
    window.addEventListener('load', function() {
        const preloader = document.querySelector('.preloader');
        if (preloader) {
            preloader.style.opacity = '0';
            setTimeout(() => {
                preloader.style.display = 'none';
            }, 500);
        }
    });

    // iOS Safari specific fixes
    if (isIOS) {
        // Fix for iOS Safari input zoom
        const inputs = document.querySelectorAll('input, textarea, select');
        inputs.forEach(input => {
            input.addEventListener('focus', function() {
                if (this.type !== 'file') {
                    this.style.fontSize = '16px';
                }
            });
        });
        
        // Fix for iOS Safari scroll momentum
        const scrollableElements = document.querySelectorAll('.mobile-menu, .reviews-container, .users-container');
        scrollableElements.forEach(element => {
            element.style.webkitOverflowScrolling = 'touch';
        });
    }

});

// Utility functions
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Throttle function per performance
function throttle(func, limit) {
    let inThrottle;
    return function() {
        const args = arguments;
        const context = this;
        if (!inThrottle) {
            func.apply(context, args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    };
}
