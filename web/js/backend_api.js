// ========================================
// DECEPTRON - BACKEND COMMUNICATION
// JavaScript helper for talking to Python
// ========================================

/**
 * Get list of all available cameras from Python backend
 * @returns {Promise<Array>} List of camera objects
 */
async function getAvailableCameras() {
    try {
        const cameras = await eel.get_available_cameras()();
        console.log('📷 Available cameras:', cameras);
        return cameras;
    } catch (error) {
        console.error('❌ Error getting cameras:', error);
        return [];
    }
}

/**
 * Get list of all available microphones from Python backend
 * @returns {Promise<Array>} List of microphone objects
 */
async function getAvailableMicrophones() {
    try {
        const mics = await eel.get_available_microphones()();
        console.log('🎤 Available microphones:', mics);
        return mics;
    } catch (error) {
        console.error('❌ Error getting microphones:', error);
        return [];
    }
}

/**
 * Send a video frame to Python for emotion detection
 * @param {HTMLVideoElement} videoElement - The video element with camera feed
 * @returns {Promise<Object>} Emotion detection results
 */
async function detectEmotionFromVideo(videoElement) {
    try {
        // Create canvas to capture frame
        const canvas = document.createElement('canvas');
        canvas.width = videoElement.videoWidth;
        canvas.height = videoElement.videoHeight;
        
        // Draw current video frame to canvas
        const ctx = canvas.getContext('2d');
        ctx.drawImage(videoElement, 0, 0);
        
        // Convert canvas to base64 image
        const base64Image = canvas.toDataURL('image/jpeg', 0.8);
        
        // Send to Python backend
        const result = await eel.process_frame(base64Image)();
        
        return result;
    } catch (error) {
        console.error('❌ Error detecting emotion:', error);
        return {
            success: false,
            error: error.message
        };
    }
}

/**
 * Start real-time emotion detection loop
 * @param {HTMLVideoElement} videoElement - The video element with camera feed
 * @param {Function} callback - Function to call with emotion results
 * @param {number} intervalMs - How often to detect (default: 500ms = 2 times per second)
 * @returns {number} Interval ID (use clearInterval to stop)
 */
function startEmotionDetection(videoElement, callback, intervalMs = 500) {
    console.log('🚀 Starting real-time emotion detection...');
    
    const intervalId = setInterval(async () => {
        const result = await detectEmotionFromVideo(videoElement);
        
        if (result.success && result.face_found) {
            // Call the callback with emotion data
            callback(result);
        } else if (result.success && !result.face_found) {
            // No face detected
            callback({
                success: true,
                face_found: false,
                emotion: 'No Face',
                confidence: 0
            });
        }
    }, intervalMs);
    
    return intervalId;
}

/**
 * Stop real-time emotion detection
 * @param {number} intervalId - The interval ID returned by startEmotionDetection
 */
function stopEmotionDetection(intervalId) {
    if (intervalId) {
        clearInterval(intervalId);
        console.log('⏹️ Stopped emotion detection');
    }
}

// ========================================
// EXAMPLE USAGE (for reference)
// ========================================

/*

// Example 1: Get available devices
async function loadDevices() {
    const cameras = await getAvailableCameras();
    const mics = await getAvailableMicrophones();
    
    // Populate dropdowns
    cameras.forEach(cam => {
        console.log(`Camera ${cam.id}: ${cam.name}`);
    });
}

// Example 2: Real-time emotion detection
const videoElement = document.getElementById('webcam');
let detectionInterval = null;

function startDetection() {
    detectionInterval = startEmotionDetection(videoElement, (result) => {
        // Update UI with emotion
        console.log(`Emotion: ${result.emotion} (${result.confidence})`);
        document.getElementById('emotionLabel').innerText = result.emotion;
    });
}

function stopDetection() {
    stopEmotionDetection(detectionInterval);
}

*/
