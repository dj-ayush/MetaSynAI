document.addEventListener('DOMContentLoaded', function() {
    // Initialize particles.js with modified settings
    particlesJS('particles-js', {
        particles: {
            number: {
                value: 60,
                density: {
                    enable: true,
                    value_area: 800
                }
            },
            color: {
                value: "#ffffff"
            },
            opacity: {
                value: 0.2,
                random: true
            },
            size: {
                value: 3,
                random: true
            },
            line_linked: {
                enable: true,
                distance: 150,
                color: "#ffffff",
                opacity: 0.1,
                width: 1
            },
            move: {
                enable: true,
                speed: 1,
                direction: "none"
            }
        },
        interactivity: {
            detect_on: "canvas",
            events: {
                onhover: {
                    enable: true,
                    mode: "grab"
                },
                onclick: {
                    enable: true,
                    mode: "push"
                }
            }
        }
    });

    // Wait for everything to be fully loaded
    window.addEventListener('load', function() {
        // Remove preparation class
        document.body.classList.remove('gsap-prepare');
        
        // GSAP timeline for animations
        const tl = gsap.timeline({ defaults: { ease: "power3.out" } });

        // Navbar animation
        tl.from(".navbar", {
            y: -50,
            opacity: 0,
            duration: 0.8
        });

        // Main title animation
        tl.from(".main-title", {
            y: 30,
            opacity: 0,
            duration: 0.8
        }, "-=0.4");

        // Card animations with proper z-index handling
        tl.from(".card", {
            y: 30,
            opacity: 0,
            duration: 0.8,
            stagger: 0.15,
            ease: "back.out",
            onStart: function() {
                // Ensure cards are visible
                gsap.set(".card", { zIndex: 10 });
            }
        }, "-=0.3");

        // Footer animation
        tl.from(".footer", {
            y: 30,
            opacity: 0,
            duration: 0.8
        }, "-=0.4");
    });

    // Card hover effects
    document.querySelectorAll('.card').forEach(card => {
        card.addEventListener('mouseenter', () => {
            gsap.to(card, {
                scale: 1.03,
                y: -5,
                duration: 0.3
            });
        });

        card.addEventListener('mouseleave', () => {
            gsap.to(card, {
                scale: 1,
                y: 0,
                duration: 0.3
            });
        });
    });
});