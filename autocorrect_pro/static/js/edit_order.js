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

/**
 * Icon selection grid setup
 * @description Creates and manages icon selection interface for custom modes
 */
const icons = [
    'fa-language', 'fa-spell-check', 'fa-star', 'fa-magic', 'fa-pen',
    'fa-book', 'fa-comment', 'fa-lightbulb', 'fa-check', 'fa-edit',
    'fa-compress-alt', 'fa-expand-alt', 'fa-robot', 'fa-brain', 'fa-cog'
];

const iconGrid = document.getElementById('iconGrid');
if (iconGrid) {
    icons.forEach(icon => {
        const button = document.createElement('button');
        button.type = 'button';
        button.className = 'icon-button p-3 rounded-lg hover:bg-indigo-100 dark:hover:bg-gray-700 dark:text-gray-200 transition-colors';
        button.innerHTML = `<i class="fas ${icon} text-xl"></i>`;
        button.dataset.icon = icon;
        button.onclick = (e) => {
            e.preventDefault();
            document.querySelectorAll('.icon-button').forEach(btn =>
                btn.classList.remove('bg-indigo-100', 'dark:bg-gray-700'));
            button.classList.add('bg-indigo-100', 'dark:bg-gray-700');
            document.getElementById('selectedIconInput').value = icon;
        };
        iconGrid.appendChild(button);
    });
}

/**
 * Load and display custom and system modes
 * @description Fetches modes from API and renders them in management interface
 */
async function loadModes() {
    try {
        const response = await fetch('/api/modes');
        const data = await response.json();
        const modesList = document.getElementById('modesList');
        const orderModesList = document.getElementById('orderModesList');

        if (!modesList || !orderModesList) {
            return;
        }

        modesList.innerHTML = '';
        orderModesList.innerHTML = '';

        const orderedModes = {};

        if (data.order) {
            data.order.forEach(modeId => {
                if (data.custom && data.custom[modeId]) {
                    orderedModes[modeId] = data.custom[modeId];
                } else if (data.system && data.system[modeId]) {
                    orderedModes[modeId] = data.system[modeId];
                }
            });
        }
        if (data.custom) {
            Object.entries(data.custom).forEach(([id, mode]) => {
                if (!orderedModes[id]) {
                    orderedModes[id] = mode;
                }
            });
        }

        if (data.system) {
            Object.entries(data.system).forEach(([id, mode]) => {
                if (!orderedModes[id]) {
                    orderedModes[id] = mode;
                }
            });
        }

        if (data.custom) {
            Object.entries(data.custom).forEach(([id, mode]) => {
                const modeElement = document.createElement('div');
                modeElement.className = 'border rounded-lg overflow-hidden mb-4';
                modeElement.innerHTML = `
                    <div class="flex items-center justify-between p-4 cursor-pointer mode-header"
                         onclick="toggleModeDetails('${id}')">
                        <div class="flex items-center">
                            <i class="fas ${mode.icon} text-xl text-indigo-500 mr-3"></i>
                            <span class="font-medium text-gray-700">${mode.title}</span>
                        </div>
                        <div class="flex items-center space-x-2">
                            <button onclick="editMode('${id}', event)"
                                    class="text-indigo-500  p-2">
                                <i class="fas fa-edit"></i>
                            </button>
                            <button onclick="deleteMode('${id}', event)"
                                    class="text-red-500 hover:text-red-700 p-2">
                                <i class="fas fa-trash"></i>
                            </button>
                            <i class="fas fa-chevron-down text-gray-400 transition-transform duration-300"></i>
                        </div>
                    </div>
                    <div id="mode-details-${id}" class="hidden">
                        <div class="p-4 border-t bg-white" data-theme="light">
                            <div class="mb-2">
                                <label class="block text-sm font-medium text-gray-800 mb-2">
                                    Instructions pour l'IA
                                </label>
                                <div class="relative">
                                    <textarea id="prompt-${id}"
                                              class="w-full px-4 py-2 border rounded-lg bg-white text-gray-900 focus:ring-2 focus:ring-indigo-200 focus:border-indigo-400 resize-none"
                                              rows="6"
                                              readonly
                                    >${mode.prompt}</textarea>
                                    <button onclick="toggleEdit('${id}')"
                                            class="absolute top-2 right-2 text-indigo-500 hover:text-indigo-700 bg-white rounded-full p-2 shadow-sm"
                                            style="background-color: var(--bg-secondary)">
                                        <i id="edit-icon-${id}" class="fas fa-lock"></i>
                                    </button>
                                </div>
                            </div>
                            <div class="flex justify-end space-x-2 mt-4">
                                <button onclick="cancelEdit('${id}')"
                                        id="cancel-${id}"
                                        class="hidden px-4 py-2 bg-gray-500 text-white rounded-lg hover:bg-gray-600 dark:bg-gray-600 dark:hover:bg-gray-700">
                                    Annuler
                                </button>
                                <button onclick="savePrompt('${id}')"
                                        id="save-${id}"
                                        class="hidden px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 dark:bg-indigo-700 dark:hover:bg-indigo-800">
                                    Sauvegarder
                                </button>
                            </div>
                        </div>
                    </div>
                `;
                modesList.appendChild(modeElement);

                const orderModeElement = document.createElement('div');
                orderModeElement.className = 'p-4 rounded-lg flex items-center justify-between';
                orderModeElement.style.backgroundColor = 'var(--bg-secondary)';
                orderModeElement.style.boxShadow = '0 4px 6px -1px var(--shadow-color), 0 2px 4px -1px var(--shadow-color)';
                orderModeElement.dataset.id = id;
                orderModeElement.innerHTML = `
                    <div class="flex items-center">
                        <i class="fas ${mode.icon} text-xl mr-3" style="color: var(--indigo-primary)"></i>
                        <span class="font-medium" style="color: var(--text-primary)">${mode.title}</span>
                    </div>
                    <div class="flex items-center space-x-3">
                        <button onclick="deleteMode('${id}', event)"
                                class="text-red-500 hover:text-red-700 transition-colors">
                            <i class="fas fa-trash"></i>
                        </button>
                        <i class="fas fa-grip-vertical text-gray-400 cursor-move"></i>
                    </div>
                `;
                orderModesList.appendChild(orderModeElement);
            });
        }

        Object.entries(orderedModes).forEach(([id, mode]) => {
            const orderModeElement = document.createElement('div');
            orderModeElement.className = 'p-4 rounded-lg flex items-center justify-between';
            orderModeElement.style.backgroundColor = 'var(--bg-secondary)';
            orderModeElement.style.boxShadow = '0 4px 6px -1px var(--shadow-color), 0 2px 4px -1px var(--shadow-color)';
            orderModeElement.dataset.id = id;

            const isCustomMode = data.custom && data.custom[id];

            orderModeElement.innerHTML = `
                <div class="flex items-center">
                    <i class="fas ${mode.icon} text-xl mr-3" style="color: var(--indigo-primary)"></i>
                    <span class="font-medium" style="color: var(--text-primary)">${mode.title}</span>
                </div>
                <div class="flex items-center space-x-3">
                    ${isCustomMode ? `
                        <button onclick="deleteMode('${id}', event)"
                                class="text-red-500 hover:text-red-700 transition-colors">
                            <i class="fas fa-trash"></i>
                        </button>
                    ` : ''}
                    <i class="fas fa-grip-vertical text-gray-400 cursor-move"></i>
                </div>
            `;
            orderModesList.appendChild(orderModeElement);
        });

        new Sortable(orderModesList, {
            animation: 150,
            ghostClass: 'bg-indigo-50'
        });

    } catch (error) {
        console.error('Erreur lors du chargement des modes:', error);
    }
}

/**
 * Toggle mode details visibility
 * @param {string} modeId - ID of the mode to toggle
 * @description Shows/hides detailed view of mode with animation
 */
function toggleModeDetails(modeId) {
    const details = document.getElementById(`mode-details-${modeId}`);
    const chevron = details.previousElementSibling.querySelector('.fa-chevron-down');

    if (details.classList.contains('hidden')) {
        details.classList.remove('hidden');
        chevron.style.transform = 'rotate(180deg)';
    } else {
        details.classList.add('hidden');
        chevron.style.transform = 'rotate(0deg)';
    }
}

/**
 * Custom mode form submission handler
 * @description Processes form data for creating new custom modes
 */
const customModeForm = document.getElementById('customModeForm');
if (customModeForm) {
    customModeForm.addEventListener('submit', async function (e) {
        e.preventDefault();

        const formData = {
            title: document.getElementById('title').value,
            icon: document.getElementById('selectedIconInput').value,
            prompt: document.getElementById('prompt').value
        };

        try {
            const response = await fetch('/api/modes', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(formData)
            });

            const data = await response.json();

            if (data.success) {
                await loadModes();
                this.reset();
                document.querySelectorAll('.icon-button').forEach(btn =>
                    btn.classList.remove('bg-indigo-100'));

                Swal.fire('Succès', 'Mode créé avec succès !', 'success');
            } else {
                throw new Error(data.error || 'Erreur lors de la création du mode');
            }
        } catch (error) {
            Swal.fire('Erreur', error.message, 'error');
        }
    });
}

/**
 * Save mode order handler
 * @description Updates the order of modes based on user rearrangement
 */
const saveOrderBtn = document.getElementById('saveOrderBtn');
if (saveOrderBtn) {
    saveOrderBtn.addEventListener('click', async function () {
        const orderModesList = document.getElementById('orderModesList');
        if (!orderModesList) return;

        const newOrder = Array.from(orderModesList.children).map(el => el.dataset.id);

        try {
            const response = await fetch('/api/modes', {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({order: newOrder})
            });

            const data = await response.json();

            if (data.success) {
                Swal.fire('Succès', 'L\'ordre des modes a été sauvegardé !', 'success');
            } else {
                throw new Error(data.error || 'Erreur lors de la sauvegarde');
            }
        } catch (error) {
            Swal.fire('Erreur', error.message, 'error');
        }
    });
}

/**
 * Tab management system
 * @description Handles tab switching between custom modes and order management
 */
const tabCustom = document.getElementById('tabCustom');
const tabOrder = document.getElementById('tabOrder');

if (tabCustom && tabOrder) {
    tabCustom.addEventListener('click', function () {
        this.classList.add('active');
        tabOrder.classList.remove('active');

        const customModeSection = document.getElementById('customModeSection');
        const orderModeSection = document.getElementById('orderModeSection');

        if (customModeSection) customModeSection.classList.remove('hidden');
        if (orderModeSection) orderModeSection.classList.add('hidden');
    });

    tabOrder.addEventListener('click', function () {
        this.classList.add('active');
        tabCustom.classList.remove('active');

        const customModeSection = document.getElementById('customModeSection');
        const orderModeSection = document.getElementById('orderModeSection');

        if (orderModeSection) orderModeSection.classList.remove('hidden');
        if (customModeSection) customModeSection.classList.add('hidden');
    });
}

/**
 * Initialize modes on page load
 * @description Loads all modes when the page loads
 */
loadModes();