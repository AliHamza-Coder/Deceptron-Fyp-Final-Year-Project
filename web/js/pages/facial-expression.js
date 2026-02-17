// ========================================
// DECEPTRON - FACIAL EXPRESSION PAGE
// Video analysis and facial expression detection
// ========================================

let mediaStream = null;
let mediaRecorder = null;
let recordedChunks = [];
let isRecording = false;

// Start camera
async function startCamera() {
    try {
        const cameraId = document.getElementById('camera-select').value;
        
        const constraints = {
            video: cameraId ? { deviceId: { exact: cameraId } } : {
                width: { ideal: 1280 },
                height: { ideal: 720 },
                frameRate: { ideal: 30 }
            }
        };
        
        mediaStream = await navigator.mediaDevices.getUserMedia(constraints);
        document.getElementById('video-feed').srcObject = mediaStream;
        
        updateStatusUI('live', 'Camera Active');
    } catch (err) {
        console.error("Camera error:", err);
        alert("Could not access camera: " + err.message);
    }
}

// Stop camera
function stopCamera() {
    if (mediaStream) {
        mediaStream.getTracks().forEach(track => track.stop());
        mediaStream = null;
        document.getElementById('video-feed').srcObject = null;
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
        
        setTimeout(() => showSaveDialog(), 500);
    }
}

// Save recording
async function saveRecording() {
    const filename = document.getElementById('session-name').value || 'facial-session';
    
    try {
        Loader.show('Saving video...');
        
        const blob = new Blob(recordedChunks, { type: 'video/webm' });
        const result = await uploadFile(blob, true, (progress) => {
            Loader.updateProgress(progress);
        });
        
        if (result.success) {
            alert('Video saved successfully!');
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

// Load cameras
async function loadCameras() {
    try {
        const devices = await navigator.mediaDevices.enumerateDevices();
        const cameras = devices.filter(d => d.kind === 'videoinput');
        
        const select = document.getElementById('camera-select');
        select.innerHTML = '';
        
        cameras.forEach((camera, i) => {
            const option = document.createElement('option');
            option.value = camera.deviceId;
            option.text = camera.label || `Camera ${i + 1}`;
            select.appendChild(option);
        });
        
        // Load saved preference
        const prefs = await loadPreferences();
        if (prefs.defaultCamera) {
            select.value = prefs.defaultCamera;
        }
    } catch (err) {
        console.error("Error enumerating cameras:", err);
    }
}

// Initialize page
document.addEventListener('DOMContentLoaded', async () => {
    await requireAuth();
    await loadCameras();
});
