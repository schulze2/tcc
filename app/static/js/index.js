document.addEventListener('DOMContentLoaded', () => {
    let registrationEmailAvailable = false;
    let registrationEmailValue = '';

    // Password visibility toggle logic
    window.togglePassword = function (inputId, iconId) {
        const passwordInput = document.getElementById(inputId);
        const eyeIcon = document.getElementById(iconId);

        if (!passwordInput || !eyeIcon) {
            return;
        }

        if (passwordInput.type === 'password') {
            passwordInput.type = 'text';
            eyeIcon.setAttribute('icon', 'lucide:eye-off');
        } else {
            passwordInput.type = 'password';
            eyeIcon.setAttribute('icon', 'lucide:eye');
        }
    };

    // Switch to Registration View
    window.toggleRegister = function (showRegister) {
        const mainCard = document.getElementById('main-card');

        if (!mainCard) {
            return;
        }

        if (showRegister) {
            mainCard.classList.add('is-registering');
        } else {
            mainCard.classList.remove('is-registering');
        }
    };

    // Glow button cursor tracking (ported from Design System)
    document.querySelectorAll('.btn-glow').forEach(btn => {
        btn.addEventListener('mousemove', e => {
            const rect = btn.getBoundingClientRect();
            btn.style.setProperty('--x', `${e.clientX - rect.left}px`);
            btn.style.setProperty('--y', `${e.clientY - rect.top}px`);
        });
    });

    // Disable tilt on smaller screens for better performance and usability
    if (window.innerWidth < 1024) {
        const tiltedElements = document.querySelectorAll('[data-tilt]');
        tiltedElements.forEach(el => {
            if (el.vanillaTilt) {
                el.vanillaTilt.destroy();
            }
        });
    }

    window.validateRegistration = async function () {
        const formCadastro = document.getElementById('formCadastro');
        const pass = document.getElementById('reg-password');
        const confirm = document.getElementById('reg-password-confirm');
        const errorMsg = document.getElementById('reg-password-error');
        const emailErrorMsg = document.getElementById('reg-email-error');
        const emailInput = document.getElementById('reg-email');
        const emailCheckUrl = formCadastro ? formCadastro.dataset.emailCheckUrl : '';

        if (!formCadastro || !pass || !confirm || !errorMsg || !emailErrorMsg || !emailInput || !emailCheckUrl) {
            return;
        }

        emailErrorMsg.classList.add('hidden');
        emailErrorMsg.textContent = '';
        registrationEmailAvailable = false;
        const emailValue = (registrationEmailValue || emailInput.value || '').trim();

        if (!formCadastro.reportValidity()) {
            return;
        }

        if (!emailValue) {
            emailErrorMsg.textContent = 'Preencha o e-mail corporativo antes de continuar.';
            emailErrorMsg.classList.remove('hidden');
            emailInput.focus();
            return;
        }

        const url = `${emailCheckUrl}?email=${encodeURIComponent(emailValue)}`;
        const response = await fetch(url, {
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
            },
        });

        if (!response.ok) {
            emailErrorMsg.textContent = 'Não foi possível validar o e-mail agora.';
            emailErrorMsg.classList.remove('hidden');
            return;
        }

        const data = await response.json();

        if (data.exists) {
            emailErrorMsg.textContent = 'Este e-mail já está cadastrado.';
            emailErrorMsg.classList.remove('hidden');
            emailInput.focus();
            window.closePasswordModal();
            return;
        }

        registrationEmailAvailable = true;

        if (pass.value !== confirm.value) {
            errorMsg.classList.remove('hidden');
            return;
        }

        errorMsg.textContent = 'As senhas não coincidem.';
        errorMsg.classList.add('hidden');
        window.showPasswordModal();
    };

    // Modal Logic
    const passwordModal = document.getElementById('password-confirm-modal');
    const passwordModalContent = document.getElementById('password-modal-content');

    window.showPasswordModal = function () {
        // Clear previous inputs
        const keyPassword = document.getElementById('key-password');
        const keyPasswordConfirm = document.getElementById('key-password-confirm');
        const passwordError = document.getElementById('password-error');

        if (keyPassword) {
            keyPassword.value = '';
        }

        if (keyPasswordConfirm) {
            keyPasswordConfirm.value = '';
        }

        if (passwordError) {
            passwordError.classList.add('hidden');
        }

        if (!passwordModal || !passwordModalContent) {
            return;
        }

        passwordModal.classList.remove('opacity-0', 'pointer-events-none');
        passwordModalContent.classList.remove('scale-95');
        passwordModalContent.classList.add('scale-100');
    };

    window.openPasswordModal = window.showPasswordModal;

    window.closePasswordModal = function () {
        if (!passwordModal || !passwordModalContent) {
            return;
        }

        passwordModal.classList.add('opacity-0', 'pointer-events-none');
        passwordModalContent.classList.remove('scale-100');
        passwordModalContent.classList.add('scale-95');
    };

    window.validateAndGenerateKey = function () {
        const formCadastro = document.getElementById('formCadastro');
        const pass = document.getElementById('key-password');
        const confirm = document.getElementById('key-password-confirm');
        const errorMsg = document.getElementById('password-error');
        const emailErrorMsg = document.getElementById('reg-email-error');
        const emailInput = document.getElementById('email');

        if (!formCadastro || !pass || !confirm || !errorMsg || !emailErrorMsg || !emailInput) {
            return;
        }

        if (!registrationEmailAvailable) {
            emailErrorMsg.textContent = 'Este e-mail já está cadastrado.';
            emailErrorMsg.classList.remove('hidden');
            emailInput.focus();
            window.closePasswordModal();
            return;
        }

        if (!pass.value || !confirm.value) {
            errorMsg.textContent = 'Preencha os dois campos da senha da chave.';
            errorMsg.classList.remove('hidden');
            return;
        }

        if (pass.value !== confirm.value) {
            errorMsg.textContent = 'As senhas não coincidem.';
            errorMsg.classList.remove('hidden');
            return;
        }

        errorMsg.textContent = 'As senhas não coincidem.';
        errorMsg.classList.add('hidden');

        let hiddenPass = document.getElementById('hidden-senha-chave');
        let hiddenConfirm = document.getElementById('hidden-confirmar-senha-chave');

        if (!hiddenPass) {
            hiddenPass = document.createElement('input');
            hiddenPass.type = 'hidden';
            hiddenPass.id = 'hidden-senha-chave';
            hiddenPass.name = 'senha_chave';
            formCadastro.appendChild(hiddenPass);
        }

        if (!hiddenConfirm) {
            hiddenConfirm = document.createElement('input');
            hiddenConfirm.type = 'hidden';
            hiddenConfirm.id = 'hidden-confirmar-senha-chave';
            hiddenConfirm.name = 'confirmar_senha_chave';
            formCadastro.appendChild(hiddenConfirm);
        }

        hiddenPass.value = pass.value;
        hiddenConfirm.value = confirm.value;

        formCadastro.submit();
    };

    const loginForm = document.getElementById('formLogin');
    const toastTitles = {
        success: 'Sucesso',
        error: 'Erro',
        info: 'Informação',
        warning: 'Atenção',
    };

    const notifyToast = (type, message, title) => {
        if (typeof window.showToast === 'function') {
            window.showToast(title || toastTitles[type] || 'Informação', message, type);
            return;
        }

        window.alert(message);
    };

    if (loginForm) {
        loginForm.addEventListener('submit', async (event) => {
            event.preventDefault();

            const response = await fetch(loginForm.action, {
                method: 'POST',
                body: new FormData(loginForm),
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                },
            });

            let data = null;

            try {
                data = await response.json();
            } catch (error) {
                notifyToast('error', 'Não foi possível processar o login agora.');
                return;
            }

            if (!response.ok || !(data.ok || data.success)) {
                notifyToast('error', data.message || data.mensagem || data.error || 'E-mail ou senha inválidos.');
                return;
            }

            window.location.href = data.redirect_url || '/dashboard/';
        });
    }

    const surfaceInlineFormErrors = () => {
        const errorNodes = document.querySelectorAll('form p.text-red-400, form p[id$="-error"]');

        errorNodes.forEach((node) => {
            if (!node || node.dataset.toastShown === 'true') {
                return;
            }

            const message = (node.textContent || '').trim();
            const isVisible = !node.classList.contains('hidden');

            if (!message || !isVisible) {
                return;
            }

            node.dataset.toastShown = 'true';
            node.classList.add('hidden');

            notifyToast('error', message);
        });
    };

    window.requestAnimationFrame(() => {
        surfaceInlineFormErrors();
    });

    const emailInput = document.getElementById('reg-email');
    if (emailInput) {
        registrationEmailValue = emailInput.value || '';

        const syncEmailValue = () => {
            registrationEmailValue = emailInput.value || '';
        };

        emailInput.addEventListener('input', syncEmailValue);
        emailInput.addEventListener('change', syncEmailValue);
        emailInput.addEventListener('blur', syncEmailValue);

        emailInput.addEventListener('input', () => {
            registrationEmailAvailable = false;
            const emailErrorMsg = document.getElementById('reg-email-error');
            if (emailErrorMsg) {
                emailErrorMsg.classList.add('hidden');
                emailErrorMsg.textContent = '';
            }
        });
    }

    const modal = document.getElementById('secure-key-modal');
    const modalContent = document.getElementById('modal-content');


    window.closeModal = function () {
        if (!modal || !modalContent) {
            return;
        }

        modal.classList.add('opacity-0', 'pointer-events-none');
        modalContent.classList.remove('scale-100');
        modalContent.classList.add('scale-95');
    };

    window.showDownloadModal = function () {
        if (!modal || !modalContent) {
            return;
        }

        modal.classList.remove('opacity-0', 'pointer-events-none');
        modalContent.classList.remove('scale-95');
        modalContent.classList.add('scale-100');
    };


    window.downloadKey = function () {
        const privateKeyField = document.getElementById('private-key-content');

        if (!privateKeyField) {
            notifyToast('error', 'Chave privada não encontrada.');
            return;
        }

        const privateKey = privateKeyField.value;

        const element = document.createElement('a');
        const file = new Blob([privateKey], { type: 'application/x-pem-file' });

        element.href = URL.createObjectURL(file);
        element.download = 'chave_privada_ecc.pem';

        document.body.appendChild(element);
        element.click();
        document.body.removeChild(element);

        URL.revokeObjectURL(element.href);

        closeModal();
    };

    const themeBtns = document.querySelectorAll('.theme-btn');
    const activePill = document.querySelector('.active-pill');

    function updateTheme(theme) {
        const root = document.documentElement;
        const isDark = theme === 'dark' || (theme === 'system' && window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches);

        if (isDark) {
            root.removeAttribute('data-theme');
        } else {
            root.setAttribute('data-theme', 'light');
        }

        themeBtns.forEach((btn, index) => {
            if (btn.dataset.themeValue === theme) {
                btn.classList.add('active', 'text-white');
                btn.classList.remove('text-white/50');
                activePill.style.transform = `translateX(${index * 32}px)`;
            } else {
                btn.classList.remove('active', 'text-white');
                btn.classList.add('text-white/50');
            }
        });

        localStorage.setItem('hybrid-theme', theme);
    }

    const currentTheme = localStorage.getItem('hybrid-theme') || 'system';
    setTimeout(() => updateTheme(currentTheme), 0);

    if (window.matchMedia) {
        window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', () => {
            if (localStorage.getItem('hybrid-theme') === 'system') {
                updateTheme('system');
            }
        });
    }

    themeBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            updateTheme(btn.dataset.themeValue);
        });
    });

    const mobileMenuBtn = document.getElementById('mobile-menu-btn');
    const closeSidebarBtn = document.getElementById('close-sidebar-btn');
    const sidebar = document.getElementById('sidebar');
    const sidebarOverlay = document.getElementById('sidebar-overlay');

    function openSidebar() {
        if (!sidebar || !sidebarOverlay) {
            return;
        }

        sidebar.classList.remove('-translate-x-full');
        sidebarOverlay.classList.remove('hidden');
        sidebarOverlay.classList.remove('pointer-events-none');

        requestAnimationFrame(() => {
            sidebarOverlay.classList.remove('opacity-0');
        });
    }

    function closeSidebar() {
        if (!sidebar || !sidebarOverlay) {
            return;
        }

        sidebar.classList.add('-translate-x-full');
        sidebarOverlay.classList.add('opacity-0');
        sidebarOverlay.classList.add('pointer-events-none');

        window.setTimeout(() => {
            sidebarOverlay.classList.add('hidden');
        }, 300);
    }

    if (mobileMenuBtn && closeSidebarBtn && sidebar && sidebarOverlay) {
        mobileMenuBtn.addEventListener('click', openSidebar);
        closeSidebarBtn.addEventListener('click', closeSidebar);
        sidebarOverlay.addEventListener('click', closeSidebar);
    }

    const dropZone = document.getElementById('drop-zone');
    const fileInput = document.getElementById('file-input');
    const uploadIdle = document.getElementById('upload-idle');
    const uploadSuccess = document.getElementById('upload-success');
    const fileNameDisplay = document.getElementById('file-name');
    const btnRemoveFile = document.getElementById('btn-remove-file');
    const pdfFrame = document.getElementById('pdf-frame');
    const novoDocumentoForm = document.getElementById('novo-documento-form');

    let currentPdfUrl = null;

    function resetUploadPreview() {
        if (currentPdfUrl) {
            URL.revokeObjectURL(currentPdfUrl);
            currentPdfUrl = null;
        }

        if (pdfFrame) {
            pdfFrame.src = '';
        }

        if (uploadSuccess) {
            uploadSuccess.classList.add('hidden');
            uploadSuccess.classList.remove('flex');
        }

        if (uploadIdle) {
            uploadIdle.classList.remove('hidden');
        }

        if (dropZone) {
            dropZone.classList.add('border-dashed');
            dropZone.classList.remove('border-solid', 'border-sky-500/30', 'bg-sky-500/5');
            dropZone.classList.remove('dragover');
        }
    }

    function handleDroppedFile(file) {
        if (!file || !fileNameDisplay || !uploadIdle || !uploadSuccess || !dropZone) {
            return;
        }

        fileNameDisplay.textContent = file.name;

        if (file.type === 'application/pdf' && pdfFrame) {
            if (currentPdfUrl) {
                URL.revokeObjectURL(currentPdfUrl);
            }

            currentPdfUrl = URL.createObjectURL(file);
            pdfFrame.src = currentPdfUrl;
        } else if (pdfFrame) {
            pdfFrame.src = '';
        }

        uploadIdle.classList.add('hidden');
        uploadSuccess.classList.remove('hidden');
        uploadSuccess.classList.add('flex');

        dropZone.classList.remove('border-dashed');
        dropZone.classList.add('border-solid', 'border-sky-500/30', 'bg-sky-500/5');

        notifyToast('success', `O arquivo ${file.name} foi adicionado com sucesso.`, toastTitles.success);
    }

    if (dropZone && fileInput) {
        fileInput.addEventListener('change', (event) => {
            if (event.target.files && event.target.files.length > 0) {
                handleDroppedFile(event.target.files[0]);
            }
        });

        dropZone.addEventListener('dragover', (event) => {
            event.preventDefault();
            dropZone.classList.add('dragover');
        });

        dropZone.addEventListener('dragleave', (event) => {
            event.preventDefault();
            dropZone.classList.remove('dragover');
        });

        dropZone.addEventListener('drop', (event) => {
            event.preventDefault();
            dropZone.classList.remove('dragover');

            if (event.dataTransfer.files.length > 0) {
                const dataTransfer = new DataTransfer();
                dataTransfer.items.add(event.dataTransfer.files[0]);
                fileInput.files = dataTransfer.files;
                handleDroppedFile(event.dataTransfer.files[0]);
            }
        });
    }

    if (btnRemoveFile) {
        btnRemoveFile.addEventListener('click', (event) => {
            event.stopPropagation();
            event.preventDefault();

            if (fileInput) {
                fileInput.value = '';
            }

            resetUploadPreview();
        });
    }

    if (novoDocumentoForm && fileInput) {
        novoDocumentoForm.addEventListener('submit', (event) => {
            if (!fileInput.files || fileInput.files.length === 0) {
                event.preventDefault();
                notifyToast('warning', 'Selecione um documento PDF antes de preparar para assinatura.');
            }
        });
    }

    const btnVerifyAssinatura = document.getElementById('btn-verificar-assinatura');
    const verifyModalOverlay = document.getElementById('verify-modal-overlay');
    const verifyModal = document.getElementById('verify-modal');
    const closeVerifyModal = document.getElementById('close-verify-modal');
    const verifyStepList = document.getElementById('verify-step-list');
    const verifyStepScan = document.getElementById('verify-step-scan');
    const verifyStepSuccess = document.getElementById('verify-step-success');
    const verifyStepError = document.getElementById('verify-step-error');
    const verifyButtons = document.querySelectorAll('.btn-start-verify');
    const verifyBackButtons = document.querySelectorAll('.btn-voltar-verificacao');

    let verifyScanTimeoutId = null;

    function setVerifyStep(stepName) {
        const stepMap = {
            list: verifyStepList,
            scan: verifyStepScan,
            success: verifyStepSuccess,
            error: verifyStepError,
        };

        Object.values(stepMap).forEach(step => {
            if (!step) {
                return;
            }

            step.classList.add('hidden');
            step.classList.remove('flex');
        });

        if (stepMap[stepName]) {
            stepMap[stepName].classList.remove('hidden');
            stepMap[stepName].classList.add('flex');
        }
    }

    function openVerifyModal() {
        if (!verifyModalOverlay || !verifyModal) {
            return;
        }

        if (verifyScanTimeoutId) {
            window.clearTimeout(verifyScanTimeoutId);
            verifyScanTimeoutId = null;
        }

        setVerifyStep('list');
        verifyModalOverlay.classList.remove('hidden');

        requestAnimationFrame(() => {
            verifyModalOverlay.classList.remove('opacity-0');
            verifyModal.classList.remove('scale-95');
            verifyModal.classList.add('scale-100');
        });
    }

    function closeVerifyModalFn() {
        if (!verifyModalOverlay || !verifyModal) {
            return;
        }

        verifyModalOverlay.classList.add('opacity-0');
        verifyModal.classList.remove('scale-100');
        verifyModal.classList.add('scale-95');

        window.setTimeout(() => {
            verifyModalOverlay.classList.add('hidden');
            setVerifyStep('list');
        }, 300);
    }

    if (btnVerifyAssinatura && verifyModalOverlay && verifyModal) {
        btnVerifyAssinatura.addEventListener('click', openVerifyModal);
    }

    if (closeVerifyModal) {
        closeVerifyModal.addEventListener('click', closeVerifyModalFn);
    }

    if (verifyModalOverlay) {
        verifyModalOverlay.addEventListener('click', (event) => {
            if (event.target === verifyModalOverlay) {
                closeVerifyModalFn();
            }
        });
    }

    verifyButtons.forEach(button => {
        button.addEventListener('click', () => {
            if (!verifyModal) {
                return;
            }

            const result = button.dataset.result === 'error' ? 'error' : 'success';
            setVerifyStep('scan');

            verifyScanTimeoutId = window.setTimeout(() => {
                setVerifyStep(result);
            }, 1400);
        });
    });

    verifyBackButtons.forEach(button => {
        button.addEventListener('click', () => {
            if (verifyScanTimeoutId) {
                window.clearTimeout(verifyScanTimeoutId);
                verifyScanTimeoutId = null;
            }

            setVerifyStep('list');
        });
    });

    const btnVerifyBlockchain = document.getElementById('btn-verificar-blockchain');
    const blockchainModalOverlay = document.getElementById('blockchain-modal-overlay');
    const blockchainModal = document.getElementById('blockchain-modal');
    const closeBlockchainModal = document.getElementById('close-blockchain-modal');
    const blockchainStepList = document.getElementById('blockchain-step-list');
    const blockchainStepScan = document.getElementById('blockchain-step-scan');
    const blockchainStepSuccess = document.getElementById('blockchain-step-success');
    const blockchainStepError = document.getElementById('blockchain-step-error');
    const blockchainButtons = document.querySelectorAll('.btn-start-blockchain');
    const blockchainBackButtons = document.querySelectorAll('.btn-voltar-blockchain');

    let blockchainScanTimeoutId = null;

    function setBlockchainStep(stepName) {
        const stepMap = {
            list: blockchainStepList,
            scan: blockchainStepScan,
            success: blockchainStepSuccess,
            error: blockchainStepError,
        };

        Object.values(stepMap).forEach(step => {
            if (!step) {
                return;
            }

            step.classList.add('hidden');
            step.classList.remove('flex');
        });

        if (stepMap[stepName]) {
            stepMap[stepName].classList.remove('hidden');
            stepMap[stepName].classList.add('flex');
        }
    }

    function openBlockchainModal() {
        if (!blockchainModalOverlay || !blockchainModal) {
            return;
        }

        if (blockchainScanTimeoutId) {
            window.clearTimeout(blockchainScanTimeoutId);
            blockchainScanTimeoutId = null;
        }

        setBlockchainStep('list');
        blockchainModalOverlay.classList.remove('hidden');

        requestAnimationFrame(() => {
            blockchainModalOverlay.classList.remove('opacity-0');
            blockchainModal.classList.remove('scale-95');
            blockchainModal.classList.add('scale-100');
        });
    }

    function closeBlockchainModalFn() {
        if (!blockchainModalOverlay || !blockchainModal) {
            return;
        }

        blockchainModalOverlay.classList.add('opacity-0');
        blockchainModal.classList.remove('scale-100');
        blockchainModal.classList.add('scale-95');

        window.setTimeout(() => {
            blockchainModalOverlay.classList.add('hidden');
            setBlockchainStep('list');
        }, 300);
    }

    if (btnVerifyBlockchain && blockchainModalOverlay && blockchainModal) {
        btnVerifyBlockchain.addEventListener('click', openBlockchainModal);
    }

    if (closeBlockchainModal) {
        closeBlockchainModal.addEventListener('click', closeBlockchainModalFn);
    }

    if (blockchainModalOverlay) {
        blockchainModalOverlay.addEventListener('click', (event) => {
            if (event.target === blockchainModalOverlay) {
                closeBlockchainModalFn();
            }
        });
    }

    blockchainButtons.forEach(button => {
        button.addEventListener('click', () => {
            if (!blockchainModal) {
                return;
            }

            const result = button.dataset.result === 'error' ? 'error' : 'success';
            setBlockchainStep('scan');

            blockchainScanTimeoutId = window.setTimeout(() => {
                setBlockchainStep(result);
            }, 1400);
        });
    });

    blockchainBackButtons.forEach(button => {
        button.addEventListener('click', () => {
            if (blockchainScanTimeoutId) {
                window.clearTimeout(blockchainScanTimeoutId);
                blockchainScanTimeoutId = null;
            }

            setBlockchainStep('list');
        });
    });

    const optionsDropdown = document.getElementById('options-dropdown');
    const optionsButtons = document.querySelectorAll('.btn-options-dropdown');
    const dropdownViewDocument = document.getElementById('dropdown-view-document');
    const dropdownShareDocument = document.getElementById('dropdown-share-document');
    const dropdownSignDocument = document.getElementById('dropdown-sign-document');
    const dropdownRejectDocument = document.getElementById('dropdown-reject-document');
    const dropdownCancelDocument = document.getElementById('dropdown-cancel-document');
    const dropdownActionForm = document.getElementById('dropdown-action-form');
    let activeOptionsButton = null;

    function hideOptionsDropdown() {
        if (!optionsDropdown) {
            return;
        }

        optionsDropdown.classList.add('hidden');
        optionsDropdown.classList.remove('flex');
        optionsDropdown.classList.add('opacity-0', 'scale-95');
        activeOptionsButton = null;
    }

    function setDropdownItemVisible(item, visible) {
        if (!item) {
            return;
        }

        item.classList.toggle('hidden', !visible);
        item.classList.toggle('flex', visible);
    }

    function submitDropdownAction(actionUrl, confirmMessage) {
        if (!dropdownActionForm || !actionUrl) {
            return;
        }

        if (confirmMessage && !window.confirm(confirmMessage)) {
            return;
        }

        dropdownActionForm.action = actionUrl;
        dropdownActionForm.submit();
    }

    if (optionsDropdown && optionsButtons.length > 0) {
        optionsButtons.forEach(button => {
            button.addEventListener('click', (event) => {
                event.stopPropagation();

                if (activeOptionsButton === button) {
                    hideOptionsDropdown();
                    return;
                }

                activeOptionsButton = button;

                setDropdownItemVisible(dropdownSignDocument, button.dataset.canSign === 'true');
                setDropdownItemVisible(dropdownRejectDocument, button.dataset.canRecusar === 'true');
                setDropdownItemVisible(dropdownCancelDocument, button.dataset.canCancel === 'true');

                optionsDropdown.classList.remove('hidden');
                optionsDropdown.classList.add('flex');

                const rect = button.getBoundingClientRect();
                const margin = 12;
                const dropdownWidth = optionsDropdown.offsetWidth;
                const dropdownHeight = optionsDropdown.offsetHeight;
                const preferredLeft = window.scrollX + rect.right - dropdownWidth;
                const maxLeft = window.scrollX + window.innerWidth - dropdownWidth - margin;
                const minLeft = window.scrollX + margin;
                const preferredTop = window.scrollY + rect.bottom + 8;
                const maxTop = window.scrollY + window.innerHeight - dropdownHeight - margin;

                optionsDropdown.style.left = `${Math.max(minLeft, Math.min(preferredLeft, maxLeft))}px`;
                optionsDropdown.style.top = `${Math.max(window.scrollY + margin, Math.min(preferredTop, maxTop))}px`;

                requestAnimationFrame(() => {
                    optionsDropdown.classList.remove('opacity-0', 'scale-95');
                });
            });
        });

        document.addEventListener('click', (event) => {
            if (!optionsDropdown.contains(event.target)) {
                hideOptionsDropdown();
            }
        });
    }

    if (dropdownViewDocument) {
        dropdownViewDocument.addEventListener('click', () => {
            if (!activeOptionsButton || !activeOptionsButton.dataset.viewUrl) {
                return;
            }

            window.open(activeOptionsButton.dataset.viewUrl, '_blank');
            hideOptionsDropdown();
        });
    }

    if (dropdownShareDocument) {
        dropdownShareDocument.addEventListener('click', () => {
            notifyToast('info', 'Compartilhamento ainda não foi implementado para este documento.');
            hideOptionsDropdown();
        });
    }

    if (dropdownSignDocument) {
        dropdownSignDocument.addEventListener('click', () => {
            if (activeOptionsButton) {
                openSignModal(activeOptionsButton);
            }

            hideOptionsDropdown();
        });
    }

    if (dropdownRejectDocument) {
        dropdownRejectDocument.addEventListener('click', () => {
            if (!activeOptionsButton) {
                return;
            }

            submitDropdownAction(
                activeOptionsButton.dataset.recusarUrl,
                'Deseja recusar este convite de assinatura?'
            );
        });
    }

    if (dropdownCancelDocument) {
        dropdownCancelDocument.addEventListener('click', () => {
            if (!activeOptionsButton) {
                return;
            }

            submitDropdownAction(
                activeOptionsButton.dataset.cancelUrl,
                'Deseja cancelar este documento?'
            );
        });
    }

    const signModalOverlay = document.getElementById('sign-modal-overlay');
    const signDocumentForm = document.getElementById('sign-document-form');
    const signDocumentName = document.getElementById('sign-document-name');
    const signAssinanteId = document.getElementById('sign-assinante-id');
    const signPrivateKey = document.getElementById('sign-private-key');
    const signPrivateKeyPassword = document.getElementById('sign-private-key-password');
    const signModalButtons = document.querySelectorAll('.btn-open-sign-modal');
    const closeSignModalButtons = document.querySelectorAll('#btn-close-sign-modal, #btn-cancel-sign-modal');

    function openSignModal(button) {
        if (!signModalOverlay || !signDocumentForm || !signAssinanteId) {
            return;
        }

        const documentoId = button.dataset.documentoId;
        const assinanteId = button.dataset.assinanteId;
        const documentoNome = button.dataset.documentoNome || 'Documento selecionado';

        if (!documentoId || !assinanteId) {
            notifyToast('error', 'Não foi possível identificar o convite de assinatura.');
            return;
        }

        signDocumentForm.action = `/documentos/${documentoId}/assinar`;
        signAssinanteId.value = assinanteId;

        if (signDocumentName) {
            signDocumentName.textContent = documentoNome;
        }

        if (signPrivateKey) {
            signPrivateKey.value = '';
        }

        if (signPrivateKeyPassword) {
            signPrivateKeyPassword.value = '';
        }

        signModalOverlay.classList.remove('hidden');
        void signModalOverlay.offsetWidth;
        signModalOverlay.classList.remove('opacity-0');

        if (signDocumentForm) {
            signDocumentForm.classList.remove('scale-95');
            signDocumentForm.classList.add('scale-100');
        }
    }

    function closeSignModal() {
        if (!signModalOverlay || !signDocumentForm) {
            return;
        }

        signModalOverlay.classList.add('opacity-0');
        signDocumentForm.classList.remove('scale-100');
        signDocumentForm.classList.add('scale-95');

        window.setTimeout(() => {
            signModalOverlay.classList.add('hidden');
        }, 300);
    }

    signModalButtons.forEach(button => {
        button.addEventListener('click', () => openSignModal(button));
    });

    closeSignModalButtons.forEach(button => {
        button.addEventListener('click', closeSignModal);
    });

    if (signModalOverlay) {
        signModalOverlay.addEventListener('click', (event) => {
            if (event.target === signModalOverlay) {
                closeSignModal();
            }
        });
    }

    const btnFinalizar = document.getElementById('btn-finalizar');
    const eccModal = document.getElementById('ecc-modal');
    const eccBackdrop = document.getElementById('ecc-backdrop');
    const eccContent = document.getElementById('ecc-content');
    const btnCancelEcc = document.getElementById('btn-cancel-ecc');
    const btnConfirmEcc = document.getElementById('btn-confirm-ecc');
    const eccPassword = document.getElementById('ecc-password');
    const eccSuccessMsg = document.getElementById('ecc-success-msg');
    const eccActions = document.getElementById('ecc-actions');

    function openEccModal() {
        if (!eccModal || !eccContent) {
            return;
        }

        if (!currentPdfUrl) {
            notifyToast('warning', 'Por favor, selecione um documento PDF primeiro.');
            return;
        }

        eccModal.classList.remove('hidden');
        void eccModal.offsetWidth;
        eccContent.classList.remove('scale-95', 'opacity-0');
        eccContent.classList.add('scale-100', 'opacity-100');

        if (eccPassword) {
            eccPassword.value = '';
            eccPassword.classList.remove('border-red-500/50');
        }

        if (eccSuccessMsg) {
            eccSuccessMsg.classList.add('hidden');
            eccSuccessMsg.classList.remove('flex');
        }

        if (eccActions) {
            eccActions.classList.remove('hidden');
            eccActions.classList.add('flex');
        }

        if (eccPassword) {
            eccPassword.focus();
        }
    }

    function closeEccModal() {
        if (!eccModal || !eccContent) {
            return;
        }

        eccContent.classList.remove('scale-100', 'opacity-100');
        eccContent.classList.add('scale-95', 'opacity-0');

        window.setTimeout(() => {
            eccModal.classList.add('hidden');
        }, 300);
    }

    if (btnFinalizar && !btnFinalizar.dataset.submitDocument) {
        btnFinalizar.addEventListener('click', openEccModal);
    }

    if (btnCancelEcc) {
        btnCancelEcc.addEventListener('click', closeEccModal);
    }

    if (eccBackdrop) {
        eccBackdrop.addEventListener('click', closeEccModal);
    }

    if (btnConfirmEcc && eccPassword && eccSuccessMsg && eccActions) {
        btnConfirmEcc.addEventListener('click', () => {
            if (!eccPassword.value.trim()) {
                eccPassword.classList.add('border-red-500/50');

                window.setTimeout(() => {
                    eccPassword.classList.remove('border-red-500/50');
                }, 1000);

                return;
            }

            const originalContent = btnConfirmEcc.innerHTML;
            btnConfirmEcc.innerHTML = '<span class="flex items-center justify-center gap-2 w-full h-full rounded-xl px-4 py-3.5 backdrop-blur-xl border border-white/10 text-white"><iconify-icon icon="lucide:loader-2" width="20" class="animate-spin text-white"></iconify-icon></span>';

            window.setTimeout(() => {
                eccActions.classList.add('hidden');
                eccActions.classList.remove('flex');
                eccSuccessMsg.classList.remove('hidden');
                eccSuccessMsg.classList.add('flex');

                window.setTimeout(() => {
                    btnConfirmEcc.innerHTML = originalContent;
                    window.location.href = 'documentos.html';
                }, 2000);
            }, 1500);
        });
    }

    window.showToast = function (title, message, type = 'success', duration = 4000) {
        const container = document.getElementById('toast-container');

        if (!container) {
            return;
        }

        const toast = document.createElement('div');
        toast.className = 'glass-panel pointer-events-auto w-80 rounded-2xl overflow-hidden shadow-2xl border transition-all duration-300 transform translate-y-8 opacity-0 flex flex-col mt-3 bg-slate-900/95';

        let icon = 'lucide:info';
        let colorClass = 'text-sky-400';
        let bgClass = 'bg-sky-500/10';
        let borderClass = 'border-sky-500/20';
        let progressBgClass = 'bg-sky-500';

        if (type === 'success') {
            icon = 'lucide:check-circle-2';
            colorClass = 'text-emerald-400';
            bgClass = 'bg-emerald-500/10';
            borderClass = 'border-emerald-500/20';
            progressBgClass = 'bg-emerald-500';
        } else if (type === 'error') {
            icon = 'lucide:alert-circle';
            colorClass = 'text-red-400';
            bgClass = 'bg-red-500/10';
            borderClass = 'border-red-500/20';
            progressBgClass = 'bg-red-500';
        }

        toast.innerHTML = `
            <div class="p-4 flex items-start gap-3 bg-white/[0.02]">
                <div class="w-8 h-8 rounded-full ${bgClass} ${borderClass} border flex items-center justify-center shrink-0 ${colorClass}">
                    <iconify-icon icon="${icon}" width="16"></iconify-icon>
                </div>
                <div class="flex-1 min-w-0 pt-1">
                    <h4 class="text-sm font-medium text-white">${title}</h4>
                    <p class="text-xs text-white/60 mt-0.5 leading-relaxed">${message}</p>
                </div>
                <button class="w-6 h-6 flex items-center justify-center text-white/40 hover:text-white transition-colors shrink-0" onclick="this.closest('.glass-panel').remove()">
                    <iconify-icon icon="lucide:x" width="14"></iconify-icon>
                </button>
            </div>
            <div class="h-1 w-full bg-black/20">
                <div class="h-full ${progressBgClass} transition-all duration-100 ease-linear origin-left" style="width: 100%"></div>
            </div>
        `;

        container.appendChild(toast);

        requestAnimationFrame(() => {
            toast.classList.remove('translate-y-8', 'opacity-0');
        });

        const progressBar = toast.querySelector('.h-full.transition-all');
        const startTime = Date.now();

        function updateProgress() {
            const elapsed = Date.now() - startTime;
            const progress = Math.max(0, 100 - (elapsed / duration) * 100);
            progressBar.style.width = `${progress}%`;

            if (progress > 0) {
                requestAnimationFrame(updateProgress);
            }
        }

        requestAnimationFrame(updateProgress);

        window.setTimeout(() => {
            toast.classList.add('translate-y-8', 'opacity-0');

            window.setTimeout(() => {
                toast.remove();
            }, 300);
        }, duration);
    };


    // ==========================================
    // Dynamic Signers Logic
    // ==========================================
    const btnMinus = document.getElementById('btn-minus-signer');
    const btnPlus = document.getElementById('btn-plus-signer');
    const signerCountDisplay = document.getElementById('signer-count');
    const signersContainer = document.getElementById('signers-container');

    if (btnMinus && btnPlus && signerCountDisplay && signersContainer) {
    let numSigners = 1;

    function renderSigners() {
        signerCountDisplay.textContent = numSigners;
        btnMinus.disabled = numSigners <= 1;

        // Clear current
        signersContainer.innerHTML = '';

        for (let i = 1; i <= numSigners; i++) {
            const signerHtml = `
                        <div class="bg-white/[0.02] border border-white/5 rounded-2xl p-5 relative group transition-all animate-[fadeIn_0.3s_ease-out]">
                            <div class="absolute top-0 right-0 p-3">
                                <span class="text-[10px] text-white/30 uppercase tracking-wider font-semibold">Signatário ${i}</span>
                            </div>
                            <div class="space-y-4 pt-2">
                                <div>
                                    <label class="block text-xs text-white/50 mb-1.5 ml-1">Nome Completo</label>
                                    <div class="relative">
                                        <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-white/30">
                                            <iconify-icon icon="lucide:user" width="16"></iconify-icon>
                                        </div>
                                        <input type="text" name="assinantes_nome[]" required placeholder="Ex: Dr. Renato Silva" class="w-full bg-black/20 border border-white/10 rounded-xl py-2.5 pl-10 pr-4 text-white placeholder-white/30 focus:outline-none focus:border-sky-500/50 focus:ring-1 focus:ring-sky-500/50 transition-all text-sm">
                                    </div>
                                </div>
                                <div>
                                    <label class="block text-xs text-white/50 mb-1.5 ml-1">E-mail Profissional</label>
                                    <div class="relative">
                                        <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-white/30">
                                            <iconify-icon icon="lucide:mail" width="16"></iconify-icon>
                                        </div>
                                        <input type="email" name="assinantes_email[]" required placeholder="exemplo@escritorio.adv.br" class="w-full bg-black/20 border border-white/10 rounded-xl py-2.5 pl-10 pr-4 text-white placeholder-white/30 focus:outline-none focus:border-sky-500/50 focus:ring-1 focus:ring-sky-500/50 transition-all text-sm">
                                    </div>
                                </div>
                            </div>
                        </div>
                    `;
            signersContainer.insertAdjacentHTML('beforeend', signerHtml);
        }
    }

    btnPlus.addEventListener('click', () => {
        if (numSigners < 10) {
            numSigners++;
            renderSigners();
        }
    });

    btnMinus.addEventListener('click', () => {
        if (numSigners > 1) {
            numSigners--;
            renderSigners();
        }
    });

    // Initial render
    renderSigners();
    }


});
