document.addEventListener('DOMContentLoaded', function() {
    const mobileMenuToggle = document.getElementById('mobile-menu-toggle');
    const mobileHeader = document.getElementById('mobile-header');
    const closeMobileMenuBtn = document.getElementById('close-mobile-menu');

    // Toggle mobile menu
    mobileMenuToggle.addEventListener('click', function() {
        mobileHeader.classList.remove('hidden');
    });

    // Close mobile menu
    closeMobileMenuBtn.addEventListener('click', function() {
        mobileHeader.classList.add('hidden');
    });
});