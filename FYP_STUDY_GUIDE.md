# Deceptron FYP — Study Guide (Know Your Project)

This guide is written to help you answer viva / presentation questions about your
own project. It is organised in three parts:

1. **Page-by-page questions** — what each screen does and what happens when you click things.
2. **Folder & file questions** — why every folder and key file exists.
3. **Module & function questions** — what each backend class/function does and where it fits in the pipeline.

Read the answers in your own words. Do not memorise word-for-word — understand the idea behind each answer.

---

## Part 1 — Project Overview (asked first, sets the tone)

**Q1. What is your project?**
> Deceptron is a desktop application for deception detection. It takes a video/audio of an interview and analyses three things: facial behaviour (micro-expressions, gaze, head pose, lip/jaw tension, asymmetry, hand-to-face touching), voice stress (pitch, jitter, shimmer, speaking rate, pauses), and language (linguistic signs of deception like evasion, vagueness, contradiction). All three signals are combined into one deception score with a confidence level.

**Q2. What problem does it solve?**
> Investigators and researchers need a second opinion on interviews. A human can't watch eye movement, pitch changes, and word choice at the same time. The system does this automatically and shows which cues triggered the score, so a human can review the evidence instead of trusting a number blindly.

**Q3. What is the tech stack in one line?**
> Python 3.9+, PyTorch and MediaPipe for face analysis, HSEmotion for emotion, Praat/Parselmouth for voice acoustics, Whisper for transcription, PyAnnote for speaker diarization, Groq (Llama-3.3-70B) for language analysis, FastAPI for the backend API, Eel + vanilla JavaScript for the desktop UI, TinyDB for storage.

**Q4. Is it offline or online?**
> Mostly offline. Face, voice, emotion, diarization and transcription all run with local models. Only the NLP language analysis calls the Groq cloud API. That is a deliberate design choice — the heavy work does not depend on the internet.

**Q5. What is the overall architecture?**
> The desktop UI (Eel) talks to a FastAPI backend. The backend runs the pipeline: diarization → segmentation → per-segment analysis (6 face modules + voice + emotion + NLP in parallel) → fusion engine → report saved to TinyDB. Results are shown in the UI.

**Q6. How is the final score calculated?**
> A weighted fusion: Face behavioural cues 35%, Voice stress 25%, NLP language 25%, Face emotion 10%, Cross-modal mismatch 5%. Bonus rules add points (e.g. multiple cues firing together +15). The result is a 0–100 deception score plus a confidence level (LOW / MEDIUM / HIGH / CRITICAL).

---

## Part 2 — Page-by-Page Questions

### Login / Signup / Forgot Password / Reset Password
**Q. How does authentication work?**
> Passwords are hashed with SHA-256 plus a random salt before storing in TinyDB. Sessions are tracked by the app, and the user stays logged in across restarts.
>
> Signup sends a verification email through the email module (SMTP). Forgot/reset password use a reset token emailed to the user.

**Q. Why SHA-256 + salt instead of a library like bcrypt?**
> Honest answer: simplicity and portability. SHA-256 + salt is a reasonable choice for an academic project with local-only storage. A production app should use bcrypt/argon2 — that can be listed as future work.

### Dashboard
**Q. What does the dashboard show?**
> A trend chart (doughnut) splitting saved reports into **High Risk** and **Trustworthy**, plus counters and a recent-analysis history list. It reads directly from TinyDB.

**Q. How is "risk" decided?**
> Each report's deception score is bucketed at 50: scores **above 50 → High Risk**, scores **at or below 50 → Trustworthy**. The dashboard colours the history rows by the same logic.

### Start Session (the main demo page)
**Q. What can the user do on this page?**
> Three things: record live (webcam + mic), load a pre-recorded video, or upload a file. Then click **Analyse** to run the full pipeline.

**Q. What happens after clicking Analyse?**
> The video goes to the backend `/analyze/pipeline` endpoint. The pipeline: extracts audio with FFmpeg → diarizes speakers → splits the suspect's answers into segments → analyses each segment (face, voice, emotion, NLP) → fuses scores → returns the full result. The UI then shows:
> - overall risk display and timeline chart (per-second truth score)
> - transcript segments with timestamps (English + original language)
> - NLP deception indicators card
> - fusion score breakdown bars (face / emotion / voice / NLP / mismatch)
> - 6 face tabs (emotion, eye gaze, lip-jaw, head pose, asymmetry, hand touch)
> - cross-modal flags and bilingual verdict (English + Roman Urdu)
> - annotated output video

**Q. What is the behavioural baseline?**
> The first 10 seconds of the video are treated as the person's "normal" behaviour. Everything after that is compared against this baseline, so the analysis is personalised rather than comparing everyone to one average.

**Q. Why is the verdict bilingual?**
> Because the target use case is Urdu/English interviews. The reasoning engine writes the explanation in English and Roman Urdu so it is useful to local investigators.

### Facial Expression (single-module view)
**Q. What does this page do?**
> It lets you run one or more face modules on a video and see detailed per-module output: circular charts (emotion distribution, eye gaze, lip/jaw, pose, asymmetry, hand touch), tables, and the dominant emotion over time.

**Q. Which face modules exist?**
> Six: eye gaze (blink rate, gaze direction, fixation), head pose (pitch/yaw/roll, nodding/shaking), lip & jaw tension (jaw tightness, lip compression), facial asymmetry (mouth/brow/eye), hand-to-face touch, and emotion (HSEmotion).

### Voice Analysis
**Q. What does this page do?**
> Runs the voice-only analysis on a recording or file: waveform display, then acoustic metrics — jitter, shimmer, HNR (harmonics-to-noise ratio), spectral centroid, speaking rate (WPM), pause ratio, hesitation — plus Whisper transcription and a stress category (Low / Moderate / High-Controlled / High-Genuine / Critical). The report can be saved.

**Q. What does the voice analyzer actually measure?**
> It uses Parselmouth (Praat) to extract F0 (pitch), jitter and shimmer (voice micro-tremors), and HNR. Speech rate and pause ratio come from the transcription timing. High jitter/shimmer and high pause ratios are treated as stress indicators.

### Uploads (Evidence Vault)
**Q. What is the Evidence Vault?**
> A media management area. Files are uploaded in 1 MB chunks (good for large videos), listed with type filters (video/audio), previewed (audio via WaveSurfer), downloaded, or deleted.

### Reports
**Q. What does the reports page do?**
> Lists all saved reports (from start-session, voice, facial pages). You can search, filter by type, export a report as JSON, delete it, or open the detail page.

### Report Detail
**Q. What does the detail page show?**
> The full saved report: final score, per-module breakdown, the truth timeline chart, the transcript with click-to-seek into the output video, active cues, and the saved notes area.

### Profile & Settings
**Q. What are these pages?**
> Profile: edit name/username, upload avatar, change password. Settings: choose camera and microphone, brightness/contrast/saturation sliders, and mirror toggle for the live view.

---

## Part 3 — Folder & File Structure Questions

### Root
| Path | What it is |
|---|---|
| `README.md` | Project overview and setup guide (this is your first impression on GitHub). |
| `PRESENTATION_PREP.md` | Demo flow + examiner questions + UI audit notes (your private prep doc). |
| `FYP_STUDY_GUIDE.md` | This document. |
| `SYSTEM_ACCURACY_EXPLANATION.md` | Explains the 89.1% accuracy estimate and how it was derived. |
| `calculate_system_accuracy.py` | Script that computes the accuracy estimate from published benchmark accuracies weighted by the fusion weights. |
| `testvideo.mp4`, `Untitled design.mp4` | Test media (kept out of GitHub — see `.gitignore`). |
| `Output of pipeline api.txt` | A saved sample of raw pipeline API output from a test run. |
| `.gitignore` | Tells git what not to upload (env files, models, venv, videos). |

### Backend
| Path | What it is |
|---|---|
| `backend/server.py` | FastAPI entry point. Registers the routers: voice, emotion, face, pipeline. |
| `backend/requirements.txt` | All Python dependencies for the backend. |
| `backend/.env` / `.env.example` | Groq API key (`.env` is real, never commit it; `.env.example` is the template). |
| `backend/download_models.py` | Pre-downloads Whisper and PyAnnote models so they run offline. |
| `backend/build_backend.ps1`, `deceptron_backend.spec` | PyInstaller packaging for the backend. |
| `backend/modules/main.py` | CLI entry that runs the pipeline from the command line for testing. |
| `backend/modules/test_apis.py` | Small script to test the HuggingFace token and Groq API key. |
| `backend/api/routes/` | FastAPI routers: `voice.py`, `emotion.py`, `face.py`, `pipeline.py`. |
| `backend/local_models/` | Downloaded model weights (diarizer, embedding, segmenter, whisper) — offline inference. |
| `backend/myenv/` | The Python virtual environment (never commit this). |

### Frontend
| Path | What it is |
|---|---|
| `frontend/main.py` | Desktop app entry point — starts Eel with the web UI. |
| `frontend/web_app.py` | Alternative launcher that serves the UI in a normal browser. |
| `frontend/config.py` | Backend URL + SMTP config, loads from `~/.deceptron/config.json` and `.env`. |
| `frontend/RUN.bat` | One-click Windows launcher. |
| `frontend/main.spec` | PyInstaller spec for the desktop executable. |
| `frontend/modules/database.py` | All TinyDB operations (users, reports, uploads, settings). |
| `frontend/modules/email_sender.py` | SMTP email sending (verification, password reset). |
| `frontend/modules/email_templates/` | HTML email templates (verify, welcome, reset password). |
| `frontend/web/index.html` | App shell / redirect. |
| `frontend/web/pages/` | One HTML file per page (login, dashboard, start-session, reports, etc.). |
| `frontend/web/js/common/` | Shared JS: `api.js` (backend calls), `auth.js`, `utils.js`, `constants.js`, `media-recorder.js`. |
| `frontend/web/js/components/` | Reusable UI: `sidebar.js`, `loader.js`, `media-preview.js`, `vault-component.js`. |
| `frontend/web/js/pages/` | External page scripts. Note: most pages keep logic inline; only the auth pages and voice-analysis load their external JS. |
| `frontend/web/styles/output.css` | Compiled stylesheet (custom Tailwind build). |
| `frontend/web/scripts/` | Vendored libraries: `chart.min.js`, `wavesurfer.min.js`. |

**Likely question:** *"Why is some logic inline in HTML instead of in the JS files?"*
> Answer honestly: the final version was consolidated into inline scripts for simplicity of shipping a desktop app with Eel. Some older external JS files still exist but are not loaded. The auth pages and voice analysis do use their external JS.

---

## Part 4 — Module & Function Questions (Backend)

### `speaker_diarizer.py` — `SpeakerDiarizer`
**What it does:** Identifies **who spoke when** using the PyAnnote audio pipeline (offline, local `config.yaml`).
**Key function:** `diarize(audio_path)` → returns speaker turns with labels and time ranges.
**Likely Q:** *Why do you need diarization?* — So the system can separate the **suspect's** answers from the **interviewer's** questions without manual annotation. The suspect is picked as the speaker with the most talking time.

### `segment_manager.py` — `SegmentManager`
**What it does:** Turns diarized audio + Whisper transcription into **answer segments** for the suspect.
**Key functions:**
- `get_suspect_segments(audio_path, suspect_label)` → ordered list of suspect segments.
- `_split_by_silence(...)` → splits long answers (>15 s) on silence; minimum segment ~1.5–2 s; very quiet sub-segments (RMS below 0.005) are discarded.
- `_merge_segments(...)` → joins tiny fragments separated by <0.5 s.
- `_transcribe_block(...)` → Whisper transcription per block.
**Likely Q:** *Why split long answers?* — A 60-second rambling answer mixes many ideas; splitting gives one analysis per idea, so cues are easier to interpret and cross-check.

### `forensic_voice_analyzer.py` — `ForensicVoiceAnalyzer`
**What it does:** Voice stress analysis using Parselmouth (Praat) + pure-NumPy signal processing, plus Whisper transcription.
**Key functions:**
- `calibrate(neutral_wav)` → personal baseline from neutral speech.
- `analyze(wav_path)` → full acoustic analysis.
- `analyze_segment(wav, start, end)` → per-segment analysis.
- `_analyze_core_from_array(y, sr)` → jitter, shimmer, HNR, F0 stats, RMS, centroid.
- `_compute_spectral_centroid(y, sr)` → brightness of the voice spectrum.
**Outputs:** F0 (mean/std/min/max, Flat/Stable/Unstable), jitter (local, ppq5), shimmer (local, apq11), HNR, speaking rate (WPM), pause ratio, hesitation flag, energy trend, stress category, silence handling, transcription (original + English).
**Likely Q:** *What are jitter and shimmer?* — Tiny cycle-to-cycle variations in pitch and amplitude of the voice. They rise under tension and are classic acoustic stress markers.

### `emotion_detection_module.py` — `EmotionAnalyzer`
**What it does:** Frame-by-frame facial emotion classification with **HSEmotion** (model `enet_b0_8_best_vgaf`).
**Key functions:** `process_video(...)`, `get_summary(frame_data)`.
**Outputs:** dominant emotion per frame + confidence, emotion distribution, controlled-expression score used by the fusion engine.

### `eye_gaze_module.py` — `EyeGazeAnalyzer`
**What it does:** Gaze direction + blink detection using MediaPipe landmarks.
**Key functions:** `get_ear(eye_pts)` computes the **Eye Aspect Ratio** (EAR) — the ratio of eye height to width, which drops sharply during a blink — and `process_video(...)`, `get_summary(...)`.
**Outputs:** blink count/rate, gaze distribution (centre/left/right), fixation score, gaze stability, blink-rate spikes.

### `head_pose_module.py` — `HeadPoseAnalyzer`
**What it does:** Estimates head orientation from face landmarks (solvePnP-style) and converts the rotation matrix to Euler angles.
**Key functions:** `_rotation_matrix_to_euler_angles(R)`, `process_video(...)`, `get_summary(...)`.
**Outputs:** pitch / yaw / roll, withdrawal score, stiffness, nodding and shaking detection.

### `lip_jaw_module.py` — `LipJawAnalyzer`
**What it does:** Measures mouth and jaw tension.
**Key functions:** `process_video(...)`, `get_summary(...)`.
**Outputs:** jaw tightness, lip compression, chin tremor, lip disappearance (e.g. lip pressing/sucking).

### `asymmetry_module.py` — `AsymmetryAnalyzer`
**What it does:** Measures left–right facial asymmetry of mouth, brows, and eyes.
**Key functions:** `_raw_asymmetry(...)`, `process_video(...)`, `get_summary(...)`.
**Outputs:** asymmetry scores relative to the behavioural baseline. Increased asymmetry can appear under stress.

### `hand_face_touch_module.py` — `HandFaceTouchAnalyzer`
**What it does:** Detects self-adaptor gestures (hand touching face/mouth/nose/eyes) using hand + face landmark distances.
**Key functions:** `_get_regions_def(...)`, `process_video(...)`, `get_summary(...)`.
**Outputs:** touch count, which regions were touched, timeline of touches.

### `nlp_deception_module.py` — `NLPDeceptionAnalyzer`
**What it does:** Sends the transcript to **Groq (Llama-3.3-70B-Versatile)** and parses the JSON response into deception indicators.
**Key functions:**
- `analyze(...)` — main entry (text + optional voice stress + question context).
- `_preprocess_text(...)` — local heuristics (filler words, first-person pronouns, hedging) injected before the LLM call.
- `_build_prompt(...)` — builds the prompt with a strict JSON output format.
- `_call_groq_with_retries(...)` — calls the API, up to 2 retries.
- `_parse_response(...)` — converts the model's JSON into structured scores.
- `_unanalyzable_result(...)` — safe fallback for empty/very short transcripts.
**Indicators:** evasion, over-explanation, irrelevance, contradiction, vagueness, improbable details, cognitive load, distancing language, plus emotion mismatch and cross-segment contradiction. Responses are cached by MD5 to avoid repeated API calls.
**Likely Q:** *Why Groq instead of a local LLM?* — Speed (high token throughput) and no local GPU requirement for the LLM. The rest of the system is offline; only this needs internet.

### `reasoning_engine.py` — `ReasoningEngine`
**What it does:** Turns a segment's data into a **bilingual explanation** (English + Roman Urdu) so the verdict is readable, not just a number.
**Key functions:** `explain(segment_data)`, `_build_prompt(data)`.

### `fusion_engine.py` — `FusionEngine`
**What it does:** The decision layer. Combines face, emotion, voice, NLP and mismatch into the final score and verdict.
**Key functions:**
- `fuse(...)` — main entry, applies weights and bonus rules.
- `_compute_base_score(...)` — weighted combination (35/10/25/25/5).
- `_mismatch_score(...)` — penalises conflicts (e.g. calm face + high voice stress).
- `_build_active_cues(...)` — collects which cues fired, with severity/timestamp.
- `_generate_verdict(...)` — score → confidence level + verdict.
- `explain()` — human-readable explanation of the decision.
**Bonus rules:** multi-cue clustering (+15 when several cues fire together), NLP + lip-disappear confirmation (+10).

### `deception_pipeline.py` — `DeceptionPipeline`
**What it does:** Orchestrates the whole run — this is what `/analyze/pipeline` calls.
**Key functions:**
- `process(video_path, audio_path)` — main entry: extract audio → baseline → diarize → segment → analyse each segment → fuse → report.
- `_extract_audio(...)` — FFmpeg audio extraction.
- `_analyze_baseline(...)` — builds the 10-second personal baseline.
- `_detect_conflicts(...)` — cross-modal conflict detection.
- `_detect_spikes(...)` — sudden changes vs baseline.
- `_generate_annotated_videos(...)`, `_create_combined_video(...)` — annotated + 2×2 combined output video.

### `api/routes/` — FastAPI routers
| Router | Endpoints |
|---|---|
| `voice.py` | `/analyze/voice` (GET/POST) — voice-only analysis |
| `emotion.py` | `/analyze/emotion` — emotion analysis |
| `face.py` | `/analyze/face/gaze`, `/analyze/face/pose`, `/analyze/face/touch`, `/analyze/face/lipjaw`, `/analyze/face/asymmetry`, `/analyze/face/emotion`, `/analyze/face` (parallel all-modules) |
| `pipeline.py` | `/analyze/pipeline` — full end-to-end analysis |

Interactive docs at `http://localhost:8000/docs`.

---

## Part 5 — Scoring, Accuracy & Honest Answers

**Q. Where does 89.1% come from?**
> It is an **estimate**, not a tested result. `calculate_system_accuracy.py` takes published benchmark accuracies for each component (emotion model, diarization, etc.) and averages them weighted by the same weights used in the fusion engine (35/10/25/25/5). The honest position: the system was not validated on a labelled deception dataset; that is listed as future work.

**Q. How do I read the deception score (the %)?**
> The score is 0–100. **Above 50 means higher lying risk; at or below 50 means the person seems more truthful.** The dashboard splits saved reports exactly on this line (High Risk vs Trustworthy), and each score is always shown with a confidence level (LOW / MEDIUM / HIGH / CRITICAL).

**Q. What are the weights and why?**
> Face behavioural 35% (strongest — most deception-research evidence), voice 25%, NLP 25%, emotion 10%, mismatch 5%. These are rule-based choices, not machine-learned. Own this honestly.

**Q. Is this a lie detector?**
> No — and say so. It outputs cues + a score + confidence, as an assistive tool. It is not admissible evidence and not a polygraph replacement. Deception research itself is contested; the system is designed to flag cues for a human to review.

**Q. What are the limitations?**
> - No validation on a labelled deception dataset.
> - NLP needs internet (Groq).
> - Baseline depends on the first 10 seconds being "normal".
> - Works best with good lighting, clear audio, and a visible face.
> - Cultural/individual differences in behaviour are only partially handled by the personalised baseline.

**Q. What would you do as future work?**
> Test on RLDD / Miami Deception datasets, add a local LLM option, add real-time continuous analysis, and strengthen the fusion weights using actual measured data.

---

## Part 6 — Quick Revision Tables

### Fusion weights
| Modality | Weight |
|---|---|
| Face behavioural cues | 35% |
| Voice stress | 25% |
| NLP deception | 25% |
| Face emotion (controlled) | 10% |
| Cross-modal mismatch | 5% |

### Pipeline order
```
video → FFmpeg audio → diarize (PyAnnote) → suspect segments (Whisper + VAD)
     → per segment: 6 face modules + voice + emotion + NLP (parallel)
     → fusion engine → score + verdict + bilingual reasoning → report (TinyDB)
```

### Key numbers to remember
| Fact | Value |
|---|---|
| Baseline window | first 10 seconds |
| Long-answer split threshold | > 15 seconds (VAD on silence) |
| Minimum segment length | ~1.5–2 s; quiet sub-segments < RMS 0.005 dropped |
| Face module parallelism | 6 modules via `ThreadPoolExecutor(max_workers=6)` |
| NLP retries | 2 retries on Groq API |
| NLP cache | MD5-hashed result cache |
| Storage | TinyDB at `~/.deceptron/db.json` |
| Auth hashing | SHA-256 + salt |
| Dashboard risk split | > 50 High Risk, ≤ 50 Trustworthy |
| Confidence levels | LOW / MEDIUM / HIGH / CRITICAL |
| Voice stress categories | Low / Moderate / High-Controlled / High-Genuine / Critical |

### Pages at a glance
| Page | One-line purpose |
|---|---|
| login / signup / forgot / reset | Account + email verification |
| dashboard | Risk analytics + history |
| start-session | Live/file pipeline analysis (main demo) |
| facial-expression | Per-module face analysis with charts |
| voice-analysis | Voice-only stress + transcription |
| uploads | Evidence vault (chunked uploads, preview) |
| reports | Saved report list, search, export |
| report-detail | Single report deep-dive |
| profile / settings | Account & camera/mic preferences |

---

*Read this alongside `PRESENTATION_PREP.md` (demo flow + examiner questions) and `SYSTEM_ACCURACY_EXPLANATION.md` (accuracy methodology). No code is needed to study from this guide — it matches the current project state.*
