/**
 * Set theme for the application
 * @param {string} theme - Theme name to apply
 * @description Updates the document theme and saves to localStorage
 */
function setTheme(theme) {
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('theme', theme);
}

/**
 * Initialize theme on page load
 * @description Loads and applies saved theme or defaults to light theme
 */
document.addEventListener('DOMContentLoaded', () => {
    const savedTheme = localStorage.getItem('theme') || 'light';
    setTheme(savedTheme);
});