class GestureControls {
    constructor() {
        this.cameraActive = true;
        this.settings = {
            sensitivity: 50,
            zoomSpeed: 30,
            swipeThreshold: 40
        };
        
        this.initElements();
        this.initEventListeners();
        this.loadSettings();
    }
    
    initElements() {
        this.cameraFeed = document.getElementById('camera-feed');
        this.gestureOverlay = document.getElementById('gesture-overlay');
        this.toggleCameraBtn = document.getElementById('toggle-camera');
        this.calibrateBtn = document.getElementById('calibrate-btn');
        this.cameraStatus = document.getElementById('camera-status');
        this.calibrationModal = document.getElementById('calibration-modal');
        this.calibrationClose = document.getElementById('calibration-close');
        this.calibrationCancel = document.getElementById('calibration-cancel');
        this.calibrationSave = document.getElementById('calibration-save');
        
        // Slider elements
        this.sensitivitySlider = document.getElementById('sensitivity');
        this.zoomSpeedSlider = document.getElementById('zoom-speed');
        this.swipeThresholdSlider = document.getElementById('swipe-threshold');
        
        // Value displays
        this.sensitivityValue = document.getElementById('sensitivity-value');
        this.zoomSpeedValue = document.getElementById('zoom-speed-value');
        this.swipeThresholdValue = document.getElementById('swipe-threshold-value');
    }
    
    initEventListeners() {
        this.toggleCameraBtn.addEventListener('click', () => this.toggleCamera());
        this.calibrateBtn.addEventListener('click', () => this.openCalibration());
        this.calibrationClose.addEventListener('click', () => this.closeCalibration());
        this.calibrationCancel.addEventListener('click', () => this.closeCalibration());
        this.calibrationSave.addEventListener('click', () => this.saveSettings());
        
        // Slider events
        this.sensitivitySlider.addEventListener('input', (e) => {
            this.sensitivityValue.textContent = `${e.target.value}%`;
        });
        
        this.zoomSpeedSlider.addEventListener('input', (e) => {
            this.zoomSpeedValue.textContent = `${e.target.value}%`;
        });
        
        this.swipeThresholdSlider.addEventListener('input', (e) => {
            this.swipeThresholdValue.textContent = `${e.target.value}%`;
        });
    }
    
    toggleCamera() {
        this.cameraActive = !this.cameraActive;
        
        if (this.cameraActive) {
            this.cameraFeed.style.display = 'block';
            this.cameraStatus.textContent = 'ON';
            this.toggleCameraBtn.innerHTML = '<i class="fas fa-video-slash"></i> Toggle Camera';
        } else {
            this.cameraFeed.style.display = 'none';
            this.cameraStatus.textContent = 'OFF';
            this.toggleCameraBtn.innerHTML = '<i class="fas fa-video"></i> Toggle Camera';
        }
    }
    
    openCalibration() {
        // Set current values
        this.sensitivitySlider.value = this.settings.sensitivity;
        this.zoomSpeedSlider.value = this.settings.zoomSpeed;
        this.swipeThresholdSlider.value = this.settings.swipeThreshold;
        
        this.sensitivityValue.textContent = `${this.settings.sensitivity}%`;
        this.zoomSpeedValue.textContent = `${this.settings.zoomSpeed}%`;
        this.swipeThresholdValue.textContent = `${this.settings.swipeThreshold}%`;
        
        this.calibrationModal.style.display = 'flex';
    }
    
    closeCalibration() {
        this.calibrationModal.style.display = 'none';
    }
    
    saveSettings() {
        this.settings = {
            sensitivity: parseInt(this.sensitivitySlider.value),
            zoomSpeed: parseInt(this.zoomSpeedSlider.value),
            swipeThreshold: parseInt(this.swipeThresholdSlider.value)
        };
        
        localStorage.setItem('gestureSettings', JSON.stringify(this.settings));
        this.closeCalibration();
    }
    
    loadSettings() {
        const savedSettings = localStorage.getItem('gestureSettings');
        if (savedSettings) {
            this.settings = JSON.parse(savedSettings);
        }
    }
    
    getSettings() {
        return this.settings;
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.gestureControls = new GestureControls();
});