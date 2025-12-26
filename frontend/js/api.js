class BankAPI {
    constructor() {
        this.baseUrl = 'http://localhost:5000/api';
        this.requestId = 1;
    }

    async call(method, params = {}) {
        const request = {
            jsonrpc: "2.0",
            method: method,
            params: params,
            id: this.requestId++
        };

        const response = await fetch(this.baseUrl, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(request),
            credentials: 'include'
        });

        const data = await response.json();

        if (data.error) {
            throw new Error(data.error.message);
        }

        return data.result;
    }
}

window.bankAPI = new BankAPI();