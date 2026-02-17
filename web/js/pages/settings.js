// ========================================
// DECEPTRON - SETTINGS PAGE
// Application settings and preferences
// ========================================

let previewStream = null;

// Enumerate and populate devices
async function enumerateDevices() {
    try {
        const devices = await navigator.mediaDevices.enumerateDevices();
        
        const cameras = devices.filter(d => d.kind === 'videoinput');
        const microphones = devices.filter(d => d.kind === 'audioinput');
        
        populateSelect('camera-select', cameras);
        populateSelect('mic-select', microphones);
        
        // Load saved preferences
        const prefs = await loadPreferences();
        if (prefs.defaultCamera) {
            document.getElementById('camera-select').value = prefs.defaultCamera;
        }
        if (prefs.defaultMic) {
            document.getElementById('mic-select').value = prefs.defaultMic;
        }
    } catch (err) {
        console.error("Error enumerating devices:", err);
    }
}

function populateSelect(selectId, devices) {
    const select = document.getElementById(selectId);
    select.innerHTML = '';
    
    devices.forEach((device, index) => {
        const option = document.createElement('option');
        option.value = device.deviceId;
        option.text = device.label || `Device ${index + 1}`;
        select.appendChild(option);
    });
}

// Save preferences
async function saveSettings() {
    const btn = event.target;
    const originalText = btn.innerText;
    
    try {
        btn.disabled = true;
        btn.innerText = 'Saving...';
        
        const prefs = {
            defaultCamera: document.getElementById('camera-select').value,
            defaultMic: document.getElementById('mic-select').value
        };
        
        const result = await savePreferences(prefs);
        
        if (result.success) {
            btn.innerText = 'Saved!';
            setTimeout(() => {
                btn.innerText = originalText;
                btn.disabled = false;
            }, 1500);
        } else {
            throw new Error(result.message);
        }
    } catch (e) {
        console.error("Save error:", e);
        btn.innerText = "ERROR";
        setTimeout(() => {
            btn.innerText = originalText;
            btn.disabled = false;
        }, 2000);
    }
}

// Start camera preview
async function startCameraPreview() {
    try {
        const cameraId = document.getElementById('camera-select').value;
        
        if (previewStream) {
            previewStream.getTracks().forEach(track => track.stop());
        }
        
        previewStream = await navigator.mediaDevices.getUserMedia({
            video: { deviceId: cameraId ? { exact: cameraId } : undefined }
        });
        
        document.getElementById('camera-preview').srcObject = previewStream;
    } catch (err) {
        console.error("Camera error:", err);
    }
}

// Initialize page
document.addEventListener('DOMContentLoaded', async () => {
    await requireAuth();
    await enumerateDevices();
    
    // Attach event listeners
    document.getElementById('save-settings-btn')?.addEventListener('click', saveSettings);
    document.getElementById('camera-select')?.addEventListener('change', startCameraPreview);
});
