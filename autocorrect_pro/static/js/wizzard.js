/**
 * Current step tracker for wizard navigation
 */
let currentStep = 1;

/**
 * Navigate to next step in wizard
 * @param {number} step - Step number to navigate to
 * @description Hides all steps and shows the specified step
 */
function nextStep(step) {
    document.querySelectorAll('.fade-in').forEach(el => el.classList.add('hidden'));
    document.getElementById(`step${step}`).classList.remove('hidden');
    currentStep = step;
    document.getElementById('currentStep').innerText = currentStep;
}

/**
 * Navigate to previous step in wizard
 * @param {number} step - Step number to navigate to
 * @description Wrapper around nextStep for backward navigation
 */
function prevStep(step) {
    nextStep(step);
}

/**
 * Validate configuration and proceed to final step
 * @description Validates API key and custom endpoint configuration before proceeding
 */
function validateAndNext() {
    const apiKey = document.getElementById('apiKey').value.trim();
    const selectedModel = document.getElementById('modelSelect').value;

    if (!apiKey) {
        document.getElementById('apiKey').classList.add('shake');
        setTimeout(() => {
            document.getElementById('apiKey').classList.remove('shake');
        }, 500);
        alert('Veuillez entrer une clé API valide.');
        return;
    }

    if (selectedModel === 'custom') {
        const customEndpointUrl = document.getElementById('customEndpointUrl').value.trim();
        const customEndpointModel = document.getElementById('customEndpointModel').value.trim();
        const customEndpointStyle = document.getElementById('customEndpointStyle').value;

        if (!customEndpointUrl || !customEndpointModel) {
            alert('Veuillez remplir tous les champs pour l\'endpoint personnalisé.');
            return;
        }
    }

    nextStep(4);
}

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
 * Initialize theme system and populate theme options
 * @description Loads saved theme and populates theme select with all available options
 */
document.addEventListener('DOMContentLoaded', () => {
    const savedTheme = localStorage.getItem('theme') || 'light';
    setTheme(savedTheme);
    document.getElementById('themeSelect').value = savedTheme;

    const themeSelect = document.getElementById('themeSelect');
    const newThemes = ['glass-light', 'glass-dark'];
    newThemes.forEach(theme => {
        if (!Array.from(themeSelect.options).some(opt => opt.value === theme)) {
            const option = document.createElement('option');
            option.value = theme;
            option.textContent = theme.charAt(0).toUpperCase() + theme.slice(1);
            themeSelect.appendChild(option);
        }
    });
});

/**
 * Theme change handler
 * @description Updates theme when user selects different theme option
 */
document.getElementById('themeSelect').addEventListener('change', (e) => {
    setTheme(e.target.value);
});

/**
 * API key visibility toggle system
 * @description Handles toggling API key input between password and text visibility
 */
const toggleApiKeyBtn = document.getElementById('toggleApiKey');
const apiKeyInput = document.getElementById('apiKey');

toggleApiKeyBtn.addEventListener('click', () => {
    const type = apiKeyInput.type === 'password' ? 'text' : 'password';
    apiKeyInput.type = type;
    toggleApiKeyBtn.innerHTML = `<i class="fas fa-eye${type === 'password' ? '' : '-slash'}"></i>`;
});

/**
 * Custom endpoint configuration visibility
 * @description Shows/hides custom endpoint fields based on model selection
 */
document.getElementById('modelSelect').addEventListener('change', function() {
    const customEndpointConfig = document.getElementById('customEndpointConfig');
    if (this.value === 'custom') {
        customEndpointConfig.classList.remove('hidden');
    } else {
        customEndpointConfig.classList.add('hidden');
    }
});

/**
 * Keyboard shortcut input handler
 * @description Captures and formats keyboard shortcut combinations
 */
const shortcutInput = document.getElementById('shortcutInput');
shortcutInput.addEventListener('keydown', (event) => {
    event.preventDefault();
    const keys = [];
    if (event.ctrlKey) keys.push('Ctrl');
    if (event.altKey) keys.push('Alt');
    if (event.shiftKey) keys.push('Shift');
    if (event.metaKey) keys.push('Meta');
    if (event.key && !['Control', 'Alt', 'Shift', 'Meta'].includes(event.key)) {
        if (event.key === ' ' || event.key === 'Space') {
            keys.push('Space');
        } else {
            keys.push(event.key.charAt(0).toUpperCase() + event.key.slice(1));
        }
    }
    shortcutInput.value = keys.join('+');
});

/**
 * Configuration form submission handler
 * @description Processes and saves configuration data to server API
 */
document.getElementById('submitConfig').addEventListener('click', () => {
    const apiKey = apiKeyInput.value.trim();
    const selectedModel = document.getElementById('modelSelect').value;
    const selectedTheme = document.getElementById('themeSelect').value;
    const shortcut = shortcutInput.value.trim();

    const config = {
        api_key: apiKey,
        model: selectedModel,
        theme: selectedTheme,
        shortcut: shortcut
    };

    if (selectedModel === 'custom') {
        config.custom_endpoint_url = document.getElementById('customEndpointUrl').value.trim();
        config.custom_endpoint_model = document.getElementById('customEndpointModel').value.trim();
        config.custom_endpoint_style = document.getElementById('customEndpointStyle').value;
    }

    fetch('/api/config', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(config)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            window.location.reload();
        } else {
            alert('Erreur lors de la sauvegarde de la configuration');
        }
    })
    .catch(error => {
        alert('Erreur lors de la sauvegarde de la configuration');
    });
});
