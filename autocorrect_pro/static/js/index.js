// Appliquer le thème immédiatement
const savedTheme = localStorage.getItem('theme') || 'light';
document.documentElement.setAttribute('data-theme', savedTheme);
localStorage.setItem('theme', savedTheme);

// Initialisation AOS
AOS.init({
    duration: 800,
    once: true,
    easing: 'ease-out-cubic'
});

// Initialisation du WebChannel
let pywebview = null;

new QWebChannel(qt.webChannelTransport, function (channel) {
    pywebview = channel.objects.pywebview;

    // Connecter le signal clipboard_text_signal
    pywebview.clipboard_text_signal.connect(function(clipboardText) {
        // Afficher une alerte demandant si on veut écraser le texte
        showAlert(
            'Nouveau texte dans le presse-papiers',
            'Voulez-vous écraser le texte actuel par le contenu du presse-papiers ?',
            'question',
            true
        ).then((result) => {
            if (result.isConfirmed) {
                document.getElementById('input_text').value = clipboardText;
            }
        });
    });
});

function setTheme(theme) {
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('theme', theme);
}

// CHARGEMENT DU THEME
document.addEventListener('DOMContentLoaded', function () {
    // Charger la configuration initiale
    fetch('/api/config')
        .then(response => response.json())
        .then(data => {
            if (data.theme) {
                setTheme(data.theme);
            }
        });

    // Gestion de la pagination
    const pages = document.querySelectorAll('[id^="modePage"]');
    const totalPages = pages.length;
    document.getElementById('totalPages').textContent = totalPages;

    let currentPage = 1;

    function updatePageVisibility() {
        pages.forEach(page => {
            if (page.id === `modePage${currentPage}`) {
                page.classList.remove('hidden');
            } else {
                page.classList.add('hidden');
            }
        });
        document.getElementById('currentPage').textContent = currentPage;
    }

    document.getElementById('prevPage').addEventListener('click', () => {
        currentPage = currentPage === 1 ? totalPages : currentPage - 1;
        updatePageVisibility();
    });

    document.getElementById('nextPage').addEventListener('click', () => {
        currentPage = currentPage === totalPages ? 1 : currentPage + 1;
        updatePageVisibility();
    });

    // Initialisation
    updatePageVisibility();
});
// Sélection du mode
const modeButtons = document.querySelectorAll('.mode-button');
const selectedModeInput = document.getElementById('selectedMode');

modeButtons.forEach(button => {
    button.addEventListener('click', () => {
        modeButtons.forEach(btn => btn.classList.remove('active'));
        button.classList.add('active');
        selectedModeInput.value = button.dataset.mode;

        // Afficher ou masquer la section de réponse en fonction du mode
        if (button.dataset.mode === 'repondre') {
            document.getElementById('response-section').classList.remove('hidden');
        } else {
            document.getElementById('response-section').classList.add('hidden');
        }
    });
});

// Traitement du texte
const submitBtn = document.getElementById('submit-btn');
const loading = document.getElementById('loading');
const result = document.getElementById('result');
const resultText = document.getElementById('result-text');
const copyButton = document.getElementById('copy-button');
const inputText = document.getElementById('input_text');

submitBtn.addEventListener('click', async function (e) {
    e.preventDefault();
    submitBtn.disabled = true;
    loading.classList.remove('hidden');
    result.classList.add('hidden');
    resultText.innerHTML = '';

    const formData = new FormData();
    formData.append('mode', selectedModeInput.value);
    formData.append('input_text', inputText.value);

    if (selectedModeInput.value === 'repondre') {
        const userResponse = document.getElementById('response_text').value;
        formData.append('user_response', userResponse);
    }

    try {
        const response = await fetch('/process', {
            method: 'POST',
            body: formData
        });

        loading.classList.add('hidden');
        result.classList.remove('hidden');

        const reader = response.body.getReader();
        const decoder = new TextDecoder();

        while (true) {
            const {value, done} = await reader.read();
            if (done) break;

            const chunk = decoder.decode(value);
            const lines = chunk.split('\n');

            for (const line of lines) {
                if (line.startsWith('data: ')) {
                    const rawData = line.slice(6); // Get the raw data string
                    if (rawData === '[END]') {
                        submitBtn.disabled = false;
                        AOS.refresh();
                        document.getElementById('result-buttons').classList.remove('hidden');
                        return; // Exit the loop
                    }
                    try {
                        // Parse the JSON data received from the server
                        const jsonData = JSON.parse(rawData);
                        console.log("Received data:", jsonData); // Now jsonData is the actual string

                        // Replace \n with <br> for HTML rendering using the parsed string
                        const htmlContent = jsonData.replace(/\n/g, '<br>');
                        resultText.innerHTML = htmlContent;

                    } catch (e) {
                        console.error("Failed to parse JSON data:", rawData, e);
                        // Fallback for non-JSON data (like the error message or [END])
                        // or if the server didn't send JSON for some reason
                        const htmlContent = rawData.replace(/\n/g, '<br>');
                        resultText.innerHTML = htmlContent;
                    }
                }
            }
        }
    } catch (error) {
        console.error('Fetch error:', error);
        loading.classList.add('hidden');
        submitBtn.disabled = false;
        alert('Une erreur est survenue lors du traitement.');
    }
});

// Gestion du bouton "Retour"
document.getElementById('back-button').addEventListener('click', function () {
    result.classList.add('hidden');
    document.getElementById('result-buttons').classList.add('hidden');
    inputText.value = resultText.textContent;
    inputText.parentElement.classList.remove('hidden');
    updateSubmitButton();
});

// Gestion du bouton de fermeture
document.getElementById('close-result').addEventListener('click', function () {
    result.classList.add('hidden');
    document.getElementById('result-buttons').classList.add('hidden');
    inputText.parentElement.classList.remove('hidden');
    updateSubmitButton();
});

// Copie dans le presse-papiers
copyButton.addEventListener('click', function () {
// --- MODIFICATION ICI ---
// 1. Récupérer le contenu HTML de la zone de résultat
const resultHtml = resultText.innerHTML;

// 2. Remplacer toutes les occurrences de <br> (et ses variantes) par \n

//    Le regex /<br\s*\/?>/gi gère <br>, <br/>, <br />, insensible à la casse (i) et globalement (g)
const textToCopy = resultHtml.replace(/<br\s*\/?>/gi, '\n');
// --- FIN MODIFICATION ---

console.log("Text being sent to /copy:", JSON.stringify(textToCopy)); // Pour déboguer

fetch('/copy', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
    },
    body: JSON.stringify({ text: textToCopy }) // Envoie le texte avec les \n reconstruits
})
.then(response => response.json())
.then(data => {
    if (data.success) {
        copyButton.innerHTML = '<i class="fas fa-check mr-2"></i>Copié !';
        setTimeout(() => {
            copyButton.innerHTML = '<i class="fas fa-copy mr-2"></i>Copier';
        }, 2000);
    } else {
        console.error("Copy failed:", data.error);
        copyButton.innerHTML = '<i class="fas fa-times mr-2"></i>Erreur';
         setTimeout(() => {
            copyButton.innerHTML = '<i class="fas fa-copy mr-2"></i>Copier';
        }, 2000);
    }
})
.catch(error => {
     console.error("Copy request failed:", error);
     copyButton.innerHTML = '<i class="fas fa-times mr-2"></i>Erreur';
     setTimeout(() => {
        copyButton.innerHTML = '<i class="fas fa-copy mr-2"></i>Copier';
     }, 2000);
});
});

// Initialisation au chargement de la page
document.addEventListener('DOMContentLoaded', function () {
    // Activation du mode "corriger" par défaut
    const defaultModeButton = document.querySelector('[data-mode="corriger"]');
    if (defaultModeButton) {
        defaultModeButton.classList.add('active');
    }
});

// On Alerte JS avec thème
function showAlert(title, text, icon, showCancelButton = false) {
    const isGlassTheme = document.documentElement.getAttribute('data-theme').includes('glass');
    const isDarkTheme = document.documentElement.getAttribute('data-theme') === 'dark' || 
                       document.documentElement.getAttribute('data-theme') === 'glass-dark';

    // Use default styles for glass themes
    if (isGlassTheme) {
        return Swal.fire({
            title: title,
            text: text,
            icon: icon,
            showCancelButton: showCancelButton,
            confirmButtonColor: '#6366f1',
            cancelButtonColor: '#f87171',
            confirmButtonText: 'OK',
            cancelButtonText: 'Annuler'
        });
    }

    // Use custom classes for non-glass themes
    return Swal.fire({
        title: title,
        text: text,
        icon: icon,
        showCancelButton: showCancelButton,
        confirmButtonColor: '#6366f1',
        cancelButtonColor: '#f87171',
        confirmButtonText: 'OK',
        cancelButtonText: 'Annuler',
        customClass: isDarkTheme ? {
            popup: 'swal2-dark',
            title: 'swal2-title-dark',
            content: 'swal2-content-dark',
            confirmButton: 'swal2-confirm-dark',
            cancelButton: 'swal2-cancel-dark'
        } : {
            popup: 'swal2-light',
            title: 'swal2-title-light',
            content: 'swal2-content-light',
            confirmButton: 'swal2-confirm-light',
            cancelButton: 'swal2-cancel-light'
        }
    });
}

// Utilisation pour une alerte de succès
function showSuccessAlert() {
    showAlert('Succès', 'Configuration sauvegardée avec succès !', 'success');
}

// Utilisation pour une alerte d'erreur
function showErrorAlert() {
    showAlert('Erreur', 'Erreur lors de la sauvegarde de la configuration', 'error');
}

document.getElementById('microphone-btn').addEventListener('click', function () {
    // Vérifier d'abord si on utilise OpenAI
    const modelSelect = document.getElementById('modelSelect');
    const selectedProvider = modelSelect.options[modelSelect.selectedIndex].value;

    if (!selectedProvider.includes('gpt') && selectedProvider !== 'custom') {
        showAlert(
            'Fonctionnalité non disponible',
            'La transcription audio nécessite une clé API OpenAI.',
            'warning'
        );
        return;
    }

    document.getElementById('audio-file').click();
});

function handleAudioFile(input) {
    if (input.files && input.files[0]) {
        const file = input.files[0];

        // Créer un FormData pour envoyer le fichier
        const formData = new FormData();
        formData.append('audio', file);

        // Montrer un indicateur de chargement
        Swal.fire({
            title: 'Transcription en cours',
            text: 'Veuillez patienter pendant la transcription du fichier audio...', 
            icon: 'info',
            allowOutsideClick: false,
            showConfirmButton: false,
            willOpen: () => {
                Swal.showLoading();
            }
        });

        // Envoyer le fichier au serveur
        fetch('/transcribe', {
            method: 'POST',
            body: formData
        })
            .then(response => response.json())
            .then(data => {
                Swal.close();
                if (data.success) {
                    document.getElementById('input_text').value = data.text;
                    showAlert(
                        'Succès',
                        'Transcription terminée !',
                        'success'
                    );
                } else {
                    showAlert(
                        'Erreur',
                        data.error || 'Erreur lors de la transcription',
                        'error'
                    );
                }
            })
            .catch(error => {
                Swal.close();
                showAlert(
                    'Erreur',
                    'Erreur lors de la transcription: ' + error,
                    'error'
                );
            });
    }
}

// Gestion de la suppression de la configuration
const deleteConfigBtn = document.getElementById('deleteConfig');

deleteConfigBtn.addEventListener('click', () => {
    showAlert(
        'Êtes-vous sûr ?',
        "Cela supprimera votre clé API et réinitialisera le modèle.",
        'warning',
        true
    ).then((result) => {
        if (result.isConfirmed) {
            fetch('/api/config', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    api_key: '', // Réinitialiser la clé API
                    model: 'gemini-1.5-flash' // Réinitialiser au modèle par défaut
                })
            })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        // Réinitialiser les champs
                        apiKeyInput.value = '';
                        document.getElementById('modelSelect').value = 'gemini-1.5-flash';

                        // Fermer la sidebar
                        sidebar.classList.add('translate-x-full');

                        // Potentiellement recharger la page pour montrer l'écran de configuration
                        window.location.reload();
                    } else {
                        Swal.fire({
                            icon: 'error',
                            title: 'Erreur',
                            text: 'Erreur lors de la suppression de la configuration',
                            confirmButtonColor: '#f87171'
                        });
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    Swal.fire({
                        icon: 'error',
                        title: 'Erreur',
                        text: 'Erreur lors de la suppression de la configuration',
                        confirmButtonColor: '#f87171'
                    });
                });
        }
    });
});
