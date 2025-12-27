/**
 * Initialize theme settings and apply immediately
 * @description Sets up theme configuration using localStorage or defaults to light theme
 */
const savedTheme = localStorage.getItem('theme') || 'light';
document.documentElement.setAttribute('data-theme', savedTheme);
localStorage.setItem('theme', savedTheme);

/**
 * Initialize Animate On Scroll library
 * @description Configures AOS for smooth scroll animations with custom settings
 */
AOS.init({
    duration: 800,
    once: true,
    easing: 'ease-out-cubic'
});

/**
 * Initialize WebChannel for desktop application integration
 * @description Sets up communication bridge between JavaScript and Python backend
 */
let pywebview = null;

if (typeof QWebChannel !== 'undefined' && typeof qt !== 'undefined' && qt.webChannelTransport) {
    new QWebChannel(qt.webChannelTransport, function (channel) {
        pywebview = channel.objects.pywebview;

        pywebview.clipboard_text_signal.connect(function(clipboardText) {
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
 * Initialize theme loading and pagination system
 * @description Sets up theme configuration from server and handles mode page navigation
 */
document.addEventListener('DOMContentLoaded', function () {
    fetch('/api/config')
        .then(response => response.json())
        .then(data => {
            if (data.theme) {
                setTheme(data.theme);
            }
        });

    const pages = document.querySelectorAll('[id^="modePage"]');
    const totalPages = pages.length;
    document.getElementById('totalPages').textContent = totalPages;

    let currentPage = 1;

    /**
     * Update visibility of mode pages based on current page
     * @description Shows current page and hides others, updates page counter
     */
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

    const prevPageBtn = document.getElementById('prevPage');
    const nextPageBtn = document.getElementById('nextPage');

    if (prevPageBtn) {
        prevPageBtn.addEventListener('click', () => {
            currentPage = currentPage === 1 ? totalPages : currentPage - 1;
            updatePageVisibility();
        });
    }

    if (nextPageBtn) {
        nextPageBtn.addEventListener('click', () => {
            currentPage = currentPage === totalPages ? 1 : currentPage + 1;
            updatePageVisibility();
        });
    }

    updatePageVisibility();
});
/**
 * Mode selection system
 * @description Handles mode button clicks and manages response section visibility
 */
const modeButtons = document.querySelectorAll('.mode-button');
const selectedModeInput = document.getElementById('selectedMode');

if (modeButtons.length > 0 && selectedModeInput) {
    modeButtons.forEach(button => {
        button.addEventListener('click', () => {
            modeButtons.forEach(btn => btn.classList.remove('active'));
            button.classList.add('active');
            selectedModeInput.value = button.dataset.mode;

            if (button.dataset.mode === 'repondre') {
                const responseSection = document.getElementById('response-section');
                if (responseSection) responseSection.classList.remove('hidden');
            } else {
                const responseSection = document.getElementById('response-section');
                if (responseSection) responseSection.classList.add('hidden');
            }
        });
    });
}

/**
 * Text processing system
 * @description Handles form submission, streaming responses, and result display
 */
const submitBtn = document.getElementById('submit-btn');
const loading = document.getElementById('loading');
const result = document.getElementById('result');
const resultText = document.getElementById('result-text');
const copyButton = document.getElementById('copy-button');
const inputText = document.getElementById('input_text');

if (submitBtn) {
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
                    const rawData = line.slice(6);
                    if (rawData === '[END]') {
                        submitBtn.disabled = false;
                        AOS.refresh();
                        document.getElementById('result-buttons').classList.remove('hidden');
                        return;
                    }
                    try {
                        const jsonData = JSON.parse(rawData);
                        const htmlContent = jsonData.replace(/\n/g, '<br>');
                        resultText.innerHTML = htmlContent;

                    } catch (e) {
                        const htmlContent = rawData.replace(/\n/g, '<br>');
                        resultText.innerHTML = htmlContent;
                    }
                }
            }
        }
    } catch (error) {
        if (loading) loading.classList.add('hidden');
        if (submitBtn) submitBtn.disabled = false;
        alert('Une erreur est survenue lors du traitement.');
    }
});
}

/**
 * Handle back button functionality
 * @description Restores input text from results and shows input area
 */
const backButton = document.getElementById('back-button');
if (backButton) {
    backButton.addEventListener('click', function () {
        if (result) result.classList.add('hidden');
        const resultButtons = document.getElementById('result-buttons');
        if (resultButtons) resultButtons.classList.add('hidden');
        if (inputText && resultText) inputText.value = resultText.textContent;
        if (inputText && inputText.parentElement) inputText.parentElement.classList.remove('hidden');
        updateSubmitButton();
    });
}

/**
 * Handle close result button functionality
 * @description Closes result view and returns to input area
 */
const closeResultBtn = document.getElementById('close-result');
if (closeResultBtn) {
    closeResultBtn.addEventListener('click', function () {
        if (result) result.classList.add('hidden');
        const resultButtons = document.getElementById('result-buttons');
        if (resultButtons) resultButtons.classList.add('hidden');
        if (inputText && inputText.parentElement) inputText.parentElement.classList.remove('hidden');
        updateSubmitButton();
    });
}

/**
 * Copy to clipboard functionality
 * @description Converts HTML content to plain text and copies to clipboard via server API
 */
if (copyButton) {
    copyButton.addEventListener('click', function () {
        if (!resultText) return;

        const resultHtml = resultText.innerHTML;
        const textToCopy = resultHtml.replace(/<br\s*\/?>/gi, '\n');

        fetch('/copy', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ text: textToCopy })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                copyButton.innerHTML = '<i class="fas fa-check mr-2"></i>Copié !';
                setTimeout(() => {
                    copyButton.innerHTML = '<i class="fas fa-copy mr-2"></i>Copier';
            }, 2000);
        } else {
            copyButton.innerHTML = '<i class="fas fa-times mr-2"></i>Erreur';
            setTimeout(() => {
                copyButton.innerHTML = '<i class="fas fa-copy mr-2"></i>Copier';
            }, 2000);
        }
    })
    .catch(error => {
        copyButton.innerHTML = '<i class="fas fa-times mr-2"></i>Erreur';
        setTimeout(() => {
            copyButton.innerHTML = '<i class="fas fa-copy mr-2"></i>Copier';
        }, 2000);
    });
});
}

/**
 * Initialize default mode on page load
 * @description Sets up default correction mode when page loads
 */
document.addEventListener('DOMContentLoaded', function () {
    const defaultModeButton = document.querySelector('[data-mode="corriger"]');
    if (defaultModeButton) {
        defaultModeButton.classList.add('active');
    }
});

/**
 * Show themed alert dialog
 * @param {string} title - Alert title
 * @param {string} text - Alert message
 * @param {string} icon - Alert icon type
 * @param {boolean} showCancelButton - Whether to show cancel button
 * @returns {Promise} SweetAlert2 promise
 * @description Displays themed alert with appropriate styling based on current theme
 */
function showAlert(title, text, icon, showCancelButton = false) {
    const isGlassTheme = document.documentElement.getAttribute('data-theme').includes('glass');
    const isDarkTheme = document.documentElement.getAttribute('data-theme') === 'dark' ||
                       document.documentElement.getAttribute('data-theme') === 'glass-dark';

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

/**
 * Show success alert helper
 * @description Displays success message with predefined text
 */
function showSuccessAlert() {
    showAlert('Succès', 'Configuration sauvegardée avec succès !', 'success');
}

/**
 * Show error alert helper
 * @description Displays error message with predefined text
 */
function showErrorAlert() {
    showAlert('Erreur', 'Erreur lors de la sauvegarde de la configuration', 'error');
}

/**
 * Microphone button click handler
 * @description Validates OpenAI model usage and triggers audio file selection
 */
const microphoneBtn = document.getElementById('microphone-btn');
if (microphoneBtn) {
    microphoneBtn.addEventListener('click', function () {
        const modelSelect = document.getElementById('modelSelect');

        if (!modelSelect) {
            const audioFile = document.getElementById('audio-file');
            if (audioFile) audioFile.click();
            return;
        }

        const selectedProvider = modelSelect.options[modelSelect.selectedIndex].value;

        if (!selectedProvider.includes('gpt') && selectedProvider !== 'custom') {
            showAlert(
                'Fonctionnalité non disponible',
                'La transcription audio nécessite une clé API OpenAI.',
                'warning'
            );
            return;
        }

        const audioFile = document.getElementById('audio-file');
        if (audioFile) audioFile.click();
    });
}

/**
 * Handle audio file upload and transcription
 * @param {HTMLInputElement} input - File input element containing audio file
 * @description Processes audio file upload and handles transcription workflow
 */
function handleAudioFile(input) {
    if (input.files && input.files[0]) {
        const file = input.files[0];

        const formData = new FormData();
        formData.append('audio', file);

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

/**
 * Configuration deletion system
 * @description Handles configuration reset with confirmation dialog
 */
const deleteConfigBtn = document.getElementById('deleteConfig');

if (deleteConfigBtn) {
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
                    api_key: '',
                    model: 'gemini-1.5-flash'
                })
            })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        apiKeyInput.value = '';
                        document.getElementById('modelSelect').value = 'gemini-1.5-flash';
                        sidebar.classList.add('translate-x-full');
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
}
