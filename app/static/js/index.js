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
    const loginError = document.getElementById('login-error');
    const loginErrorText = document.getElementById('login-error-text');

    if (loginForm && loginError && loginErrorText) {
        loginForm.addEventListener('submit', async (event) => {
            event.preventDefault();

            loginError.classList.add('hidden');
            loginErrorText.textContent = '';

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
                loginErrorText.textContent = 'Não foi possível processar o login agora.';
                loginError.classList.remove('hidden');
                return;
            }

            if (!response.ok || !data.ok) {
                loginErrorText.textContent = data.message || 'E-mail ou senha inválidos.';
                loginError.classList.remove('hidden');
                return;
            }

            window.location.href = data.redirect_url || '/dashboard/';
        });
    }

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
            alert('Chave privada não encontrada.');
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

});