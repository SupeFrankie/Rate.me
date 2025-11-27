// Dark Mode Toggle
class DarkMode {
    constructor() {
        this.theme = localStorage.getItem('theme') || 'light';
        this.init();
    }

    init() {
        document.body.setAttribute('data-theme', this.theme);
        this.createToggle();
        this.updateIcon();
    }

    createToggle() {
        const toggle = document.createElement('button');
        toggle.className = 'theme-toggle';
        toggle.innerHTML = '<i class="bi bi-moon-stars-fill"></i>';
        toggle.onclick = () => this.toggle();
        toggle.setAttribute('title', 'Toggle Dark Mode');
        document.body.appendChild(toggle);
        this.toggleBtn = toggle;
    }

    toggle() {
        this.theme = this.theme === 'light' ? 'dark' : 'light';
        document.body.setAttribute('data-theme', this.theme);
        localStorage.setItem('theme', this.theme);
        this.updateIcon();
        
        if (typeof toast !== 'undefined') {
            toast.success(`${this.theme === 'dark' ? '🌙 Dark' : '☀️ Light'} mode activated!`);
        }
    }

    updateIcon() {
        if (this.toggleBtn) {
            this.toggleBtn.innerHTML = this.theme === 'dark' 
                ? '<i class="bi bi-sun-fill"></i>' 
                : '<i class="bi bi-moon-stars-fill"></i>';
        }
    }
}

document.addEventListener('DOMContentLoaded', () => {
    new DarkMode();
});