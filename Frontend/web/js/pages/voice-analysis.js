// ========================================
// DECEPTRON - VOICE ANALYSIS UNIT LOGIC
// ========================================

let currentFilePath = null;
let mediaStream = null;
let mediaRecorder = null;
let recordedChunks = [];
let isRecording = false;
let startTime = null;
let timerInterval = null;
let analysisData = null;
let currentLanguage = 'en';

// ── Status Management ─────────────────────────────────────────────────────────

function updateStatusUI(status, label) {
    const tag = document.querySelector('#statusTag span');
    const dot = document.getElementById('statusDot');
    if (!tag || !dot) return;
    
    tag.innerText = label;
    if (status === 'live') {
        dot.className = "w-2 h-2 bg-rose-500 rounded-full animate-pulse shadow-[0_0_10px_rgba(239,68,68,0.5)]";
    } else if (status === 'active') {
        dot.className = "w-2 h-2 bg-emerald-500 rounded-full shadow-[0_0_10px_rgba(16,185,129,0.5)]";
    } else {
        dot.className = "w-2 h-2 bg-slate-600 rounded-full";
    }
}

// ── Recording Logic ───────────────────────────────────────────────────────────

async function toggleRecording() {
    const btn = document.getElementById('recordBtn');
    const recIndicator = document.getElementById('recIndicator');
    const micId = document.getElementById('micSelect').value;

    if (!isRecording) {
        try {
            const constraints = {
                audio: (micId && micId !== 'Loading microphones...') ? { deviceId: { exact: micId } } : true,
                video: false
            };
            mediaStream = await navigator.mediaDevices.getUserMedia(constraints);
            recordedChunks = [];
            
            const options = { mimeType: 'audio/webm;codecs=opus' };
            if (!MediaRecorder.isTypeSupported(options.mimeType)) options.mimeType = 'audio/webm';
            
            mediaRecorder = new MediaRecorder(mediaStream, options);
            mediaRecorder.ondataavailable = (e) => { if (e.data.size > 0) recordedChunks.push(e.data); };
            mediaRecorder.start(1000);
            
            isRecording = true;
            btn.classList.add('bg-rose-600', 'text-white');
            btn.innerHTML = '<i class="fas fa-stop"></i>';
            if (recIndicator) recIndicator.classList.remove('hidden');
            
            startTime = new Date();
            timerInterval = setInterval(updateTimer, 1000);
            updateStatusUI('live', 'Recording Active');
            
        } catch (err) {
            console.error(err);
            showToast("Microphone access denied or error occurred.", "error");
        }
    } else {
        mediaRecorder.stop();
        if (mediaStream) {
            mediaStream.getTracks().forEach(track => track.stop());
            mediaStream = null;
        }
        isRecording = false;
        btn.classList.remove('bg-rose-600', 'text-white');
        btn.innerHTML = '<i class="fas fa-microphone"></i>';
        if (recIndicator) recIndicator.classList.add('hidden');
        clearInterval(timerInterval);

        // Load recorded audio into wavesurfer immediately
        const blob = new Blob(recordedChunks, { type: 'audio/webm' });
        wavesurfer.loadBlob(blob);
        document.getElementById('playBtn').disabled = false;
        
        openSaveModal();
    }
}

function updateTimer() {
    const now = new Date();
    const diff = new Date(now - startTime);
    const h = String(diff.getUTCHours()).padStart(2, '0');
    const m = String(diff.getUTCMinutes()).padStart(2, '0');
    const s = String(diff.getUTCSeconds()).padStart(2, '0');
    document.getElementById("timer").innerText = `${h}:${m}:${s}`;
}

function togglePlayback() {
    if (!currentFilePath && wavesurfer.backend.getPeaks().length === 0) {
        showToast("No audio loaded for playback", "warning");
        return;
    }
    
    if (wavesurfer.isPlaying()) {
        wavesurfer.pause();
        document.getElementById('playBtn').innerHTML = '<i class="fas fa-play"></i>';
    } else {
        wavesurfer.play();
        document.getElementById('playBtn').innerHTML = '<i class="fas fa-pause"></i>';
    }
}

// ── Save Logic ────────────────────────────────────────────────────────────────

function openSaveModal() {
    const m = document.getElementById("saveModal");
    m.classList.remove("hidden");
    setTimeout(() => {
        m.classList.remove("opacity-0");
        m.querySelector("div").classList.remove("scale-95");
    }, 10);
}

function closeSaveModal() {
    const m = document.getElementById("saveModal");
    m.classList.add("opacity-0");
    m.querySelector("div").classList.add("scale-95");
    setTimeout(() => m.classList.add("hidden"), 300);
}

async function saveVoiceData() {
    const subjectId = document.getElementById('subjectIdInput').value || "Unknown_Subject";
    Loader.show("Securing Forensic Audio...");
    
    try {
        const timestamp = new Date().getTime();
        // Switching to .wav extension for better backend compatibility
        const fileName = `voice_${subjectId}_${timestamp}.wav`;
        const blob = new Blob(recordedChunks, { type: 'audio/webm' });
        
        // Convert Blob to File to ensure it has a 'name' property for uploadFile
        const file = new File([blob], fileName, { type: 'audio/webm' });
        
        const finalResult = await uploadFile(file, true);
        
        if (finalResult.success) {
            closeSaveModal();
            currentFilePath = finalResult.data.filepath;
            document.getElementById('playBtn').disabled = false;
            document.getElementById('analyseBtn').classList.remove('hidden');
            updateStatusUI('active', 'Acoustic Data Saved');
            showToast("Session stored in evidence vault", "success");
        } else {
            throw new Error(finalResult.message);
        }
    } catch (e) {
        console.error(e);
        showToast("Error saving: " + e.message, "error");
    } finally {
        Loader.hide();
    }
}

function discardSession() {
    if (confirm("Permanently discard this recording?")) {
        closeSaveModal();
        resetUIState();
        wavesurfer.empty();
    }
}

// ── Analysis Logic ────────────────────────────────────────────────────────────

async function finalizeAnalysis() {
    if (!currentFilePath) {
        showToast("No audio loaded for analysis", "warning");
        return;
    }

    Loader.show("Engaging Acoustic Forensic Engine...");
    try {
        console.log("🎤 Finalizing analysis for:", currentFilePath);
        
        // Use the Eel bridge for consistency and reliability
        const result = await runVoiceAnalysis(currentFilePath);

        if (result.success) {
            updateUI(result.data);
            showToast("Forensic Analysis Complete", "success");
        } else {
            console.error("Analysis failed:", result.message);
            showToast("Analysis Error: " + result.message, "error");
        }
    } catch (error) {
        console.error("Forensic Engine Error:", error);
        showToast("Forensic Engine Connection Failed", "error");
    } finally {
        Loader.hide();
    }
}

function updateUI(data) {
    analysisData = data;
    document.getElementById('emptyState').classList.add('hidden');
    document.getElementById('resultsSection').classList.remove('hidden');
    document.getElementById('analyseBtn').classList.add('hidden');
    const saveBtn = document.getElementById('saveReportBtn');
    if (saveBtn) saveBtn.classList.remove('hidden');

    // Verdict Box
    updateVerdict();
    
    const deception = data.deception_analysis;
    document.getElementById('overallDeceptionScore').innerText = `${deception.overall_deception_score.toFixed(1)}%`;
    document.getElementById('vocalStrainScore').innerText = deception.vocal_strain_score;
    document.getElementById('hesitationScore').innerText = deception.hesitation_score;
    document.getElementById('analysisConfidence').innerText = `${deception.confidence_percent}%`;

    const category = deception.stress_category;
    const catEl = document.getElementById('deceptionCategory');
    catEl.innerText = category;
    catEl.className = 'status-pill inline-block ' + getCategoryClass(category);

    const flagsEl = document.getElementById('triggeredFlags');
    flagsEl.innerHTML = (deception.triggered_flags || []).map(f => 
        `<span class="pill-danger text-[9px] px-2 py-1 rounded-md font-bold uppercase">${f}</span>`
    ).join('');

    // Fundamental Frequency
    const ff = data.fundamental_frequency;
    document.getElementById('f0Mean').innerText = `${ff.f0_mean_hz.toFixed(1)} Hz`;
    document.getElementById('f0Std').innerText = `${ff.f0_std_hz.toFixed(1)} Hz`;
    document.getElementById('f0Range').innerText = `${ff.f0_range_hz.toFixed(1)} Hz`;
    const f0Stab = document.getElementById('f0Stability');
    f0Stab.innerText = ff.stability_status;
    f0Stab.className = 'status-pill text-[9px] ' + getStabilityClass(ff.stability_status);

    // Micro Tremors
    const mt = data.micro_tremors;
    document.getElementById('jitterVal').innerText = `${mt.jitter_local_percent.toFixed(3)}%`;
    document.getElementById('shimmerVal').innerText = `${mt.shimmer_local_percent.toFixed(3)}%`;
    document.getElementById('tremorStabilityScore').innerText = mt.stability_score.toFixed(1);
    const mtStat = document.getElementById('tremorStatus');
    mtStat.innerText = mt.status;
    mtStat.className = 'status-pill text-[9px] ' + getStabilityClass(mt.status);

    // Spectral Clarity
    const sc = data.spectral_clarity;
    document.getElementById('hnrVal').innerText = `${sc.hnr_db.toFixed(1)} dB`;
    document.getElementById('centroidVal').innerText = `${sc.spectral_centroid_mean.toFixed(1)} Hz`;
    document.getElementById('centroidStd').innerText = `${sc.spectral_centroid_std.toFixed(1)} Hz`;
    const scStat = document.getElementById('clarityStatus');
    scStat.innerText = sc.status;
    scStat.className = 'status-pill text-[9px] ' + getStabilityClass(sc.status);

    // Temporal Dynamics
    const td = data.temporal_dynamics;
    document.getElementById('speakingRate').innerText = `${td.speaking_rate_wpm.toFixed(1)} WPM`;
    document.getElementById('pauseRatio').innerText = `${td.pause_ratio_percent.toFixed(1)}%`;
    document.getElementById('longestPause').innerText = `${td.longest_pause_sec.toFixed(2)}s`;
    const tdStat = document.getElementById('temporalStatus');
    tdStat.innerText = td.status;
    tdStat.className = 'status-pill text-[9px] ' + getStabilityClass(td.status);

    // Energy Profile
    const ep = data.energy_profile;
    document.getElementById('rmsMean').innerText = ep.rms_mean.toFixed(4);
    document.getElementById('zcrMean').innerText = ep.zcr_mean.toFixed(4);
    document.getElementById('rmsTrend').innerText = ep.rms_trend;
    const intense = document.getElementById('energyLevel');
    const level = ep.rms_mean > 0.05 ? 'High' : (ep.rms_mean < 0.01 ? 'Low' : 'Normal');
    intense.innerText = level;
    intense.className = 'status-pill text-[9px] ' + (level === 'High' ? 'pill-danger' : 'pill-safe');

    // Transcription
    document.getElementById('transcriptionContent').innerText = data.transcription_original || "No transcription available.";
}

// ── Save Report ────────────────────────────────────────────────────────────────

async function saveVoiceReport() {
    if (!analysisData) {
        showToast("No analysis data to save", "warning");
        return;
    }
    Loader.show("Saving Voice Analysis Report...");
    try {
        const report = {
            type: 'voice',
            source_file: currentFilePath || 'live_recording',
            full_data: analysisData,
            timestamp: new Date().toISOString(),
            analysis_date: new Date().toISOString()
        };
        const result = await eel.save_analysis_report(report)();
        if (result && result.success) {
            showToast("Report saved successfully", "success");
        } else {
            throw new Error(result?.message || "Save failed");
        }
    } catch (e) {
        console.error("Save error:", e);
        showToast("Failed to save report: " + e.message, "error");
    } finally {
        Loader.hide();
    }
}

function setLanguage(lang) {
    currentLanguage = lang;
    const langEn = document.getElementById('langEn');
    const langUr = document.getElementById('langUr');

    if (lang === 'en') {
        langEn.classList.add('bg-primary-blue', 'text-white');
        langEn.classList.remove('text-dim');
        langUr.classList.remove('bg-primary-blue', 'text-white');
        langUr.classList.add('text-dim');
    } else {
        langUr.classList.add('bg-primary-blue', 'text-white');
        langUr.classList.remove('text-dim');
        langEn.classList.remove('bg-primary-blue', 'text-white');
        langEn.classList.add('text-dim');
    }

    if (analysisData) updateVerdict();
}

function updateVerdict() {
    const verdictEl = document.getElementById('deceptionVerdict');
    const d = analysisData.deception_analysis;
    let text = currentLanguage === 'en' ? d.verdict_english : d.verdict_urdu;
    
    // Clean up text: remove semicolons and replace with dots for a more natural look
    text = text.replace(/;/g, '.');
    verdictEl.innerText = text;
}

function getCategoryClass(cat) {
    if (cat === 'Low' || cat === 'Normal') return 'pill-safe';
    if (cat === 'Moderate') return 'pill-warning';
    return 'pill-danger';
}

function getStabilityClass(status) {
    const safe = ['Optimal', 'Stable', 'Clear', 'Fluent', 'Balanced'];
    const warn = ['Moderate', 'Noisy', 'Normal'];
    if (safe.includes(status)) return 'pill-safe';
    if (warn.includes(status)) return 'pill-warning';
    return 'pill-danger';
}

// ── UI Helpers ────────────────────────────────────────────────────────────────

function resetUIState() {
    currentFilePath = null;
    analysisData = null;
    document.getElementById('emptyState').classList.remove('hidden');
    document.getElementById('resultsSection').classList.add('hidden');
    document.getElementById('analyseBtn').classList.add('hidden');
    const saveBtn = document.getElementById('saveReportBtn');
    if (saveBtn) saveBtn.classList.add('hidden');
    document.getElementById('playBtn').disabled = true;
    document.getElementById('timer').innerText = '00:00:00';
    updateStatusUI('ready', 'System Ready');
}

function openVaultSelection() {
    VaultComponent.open((item) => {
        if (item.type !== 'audio' && item.type !== 'video') { 
            showToast("Select an audio or video file", "warning"); 
            return; 
        }
        Loader.show("Syncing Forensic Data");
        currentFilePath = item.filepath;
        wavesurfer.load(item.filepath);
        wavesurfer.on('ready', () => {
            Loader.hide();
            document.getElementById('playBtn').disabled = false;
            document.getElementById('analyseBtn').classList.remove('hidden');
            updateStatusUI('active', 'Vault Data Loaded');
        });
    });
}

async function populateMicrophones() {
    const select = document.getElementById('micSelect');
    if (!select) return;
    try {
        const devices = await navigator.mediaDevices.enumerateDevices();
        const mics = devices.filter(d => d.kind === 'audioinput');
        select.innerHTML = '';
        mics.forEach((m, i) => {
            const opt = document.createElement('option');
            opt.value = m.deviceId;
            opt.text = m.label || `Microphone ${i+1}`;
            select.appendChild(opt);
        });
        if (mics.length === 0) select.innerHTML = '<option>No Microphone Found</option>';
    } catch (err) {
        console.error(err);
    }
}

// ── Lifecycle ─────────────────────────────────────────────────────────────────

document.addEventListener("DOMContentLoaded", async () => {
    const user = await getCurrentUser();
    if (!user) { window.location.href = 'login.html'; return; }
    
    const activeMember = document.querySelector('.active-member-info span.ml-1');
    if (activeMember) activeMember.textContent = `${user.firstName} ${user.lastName} • Unit #${user.username.toUpperCase()}`;

    populateMicrophones();

    const urlParams = new URLSearchParams(window.location.search);
    const autoFile = urlParams.get('file');
    if (autoFile) {
        currentFilePath = autoFile;
        wavesurfer.load(autoFile);
        wavesurfer.on('ready', () => {
            document.getElementById('playBtn').disabled = false;
            document.getElementById('analyseBtn').classList.remove('hidden');
            updateStatusUI('active', 'Vault Data Loaded');
            finalizeAnalysis();
        });
    }
});
