class BankApp {
    constructor() {
        this.api = window.bankAPI;
        this.currentUser = null;
        this.editingUserId = null;
    }

    init() {
        this.migrateAuthData();
        this.checkAuth();
        this.setupEventListeners();
    }

    migrateAuthData() {
        const bankToken = localStorage.getItem('bank_token');
        if (bankToken && !localStorage.getItem('token')) {
            localStorage.setItem('token', bankToken);
        }
        
        const bankUser = localStorage.getItem('bank_user');
        if (bankUser && !localStorage.getItem('user')) {
            localStorage.setItem('user', bankUser);
        }
        
        this.currentUser = this.getCurrentUser();
    }

    getCurrentUser() {
        const userStr = localStorage.getItem('user');
        return userStr ? JSON.parse(userStr) : null;
    }

    async checkAuth() {
        try {
            const result = await this.api.verifyToken();
            if (result.valid) {
                const user = await this.api.getAccountInfo();
                this.currentUser = user;
                localStorage.setItem('user', JSON.stringify(user));
                this.showInterface();
            } else {
                this.showLogin();
            }
        } catch (error) {
            this.showLogin();
        }
    }

    showInterface() {
        document.getElementById('loginSection').classList.add('hidden');
        this.showUserInfo();
        
        if (this.currentUser.role === 'manager') {
            document.getElementById('managerInterface').classList.remove('hidden');
            document.getElementById('clientInterface').classList.add('hidden');
            this.loadManagerData();
        } else {
            document.getElementById('clientInterface').classList.remove('hidden');
            document.getElementById('managerInterface').classList.add('hidden');
            this.loadClientData();
        }
    }

    showLogin() {
        document.getElementById('loginSection').classList.remove('hidden');
        document.getElementById('clientInterface').classList.add('hidden');
        document.getElementById('managerInterface').classList.add('hidden');
        document.getElementById('loginForm').reset();
        this.clearValidationErrors(['login', 'password']);
    }

    showUserInfo() {
        if (!this.currentUser) return;
        
        const userInfoDiv = document.getElementById('userInfo');
        userInfoDiv.innerHTML = `
            <div class="user-profile">
                <i class="fas fa-user-circle"></i>
                <div class="user-details">
                    <span class="user-name">${this.currentUser.full_name}</span>
                    <span class="user-role">${this.currentUser.role === 'manager' ? 'Менеджер' : 'Клиент'}</span>
                </div>
            </div>
        `;
    }

    async loadManagerData() {
        try {
            await this.loadAllUsers();
            await this.loadStatistics();
        } catch (error) {
            this.showError('Ошибка загрузки данных');
        }
    }

    async loadAllUsers() {
        try {
            const users = await this.api.getAllUsers();
            this.updateUsersTable(users);
        } catch (error) {
            document.getElementById('usersTableBody').innerHTML = `
                <tr>
                    <td colspan="7" class="error-table">Ошибка загрузки</td>
                </tr>
            `;
        }
    }

    updateUsersTable(users) {
        const tbody = document.getElementById('usersTableBody');
        
        if (!users || users.length === 0) {
            tbody.innerHTML = `
                <tr>
                    <td colspan="7" class="empty-table">Нет пользователей</td>
                </tr>
            `;
            return;
        }
        
        let html = '';
        users.forEach(user => {
            html += `
                <tr data-user-id="${user.id}">
                    <td>${user.login}</td>
                    <td>${user.full_name}</td>
                    <td>
                        <span class="role-badge ${user.role}">
                            ${user.role === 'manager' ? 'Менеджер' : 'Клиент'}
                        </span>
                    </td>
                    <td>${user.phone || '-'}</td>
                    <td>${user.account_number || '-'}</td>
                    <td class="balance-cell">${user.balance ? user.balance.toFixed(2) + ' ₽' : '-'}</td>
                    <td class="actions-cell">
                        <button class="btn-icon edit-user" data-id="${user.id}" title="Редактировать">
                            <i class="fas fa-edit"></i>
                        </button>
                        <button class="btn-icon delete-user" data-id="${user.id}" title="Удалить">
                            <i class="fas fa-trash"></i>
                        </button>
                    </td>
                </tr>
            `;
        });
        
        tbody.innerHTML = html;
        this.setupUserActions();
    }

    async loadStatistics() {
        try {
            const stats = await this.api.getStatistics();
            document.getElementById('totalUsers').textContent = stats.total_users;
            document.getElementById('totalManagers').textContent = stats.total_managers;
            document.getElementById('totalClients').textContent = stats.total_clients;
            document.getElementById('totalBalance').textContent = stats.total_balance.toFixed(2) + ' ₽';
            document.getElementById('statsSection').style.display = 'grid';
        } catch (error) {
            document.getElementById('statsSection').style.display = 'none';
        }
    }

    async loadClientData() {
        try {
            const accountInfo = await this.api.getAccountInfo();
            document.getElementById('balanceAmount').textContent = accountInfo.balance.toFixed(2) + ' ₽';
            document.getElementById('accountNumber').textContent = accountInfo.account_number || '-';
            document.getElementById('accountOwner').textContent = accountInfo.full_name;
            document.getElementById('accountPhone').textContent = accountInfo.phone || '-';
            await this.loadTransactionHistory();
        } catch (error) {
            this.showError('Ошибка загрузки данных счета');
        }
    }

    async loadTransactionHistory() {
        try {
            const transactions = await this.api.getTransactionHistory();
            this.updateTransactionsList(transactions);
        } catch (error) {
            console.error('Error loading transactions:', error);
        }
    }

    updateTransactionsList(transactions) {
        const list = document.getElementById('transactionsList');
        
        if (!transactions || transactions.length === 0) {
            list.innerHTML = `
                <div class="empty-state">
                    <i class="fas fa-receipt"></i>
                    <p>Нет операций</p>
                </div>
            `;
            return;
        }
        
        let html = '';
        transactions.forEach(transaction => {
            const typeClass = transaction.type === 'outgoing' ? 'debit' : 'credit';
            const typeIcon = transaction.type === 'outgoing' ? 'fa-arrow-up' : 'fa-arrow-down';
            const typeText = transaction.type === 'outgoing' ? 'Списание' : 'Пополнение';
            
            html += `
                <div class="transaction-item ${typeClass}">
                    <div class="transaction-icon">
                        <i class="fas ${typeIcon}"></i>
                    </div>
                    <div class="transaction-details">
                        <div class="transaction-header">
                            <span class="transaction-type">${typeText}</span>
                            <span class="transaction-date">${new Date(transaction.created_at).toLocaleDateString()}</span>
                        </div>
                        <div class="transaction-info">
                            ${transaction.description || 'Перевод средств'}
                        </div>
                        ${transaction.counterparty ? 
                            `<div class="transaction-counterparty">
                                Контрагент: ${transaction.counterparty}
                            </div>` : ''
                        }
                    </div>
                    <div class="transaction-amount">
                        ${transaction.amount.toFixed(2)} ₽
                    </div>
                </div>
            `;
        });
        
        list.innerHTML = html;
    }

    setupEventListeners() {
        document.getElementById('loginForm').addEventListener('submit', (e) => {
            e.preventDefault();
            this.handleLogin();
        });

        window.logoutUser = () => {
            this.handleLogout();
        };

        if (document.getElementById('showCreateUserForm')) {
            document.getElementById('showCreateUserForm').addEventListener('click', () => {
                this.hideEditUserForm();
                document.getElementById('createUserForm').style.display = 'block';
            });
        }

        if (document.getElementById('refreshUsersBtn')) {
            document.getElementById('refreshUsersBtn').addEventListener('click', () => {
                this.loadAllUsers();
                this.loadStatistics();
            });
        }

        if (document.getElementById('showStatsBtn')) {
            document.getElementById('showStatsBtn').addEventListener('click', () => {
                const statsSection = document.getElementById('statsSection');
                statsSection.style.display = statsSection.style.display === 'none' ? 'grid' : 'none';
            });
        }

        if (document.getElementById('cancelCreate')) {
            document.getElementById('cancelCreate').addEventListener('click', () => {
                this.hideEditUserForm();
            });
        }

        if (document.getElementById('newUserForm')) {
            document.getElementById('newUserForm').addEventListener('submit', (e) => {
                e.preventDefault();
                if (this.editingUserId) {
                    this.handleUpdateUser();
                } else {
                    this.handleCreateUser();
                }
            });
        }

        if (document.getElementById('newUserRole')) {
            document.getElementById('newUserRole').addEventListener('change', (e) => {
                this.toggleClientFields(e.target.value === 'client');
            });
        }

        if (document.getElementById('refreshHistory')) {
            document.getElementById('refreshHistory').addEventListener('click', () => {
                this.loadTransactionHistory();
            });
        }

        if (document.getElementById('transferForm')) {
            document.getElementById('transferForm').addEventListener('submit', (e) => {
                e.preventDefault();
                this.handleTransfer();
            });
        }
    }

    setupUserActions() {
        document.querySelectorAll('.edit-user').forEach(button => {
            button.addEventListener('click', (e) => {
                const userId = e.currentTarget.dataset.id;
                this.handleEditUser(userId);
            });
        });

        document.querySelectorAll('.delete-user').forEach(button => {
            button.addEventListener('click', (e) => {
                const userId = e.currentTarget.dataset.id;
                this.handleDeleteUser(userId);
            });
        });
    }

    async handleLogin() {
        const login = document.getElementById('login').value;
        const password = document.getElementById('password').value;
        
        this.clearValidationErrors(['login', 'password']);
        
        if (!login) {
            this.showValidationError('login', 'Логин обязателен');
            return;
        }
        
        if (!password) {
            this.showValidationError('password', 'Пароль обязателен');
            return;
        }
        
        try {
            const result = await this.api.login(login, password);
            this.currentUser = result.user;
            localStorage.setItem('user', JSON.stringify(result.user));
            this.showInterface();
        } catch (error) {
            this.showError('Ошибка входа: ' + error.message);
        }
    }

    async handleLogout() {
        if (confirm('Вы уверены, что хотите выйти?')) {
            try {
                await this.api.logout();
                localStorage.removeItem('user');
                this.currentUser = null;
                this.showLogin();
            } catch (error) {
                this.showError('Ошибка выхода');
            }
        }
    }

    async handleCreateUser() {
        const userData = {
            login: document.getElementById('newLogin').value,
            password: document.getElementById('newPassword').value,
            fullName: document.getElementById('newFullName').value,
            role: document.getElementById('newUserRole').value,
            phone: document.getElementById('newPhone').value || undefined
        };

        if (userData.role === 'client') {
            userData.accountNumber = document.getElementById('newAccountNumber').value || undefined;
            userData.balance = parseFloat(document.getElementById('newBalance').value) || 1000;
        }
        
        this.clearValidationErrors(['newLogin', 'newPassword', 'newFullName', 'newPhone', 'newAccountNumber', 'newBalance']);
        
        try {
            await this.api.createUser(userData);
            this.showSuccess('Пользователь успешно создан!');
            this.hideEditUserForm();
            await this.loadAllUsers();
            await this.loadStatistics();
        } catch (error) {
            this.showError('Ошибка создания пользователя: ' + error.message);
        }
    }

    async handleEditUser(userId) {
        try {
            const users = await this.api.getAllUsers();
            const userToEdit = users.find(u => u.id === parseInt(userId));
            
            if (!userToEdit) {
                this.showError('Пользователь не найден');
                return;
            }
            
            this.showEditUserForm(userToEdit);
        } catch (error) {
            this.showError('Ошибка загрузки данных пользователя');
        }
    }

    showEditUserForm(user) {
        this.editingUserId = user.id;
        
        const formSection = document.getElementById('createUserForm');
        formSection.style.display = 'block';
        
        document.getElementById('newLogin').value = user.login;
        document.getElementById('newPassword').value = '';
        document.getElementById('newFullName').value = user.full_name;
        document.getElementById('newUserRole').value = user.role;
        document.getElementById('newPhone').value = user.phone || '';
        document.getElementById('newAccountNumber').value = user.account_number || '';
        document.getElementById('newBalance').value = user.balance || '1000.00';
        
        this.toggleClientFields(user.role === 'client');
        
        const submitBtn = formSection.querySelector('button[type="submit"]');
        submitBtn.innerHTML = '<i class="fas fa-save"></i> Сохранить изменения';
    }

    toggleClientFields(show) {
        const clientFields = document.getElementById('clientFields');
        if (clientFields) {
            clientFields.style.display = show ? 'flex' : 'none';
        }
    }

    async handleUpdateUser() {
        if (!this.editingUserId) {
            this.showError('Не выбран пользователь для редактирования');
            return;
        }
        
        const userData = {
            id: this.editingUserId,
            login: document.getElementById('newLogin').value,
            fullName: document.getElementById('newFullName').value,
            role: document.getElementById('newUserRole').value,
            phone: document.getElementById('newPhone').value || undefined
        };
        
        const password = document.getElementById('newPassword').value;
        if (password) {
            userData.password = password;
        }
        
        if (userData.role === 'client') {
            userData.accountNumber = document.getElementById('newAccountNumber').value || undefined;
            userData.balance = parseFloat(document.getElementById('newBalance').value) || 0;
        }
        
        try {
            await this.api.updateUser(userData);
            this.showSuccess('Пользователь успешно обновлен!');
            this.hideEditUserForm();
            await this.loadAllUsers();
            await this.loadStatistics();
        } catch (error) {
            this.showError('Ошибка обновления пользователя: ' + error.message);
        }
    }

    hideEditUserForm() {
        this.editingUserId = null;
        
        const formSection = document.getElementById('createUserForm');
        formSection.style.display = 'none';
        
        const submitBtn = formSection.querySelector('button[type="submit"]');
        submitBtn.innerHTML = '<i class="fas fa-save"></i> Создать пользователя';
        
        document.getElementById('newUserForm').reset();
        this.clearValidationErrors(['newLogin', 'newPassword', 'newFullName', 'newPhone', 'newAccountNumber', 'newBalance']);
    }

    async handleDeleteUser(userId) {
        if (!confirm('Вы уверены, что хотите удалить этого пользователя?')) {
            return;
        }
        
        try {
            await this.api.deleteUser(userId);
            this.showSuccess('Пользователь удален');
            await this.loadAllUsers();
            await this.loadStatistics();
        } catch (error) {
            this.showError('Ошибка удаления пользователя: ' + error.message);
        }
    }

    async handleDeleteAccount() {
        if (!confirm('Вы уверены, что хотите удалить свой аккаунт? Это действие необратимо.')) {
            return;
        }
        
        try {
            await this.api.deleteAccount();
            this.showSuccess('Ваш аккаунт удален');
            localStorage.removeItem('user');
            this.currentUser = null;
            this.showLogin();
        } catch (error) {
            this.showError('Ошибка удаления аккаунта: ' + error.message);
        }
    }

    async handleTransfer() {
        const recipient = document.getElementById('recipient').value;
        const amount = parseFloat(document.getElementById('transferAmount').value);
        
        this.clearValidationErrors(['recipient', 'amount']);
        
        if (!recipient) {
            this.showValidationError('recipient', 'Укажите получателя');
            return;
        }
        
        if (!amount || amount <= 0) {
            this.showValidationError('amount', 'Сумма должна быть положительной');
            return;
        }
        
        try {
            await this.api.transferMoney({
                recipient: recipient,
                amount: amount
            });
            
            this.showSuccess('Перевод успешно выполнен!');
            document.getElementById('transferForm').reset();
            await this.loadClientData();
        } catch (error) {
            this.showError('Ошибка перевода: ' + error.message);
        }
    }

    // Вспомогательные методы
    showError(message) {
        alert('Ошибка: ' + message);
    }

    showSuccess(message) {
        alert('✅ ' + message);
    }

    showValidationError(fieldId, message) {
        const errorElement = document.getElementById(fieldId + 'Error');
        if (errorElement) {
            errorElement.textContent = message;
            errorElement.style.display = 'block';
        }
    }

    clearValidationErrors(fieldIds) {
        fieldIds.forEach(fieldId => {
            const errorElement = document.getElementById(fieldId + 'Error');
            if (errorElement) {
                errorElement.textContent = '';
                errorElement.style.display = 'none';
            }
        });
    }
}

window.bankApp = new BankApp();

document.addEventListener('DOMContentLoaded', () => {
    window.bankApp.init();
});