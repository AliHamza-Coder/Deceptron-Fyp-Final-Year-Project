// ========================================
// DECEPTRON - VOICE ANALYSIS PAGE
// Audio recording and voice analysis
// ========================================

let mediaStream = null;
let mediaRecorder = null;
let recordedChunks = [];
let isRecording = false;

// Start audio recording
async function startRecording() {
    try {
        const micId = document.getElementById('mic-select').value;
        
        const constraints = {
            audio: micId ? { deviceId: { exact: micId } } : {
                echoCancellation: true,
                noiseSuppression: true,
                autoGainControl: true
            }
        };
        
        mediaStream = await navigator.mediaDevices.getUserMedia(constraints);
        recordedChunks = [];
        
        const options = {
            mimeType: 'audio/webm;codecs=opus'
        };
        
        mediaRecorder = new MediaRecorder(mediaStream, options);
        
        mediaRecorder.ondataavailable = (event) => {
            if (event.data.size > 0) {
                recordedChunks.push(event.data);
            }
        };
        
        mediaRecorder.start(1000);
        isRecording = true;
        updateStatusUI('recording', 'Recording Audio...');
    } catch (err) {
        console.error("Recording Error:", err);
        alert("Could not start recording: " + err.message);
    }
}

// Stop recording
function stopRecording() {
    if (mediaRecorder && isRecording) {
        mediaRecorder.stop();
        isRecording = false;
        
        if (mediaStream) {
            mediaStream.getTracks().forEach(track => track.stop());
            mediaStream = null;
        }
        
        updateStatusUI('ready', 'Recording Complete');
        setTimeout(() => showSaveDialog(), 500);
    }
}

// Save recording
async function saveRecording() {
    const filename = document.getElementById('session-name').value || 'voice-session';
    
    try {
        Loader.show('Saving audio...');
        
        const blob = new Blob(recordedChunks, { type: 'audio/webm' });
        const result = await uploadFile(blob, true, (progress) => {
            Loader.updateProgress(progress);
        });
        
        if (result.success) {
            alert('Audio saved successfully!');
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

// Load microphones
async function loadMicrophones() {
    try {
        const devices = await navigator.mediaDevices.enumerateDevices();
        const microphones = devices.filter(d => d.kind === 'audioinput');
        
        const select = document.getElementById('mic-select');
        select.innerHTML = '';
        
        microphones.forEach((mic, i) => {
            const option = document.createElement('option');
            option.value = mic.deviceId;
            option.text = mic.label || `Microphone ${i + 1}`;
            select.appendChild(option);
        });
        
        // Load saved preference
        const prefs = await loadPreferences();
        if (prefs.defaultMic) {
            select.value = prefs.defaultMic;
        }
    } catch (err) {
        console.error("Error enumerating microphones:", err);
    }
}

// Initialize page
document.addEventListener('DOMContentLoaded', async () => {
    await requireAuth();
    await loadMicrophones();
});
