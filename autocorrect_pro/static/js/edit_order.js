// Liste des icônes
        const icons = [
            'fa-language', 'fa-spell-check', 'fa-star', 'fa-magic', 'fa-pen',
            'fa-book', 'fa-comment', 'fa-lightbulb', 'fa-check', 'fa-edit',
            'fa-compress-alt', 'fa-expand-alt', 'fa-robot', 'fa-brain', 'fa-cog'
        ];

        // Création de la grille d'icônes
        const iconGrid = document.getElementById('iconGrid');
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

        // Appliquer le thème immédiatement
        const savedTheme = localStorage.getItem('theme') || 'light';
        document.documentElement.setAttribute('data-theme', savedTheme);

        function updateTheme(theme) {
            if (theme === 'dark') {
                document.documentElement.classList.add('dark');
                document.body.classList.remove('bg-slate-50');
                document.body.classList.add('bg-gray-900');
            } else {
                document.documentElement.classList.remove('dark');
                document.body.classList.remove('bg-gray-900');
                document.body.classList.add('bg-slate-50');
            }
        }

        // Gestion du thème
        document.addEventListener('DOMContentLoaded', function () {
            // Observer les changements de thème
            const observer = new MutationObserver(function (mutations) {
                mutations.forEach(function (mutation) {
                    if (mutation.attributeName === 'data-theme') {
                        const theme = document.documentElement.getAttribute('data-theme');
                        updateTheme(theme);
                    }
                });
            });

            observer.observe(document.documentElement, {
                attributes: true,
                attributeFilter: ['data-theme']
            });

            // Appliquer le thème initial
            updateTheme(savedTheme);
        });

        // Fonction pour les alertes avec thème
        function showAlert(title, text, icon, showCancelButton = false) {
            const isDarkTheme = document.documentElement.getAttribute('data-theme') === 'dark';

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
                } : {}
            });
        }

        // Chargement et affichage des modes existants
        async function loadModes() {
            try {
                const response = await fetch('/api/modes');
                const data = await response.json();
                const modesList = document.getElementById('modesList');
                const orderModesList = document.getElementById('orderModesList');
                modesList.innerHTML = '';
                orderModesList.innerHTML = '';

                // Afficher les modes personnalisés
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

                        // Ajouter les modes personnalisés à la liste de réorganisation
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

                // Ajouter les modes système à la liste de réorganisation
                if (data.system) {
                    Object.entries(data.system).forEach(([id, mode]) => {
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
                                <i class="fas fa-grip-vertical text-gray-400 cursor-move"></i>
                            </div>
                        `;
                        orderModesList.appendChild(orderModeElement);
                    });
                }

                // Initialiser Sortable
                new Sortable(orderModesList, {
                    animation: 150,
                    ghostClass: 'bg-indigo-50'
                });

            } catch (error) {
                console.error('Erreur lors du chargement des modes:', error);
                showAlert('Erreur', 'Erreur lors du chargement des modes', 'error');
            }
        }

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

        function toggleEdit(modeId) {
            const textarea = document.getElementById(`prompt-${modeId}`);
            const editIcon = document.getElementById(`edit-icon-${modeId}`);
            const saveBtn = document.getElementById(`save-${modeId}`);
            const cancelBtn = document.getElementById(`cancel-${modeId}`);

            if (textarea.readOnly) {
                textarea.readOnly = false;
                textarea.classList.add('border-indigo-500');
                editIcon.classList.remove('fa-lock');
                editIcon.classList.add('fa-lock-open');
                saveBtn.classList.remove('hidden');
                cancelBtn.classList.remove('hidden');
                textarea.dataset.original = textarea.value;
            } else {
                textarea.readOnly = true;
                textarea.classList.remove('border-indigo-500');
                editIcon.classList.remove('fa-lock-open');
                editIcon.classList.add('fa-lock');
                saveBtn.classList.add('hidden');
                cancelBtn.classList.add('hidden');
            }
        }

        function cancelEdit(modeId) {
            const textarea = document.getElementById(`prompt-${modeId}`);
            textarea.value = textarea.dataset.original;
            toggleEdit(modeId);
        }

        async function savePrompt(modeId) {
            const textarea = document.getElementById(`prompt-${modeId}`);
            const newPrompt = textarea.value;

            try {
                const response = await fetch(`/api/modes/${modeId}`, {
                    method: 'PATCH',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        prompt: newPrompt
                    })
                });

                const data = await response.json();

                if (data.success) {
                    showAlert('Succès', 'Modifications enregistrées', 'success');
                    toggleEdit(modeId);
                } else {
                    throw new Error(data.error || 'Erreur lors de la sauvegarde');
                }
            } catch (error) {
                showAlert('Erreur', error.message, 'error');
            }
        }

        async function deleteMode(modeId, event) {
            if (event) {
                event.stopPropagation();
            }

            const result = await showAlert(
                'Êtes-vous sûr ?',
                "Cette action est irréversible !",
                'warning',
                true
            );

            if (result.isConfirmed) {
                try {
                    const response = await fetch(`/api/modes/${modeId}`, {
                        method: 'DELETE'
                    });
                    const data = await response.json();

                    if (data.success) {
                        await loadModes();
                        showAlert('Supprimé !', 'Le mode a été supprimé.', 'success');
                    } else {
                        throw new Error(data.error);
                    }
                } catch (error) {
                    showAlert('Erreur', error.message, 'error');
                }
            }
        }

        // Gestion du formulaire
        document.getElementById('customModeForm').addEventListener('submit', async function (e) {
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

                    showAlert('Succès', 'Mode créé avec succès !', 'success');
                } else {
                    throw new Error(data.error || 'Erreur lors de la création du mode');
                }
            } catch (error) {
                showAlert('Erreur', error.message, 'error');
            }
        });

        // Gestion de la sauvegarde de l'ordre
        document.getElementById('saveOrderBtn').addEventListener('click', async function () {
            const newOrder = Array.from(document.getElementById('orderModesList').children).map(el => el.dataset.id);

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
                    showAlert('Succès', 'L\'ordre des modes a été sauvegardé !', 'success');
                } else {
                    throw new Error(data.error || 'Erreur lors de la sauvegarde');
                }
            } catch (error) {
                showAlert('Erreur', error.message, 'error');
            }
        });

        // Gestion des onglets améliorée
        document.getElementById('tabCustom').addEventListener('click', function () {
            // Activer l'onglet "Modes"
            this.classList.add('active');
            document.getElementById('tabOrder').classList.remove('active');
            
            // Afficher la section correspondante
            document.getElementById('customModeSection').classList.remove('hidden');
            document.getElementById('orderModeSection').classList.add('hidden');
        });

        document.getElementById('tabOrder').addEventListener('click', function () {
            // Activer l'onglet "Ordre"
            this.classList.add('active');
            document.getElementById('tabCustom').classList.remove('active');
            
            // Afficher la section correspondante
            document.getElementById('orderModeSection').classList.remove('hidden');
            document.getElementById('customModeSection').classList.add('hidden');
        });

        // Charger les modes au chargement de la page
        loadModes();
