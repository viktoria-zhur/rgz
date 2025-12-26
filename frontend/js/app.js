class BankApp {
    constructor() {
        this.api = window.bankAPI;
        this.currentUser = null;
    }

    init() {
        console.log('BankApp initialized');
    }
}

window.bankApp = new BankApp();

document.addEventListener('DOMContentLoaded', () => {
    window.bankApp.init();
});