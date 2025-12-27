/**
 * Initialize settings page
 * @description Loads existing configuration and sets up event listeners
 */
document.addEventListener('DOMContentLoaded', function() {
    fetch('/api/config')
        .then(response => response.json())
        .then(config => {
            document.getElementById('apiKey').value = config.api_key || '';
            document.getElementById('modelSelect').value = config.model || 'gemini-1.5-flash';
            document.getElementById('shortcutInput').value = config.shortcut;
            document.getElementById('themeSelect').value = config.theme || 'light';

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

            if (config.custom_endpoint) {
                document.getElementById('customEndpointUrl').value = config.custom_endpoint.url || '';
                document.getElementById('customEndpointModel').value = config.custom_endpoint.model_name || '';
                document.getElementById('customEndpointStyle').value = config.custom_endpoint.style || 'openai';
            }

            toggleCustomEndpoint(config.model);
        })
        .catch(error => {
            console.error('Erreur lors du chargement de la configuration:', error);
        });

    /**
     * API key visibility toggle handler
     * @description Toggles API key input field between password and text modes
     */
    document.getElementById('toggleApiKey').addEventListener('click', function() {
        const apiKeyInput = document.getElementById('apiKey');
        const type = apiKeyInput.getAttribute('type') === 'password' ? 'text' : 'password';
        apiKeyInput.setAttribute('type', type);
        this.innerHTML = type === 'password' ? '<i class="fas fa-eye"></i>' : '<i class="fas fa-eye-slash"></i>';
    });

    /**
     * Model selection change handler
     * @description Shows/hides custom endpoint section based on selected model
     */
    document.getElementById('modelSelect').addEventListener('change', function() {
        toggleCustomEndpoint(this.value);
    });

    document.getElementById('saveConfig').addEventListener('click', saveConfiguration);
    document.getElementById('deleteConfig').addEventListener('click', deleteConfiguration);

    /**
     * Keyboard shortcut input handler
     * @description Captures and formats keyboard shortcut combinations with special key handling
     */
    document.getElementById('shortcutInput').addEventListener('keydown', function(e) {
        e.preventDefault();
        const keys = [];

        if (e.ctrlKey) keys.push('Ctrl');
        if (e.altKey) keys.push('Alt');
        if (e.shiftKey) keys.push('Shift');
        if (e.metaKey) keys.push('Meta');

        if (!['Control', 'Alt', 'Shift', 'Meta'].includes(e.key)) {
            if (e.key === ' ') {
                keys.push('Space');
            } else if (e.key.length === 1) {
                keys.push(e.key.toUpperCase());
            } else {
                const specialKeys = {
                    'Escape': 'Esc', 'Tab': 'Tab', 'Enter': 'Enter',
                    'Backspace': 'Backspace', 'Delete': 'Delete',
                    'ArrowUp': 'Up', 'ArrowDown': 'Down',
                    'ArrowLeft': 'Left', 'ArrowRight': 'Right'
                };
                keys.push(specialKeys[e.key] || e.key);
            }

            this.value = keys.join('+');
        }
    });
});

/**
 * Toggle custom endpoint section visibility
 * @param {string} model - Selected model name
 * @description Shows custom endpoint configuration only when 'custom' model is selected
 */
function toggleCustomEndpoint(model) {
    const customSection = document.getElementById('customEndpointConfig');
    customSection.style.display = model === 'custom' ? 'block' : 'none';
}

/**
 * Save configuration to server
 * @description Collects form data and sends it to the server for storage
 */
function saveConfiguration() {
    const apiKey = document.getElementById('apiKey').value;
    const model = document.getElementById('modelSelect').value;
    const shortcut = document.getElementById('shortcutInput').value;
    const theme = document.getElementById('themeSelect').value;
    const customEndpointUrl = document.getElementById('customEndpointUrl').value;
    const customEndpointModel = document.getElementById('customEndpointModel').value;
    const customEndpointStyle = document.getElementById('customEndpointStyle').value;

    fetch('/api/config', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            api_key: apiKey,
            model: model,
            theme: theme,
            shortcut: shortcut,
            custom_endpoint_url: customEndpointUrl,
            custom_endpoint_model: customEndpointModel,
            custom_endpoint_style: customEndpointStyle
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            localStorage.setItem('theme', theme);

            Swal.fire({
                title: 'Succès!',
                text: 'Configuration sauvegardée avec succès',
                icon: 'success',
                confirmButtonColor: '#6366f1'
            }).then(() => {
                window.location.href = "/";
            });
        } else {
            throw new Error(data.error || 'Erreur inconnue');
        }
    })
    .catch(error => {
        Swal.fire({
            title: 'Erreur!',
            text: error.message,
            icon: 'error',
            confirmButtonColor: '#6366f1'
        });
    });
}

/**
 * Delete/reset configuration
 * @description Shows confirmation dialog and resets all configuration settings
 */
function deleteConfiguration() {
    Swal.fire({
        title: 'Êtes-vous sûr?',
        text: "Cette action réinitialisera tous vos paramètres!",
        icon: 'warning',
        showCancelButton: true,
        confirmButtonColor: '#6366f1',
        cancelButtonColor: '#f87171',
        confirmButtonText: 'Oui, réinitialiser!'
    }).then((result) => {
        if (result.isConfirmed) {
            fetch('/api/config', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ api_key: '' })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    Swal.fire({
                        title: 'Réinitialisé!',
                        text: 'Vos paramètres ont été réinitialisés.',
                        icon: 'success',
                        confirmButtonColor: '#6366f1'
                    }).then(() => {
                        window.location.reload();
                    });
                }
            });
        }
    });
}
