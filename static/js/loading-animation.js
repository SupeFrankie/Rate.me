// JJK Hollow Purple Loading Animation
class HollowPurpleLoader {
    constructor() {
        this.overlay = null;
        this.createOverlay();
    }

    createOverlay() {
        this.overlay = document.createElement('div');
        this.overlay.className = 'jjk-loading-overlay';
        
        this.overlay.innerHTML = `
            <div class="infinity-symbol"></div>
            
            <div class="hollow-purple-container">
                <div class="reversal-red"></div>
                <div class="lapse-blue"></div>
                <div class="hollow-purple-core"></div>
                
                <div class="cursed-energy-wave"></div>
                <div class="cursed-energy-wave"></div>
                <div class="cursed-energy-wave"></div>
                
                <div class="domain-particles">
                    <div class="particle"></div>
                    <div class="particle"></div>
                    <div class="particle"></div>
                    <div class="particle"></div>
                    <div class="particle"></div>
                    <div class="particle"></div>
                </div>
            </div>
            
            <div class="jjk-loading-text">Hollow Purple</div>
        `;
        
        document.body.appendChild(this.overlay);
    }

    show(message = 'Hollow Purple') {
        const textEl = this.overlay.querySelector('.jjk-loading-text');
        if (textEl) textEl.textContent = message;
        this.overlay.classList.add('active');
    }

    hide() {
        this.overlay.classList.remove('active');
    }

    updateMessage(message) {
        const textEl = this.overlay.querySelector('.jjk-loading-text');
        if (textEl) textEl.textContent = message;
    }
}

// Global loader instance
const hollowPurpleLoader = new HollowPurpleLoader();

// Convenience functions
window.showLoading = (message) => hollowPurpleLoader.show(message);
window.hideLoading = () => hollowPurpleLoader.hide();
window.updateLoadingMessage = (message) => hollowPurpleLoader.updateMessage(message);