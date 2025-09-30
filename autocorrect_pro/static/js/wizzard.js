let currentStep = 1;

function nextStep(step) {
    document.querySelectorAll('.fade-in').forEach(el => el.classList.add('hidden'));
    document.getElementById(`step${step}`).classList.remove('hidden');
    currentStep = step;
    document.getElementById('currentStep').innerText = currentStep;
}

function prevStep(step) {
    nextStep(step);
}

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

// Fonction pour définir le thème
function setTheme(theme) {
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('theme', theme);
}

// Charger le thème sauvegardé
document.addEventListener('DOMContentLoaded', () => {
    const savedTheme = localStorage.getItem('theme') || 'light';
    setTheme(savedTheme);
    document.getElementById('themeSelect').value = savedTheme;
            
    // Ajouter les nouveaux thèmes s'ils ne sont pas déjà présents
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

// Écouteur pour le changement de thème
document.getElementById('themeSelect').addEventListener('change', (e) => {
    setTheme(e.target.value);
});

// Toggle visibilité clé API
const toggleApiKeyBtn = document.getElementById('toggleApiKey');
const apiKeyInput = document.getElementById('apiKey');

toggleApiKeyBtn.addEventListener('click', () => {
    const type = apiKeyInput.type === 'password' ? 'text' : 'password';
    apiKeyInput.type = type;
    toggleApiKeyBtn.innerHTML = `<i class="fas fa-eye${type === 'password' ? '' : '-slash'}"></i>`;
});

// Gestion de l'affichage des champs d'endpoint personnalisé
document.getElementById('modelSelect').addEventListener('change', function() {
    const customEndpointConfig = document.getElementById('customEndpointConfig');
    if (this.value === 'custom') {
        customEndpointConfig.classList.remove('hidden');
    } else {
        customEndpointConfig.classList.add('hidden');
    }
});

// Gestion du raccourci clavier
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

// Soumission du formulaire
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

    // Utiliser la même structure que dans index.html
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
        console.error('Error:', error);
        alert('Erreur lors de la sauvegarde de la configuration');
    });
});
