// ========================================
// DECEPTRON - LIVE SESSION PAGE
// Live video recording and session management
// ========================================

let mediaStream = null;
let mediaRecorder = null;
let recordedChunks = [];
let isRecording = false;

// Start camera
async function startCamera() {
    try {
        const cameraId = document.getElementById('camera-select').value;
        const micId = document.getElementById('mic-select').value;
        
        const constraints = {
            video: cameraId ? { deviceId: { exact: cameraId } } : true,
            audio: micId ? { deviceId: { exact: micId } } : true
        };
        
        mediaStream = await navigator.mediaDevices.getUserMedia(constraints);
        document.getElementById('webcam').srcObject = mediaStream;
        
        updateStatusUI('live', 'Camera Active');
    } catch (err) {
        console.error("Camera error:", err);
        alert("Could not access camera/mic. Please check permissions.");
    }
}

// Stop camera
function stopCamera() {
    if (mediaStream) {
        mediaStream.getTracks().forEach(track => track.stop());
        mediaStream = null;
        document.getElementById('webcam').srcObject = null;
        updateStatusUI('ready', 'System Ready');
    }
}

// Start recording
async function startRecording() {
    if (!mediaStream) {
        alert("Please start camera first");
        return;
    }
    
    try {
        recordedChunks = [];
        
        const options = {
            mimeType: 'video/webm;codecs=vp9',
            videoBitsPerSecond: 2500000
        };
        
        mediaRecorder = new MediaRecorder(mediaStream, options);
        
        mediaRecorder.ondataavailable = (event) => {
            if (event.data.size > 0) {
                recordedChunks.push(event.data);
            }
        };
        
        mediaRecorder.start(1000);
        isRecording = true;
        updateStatusUI('recording', 'Recording...');
    } catch (err) {
        console.error("Recording error:", err);
        alert("Recording failed: " + err.message);
    }
}

// Stop recording
function stopRecording() {
    if (mediaRecorder && isRecording) {
        mediaRecorder.stop();
        isRecording = false;
        updateStatusUI('live', 'Camera Active');
        
        // Show save dialog
        setTimeout(() => showSaveDialog(), 500);
    }
}

// Save recording
async function saveRecording() {
    const filename = document.getElementById('session-name').value || 'session';
    
    try {
        Loader.show('Saving recording...');
        
        const blob = new Blob(recordedChunks, { type: 'video/webm' });
        const result = await uploadFile(blob, true, (progress) => {
            Loader.updateProgress(progress);
        });
        
        if (result.success) {
            alert('Recording saved successfully!');
            recordedChunks = [];
        } else {
            alert('Save failed: ' + result.message);
        }
    } catch (error) {
        console.error("Save error:", error);
        alert('Save error: ' + error.message);
    } finally {
        Loader.hide();
    }
}

// Load device preferences
async function loadDevicePreferences() {
    try {
        const prefs = await loadPreferences();
        
        if (prefs.defaultCamera) {
            document.getElementById('camera-select').value = prefs.defaultCamera;
        }
        if (prefs.defaultMic) {
            document.getElementById('mic-select').value = prefs.defaultMic;
        }
    } catch (error) {
        console.error("Pref load error:", error);
    }
}

// Initialize page
document.addEventListener('DOMContentLoaded', async () => {
    await requireAuth();
    await loadDevicePreferences();
    
    // Enumerate devices
    const devices = await navigator.mediaDevices.enumerateDevices();
    const cameras = devices.filter(d => d.kind === 'videoinput');
    const mics = devices.filter(d => d.kind === 'audioinput');
    
    // Populate selects
    populateSelect('camera-select', cameras);
    populateSelect('mic-select', mics);
});

function populateSelect(id, devices) {
    const select = document.getElementById(id);
    select.innerHTML = '';
    devices.forEach((device, i) => {
        const option = document.createElement('option');
        option.value = device.deviceId;
        option.text = device.label || `Device ${i + 1}`;
        select.appendChild(option);
    });
}
