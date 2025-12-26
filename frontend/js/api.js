class BankAPI {
    constructor() {
        // ИЗМЕНЕНО: относительный путь
        this.baseUrl = '/api';
        this.requestId = 1;
    }

    async call(method, params = {}) {
        const request = {
            jsonrpc: "2.0",
            method: method,
            params: params,
            id: this.requestId++
        };

        try {
            const response = await fetch(this.baseUrl, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(request),
                credentials: 'include'  // Для куков сессии
            });

            if (!response.ok) {
                throw new Error(`HTTP error: ${response.status}`);
            }

            const data = await response.json();

            if (data.error) {
                throw new Error(data.error.message);
            }

            return data.result;
        } catch (error) {
            console.error('API Error:', error);
            throw error;
        }
    }

    async login(login, password) {
        return await this.call('login', { login, password });
    }

    async logout() {
        return await this.call('logout', {});
    }

    async verifyToken() {
        return await this.call('verifyToken', {});
    }

    async getAccountInfo() {
        return await this.call('getAccountInfo');
    }

    async getTransactionHistory() {
        return await this.call('getTransactionHistory');
    }

    async transferMoney(params) {
        return await this.call('transferMoney', params);
    }

    async getAllUsers() {
        return await this.call('getAllUsers');
    }

    async createUser(userData) {
        return await this.call('createUser', userData);
    }

    async updateUser(userData) {
        return await this.call('updateUser', userData);
    }

    async deleteUser(userId) {
        return await this.call('deleteUser', { id: userId });
    }

    async deleteAccount() {
        return await this.call('deleteAccount', {});
    }

    async getStatistics() {
        return await this.call('getStatistics');
    }
}

window.bankAPI = new BankAPI();