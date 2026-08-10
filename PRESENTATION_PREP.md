# Deceptron FYP — Presentation Preparation Guide

This document helps you prepare for the final presentation/viva. It contains:

1. Demo readiness checklist
2. Suggested presentation flow
3. Likely examiner questions and honest answers
4. Full page-by-page UI audit (what works, what is dead/broken)
5. Suggested fix plan (nothing in this document modifies code)

---

## 1. Demo Readiness Checklist

| Item | Status | Notes |
|---|---|---|
| Test videos | OK | `testvideo.mp4` + `Untitled design.mp4` exist in root — but both are synthetic/robot-voiced clips. Record a REAL human clip for the demo. |
| Backend `.env` | Present | Groq API key inside. Verify the key is valid BEFORE the demo (NLP card will be empty if it expired). |
| Frontend `.env` | Present | SMTP config for email verification. |
| AI models | Downloaded | `diarizer`, `embedding`, `segmenter`, `whisper` in `backend/myenv/local_models/` — the heavy models run OFFLINE. |
| `RUN.bat` | Present | `frontend/RUN.bat` — quick Windows launcher. |
| Sample pipeline output | Present | `Output of pipeline api.txt` (1MB real run). |

**Biggest demo risk:** `testvideo.mp4` is synthetic. Record yourself answering a question on camera — you know the ground truth, and it is far more convincing to examiners.

**Second risk:** NLP (Groq) needs internet. If the API key is dead or the network fails, the NLP card and bilingual verdicts will be empty. Have a fallback (pre-computed report) ready.

---

## 2. Suggested Presentation Flow (~12-15 minutes)

1. **Problem & motivation** (2 min) — why deception detection matters in investigations.
2. **Architecture** (2 min) — walk the README ASCII diagram: Frontend (Eel) → FastAPI → 5 module groups → Fusion Engine → TinyDB.
3. **Live demo** (6-8 min) — camera on, record ~30-60s, run analysis. Show: face tabs (6), voice waveform, NLP flags, fusion breakdown bars, bilingual verdict, timeline chart.
4. **Accuracy (89.1%)** (2 min) — say the word **"estimated"** first. Show `calculate_system_accuracy.py`: weighted average of published benchmark accuracies, matched to `fusion_engine.py` weights.
5. **Limitations + future work** (1 min) — naming limitations yourself makes you look honest and in control.

---

## 3. Likely Examiner Questions & Honest Answers

### Q1: "Did you test this on a real deception dataset?"
**Answer:** Be honest — "Not on a labeled dataset. The 89.1% is an estimate built from published model benchmarks. Testing on RLDD / Miami Deception Dataset is listed as future work." Lying here is the fastest way to fail.

### Q2: "Why those weights (35/10/25/25/5)?"
**Answer:** Visual cues are considered the strongest signal in deception research (Ekman micro-expressions; DePaulo meta-analysis), so face gets the largest weight. The fusion engine itself only combines channels, so it gets the smallest (5%). They are rule-based choices, not measured optimization — own that.

### Q3: "Deception detection science is controversial. Micro-expressions don't reliably predict lying."
**Answer:** "I agree — that is why the system outputs cues plus a confidence level (LOW/MEDIUM/HIGH/CRITICAL), not a definitive 'liar' verdict. It is an assistive tool for investigators, not a polygraph replacement."

### Q4: "What happens without internet?"
**Answer:** Face, voice, emotion and diarization all run offline with local models. Only NLP (Groq) needs the internet. This is a strength — emphasize it.

### Q5: "Why did you use Groq instead of a local LLM?"
**Answer:** Speed (token throughput) + no local GPU needed for the LLM. Plus an MD5-hashed result cache reduces repeated API calls.

### Q6: "What is the difference between voice stress score and deception score?"
**Answer:** The voice analyzer computes acoustic markers (jitter, shimmer, pitch, HNR, pause ratio) → a voice stress score. The fusion engine then combines face + emotion + voice + NLP + mismatch into one final deception score with weighted rules.

---

## 4. Full Page-by-Page UI Audit

> **Method note:** I cross-referenced every HTML `id` against every JS reference (external files AND inline `<script>` blocks) and traced the analyze-button flows. Findings below are read-only — nothing was changed.

### Architecture finding (important for your understanding)
Most pages keep their logic **inline in the HTML** (`<script>` blocks), NOT in the separate `frontend/web/js/pages/*.js` files. Only 5 pages load their external page-JS:
- `login.html` → `login.js` ✅
- `signup.html` → `signup.js` ✅
- `forgot-password.html` → `forgot-password.js` ✅
- `reset-password.html` → `reset-password.js` ✅
- `voice-analysis.html` → `voice-analysis.js` ✅

The following page-JS files exist but are **NOT loaded by any page** (dead files — the real logic is inline):
`dashboard.js`, `facial-expression.js`, `profile.js`, `settings.js`, `start-session.js`, `uploads.js`

> **Presentation tip:** If an examiner opens these JS files expecting page logic, they will find unused code. You can either delete these 6 files or (better) explain that the final version moved logic inline for simplicity. Do NOT claim they are the active logic.

---

### 4.1 `login.html` / `signup.html` / `forgot-password.html` / `reset-password.html` — ✅ WORKING
- Each loads its page JS correctly.
- `loginPwd` / `signupPwd` IDs are referenced (they use `.value` access — my initial audit flagged them as dead, but they are read via `document.querySelector`/form field access, so they work).
- Auth flow works: login, signup (with email verification via SMTP), forgot/reset password.
- **Note:** `index.html` contains a ~1-line inline script only (likely a redirect). No issue.

---

### 4.2 `dashboard.html` — ✅ WORKING (inline JS)
- Loads user data, renders the trend doughnut chart, and the three risk counters (`highRiskCount`, `midRiskCount`, `lowRiskCount`) via `updateTrendChart()`.
- Recent analysis list populates the `.space-y-2` container. **One dead ID:** `recentAnalysisContainer` exists in HTML but is never referenced — the JS uses a class selector (`.space-y-2`) instead. Cosmetic only; the section still fills with data.
- `theme-toggle` reference in `dashboard.js` is a broken ref, but `dashboard.js` is not loaded anyway (see above). No runtime effect.

---

### 4.3 `start-session.html` — ✅ WORKING (main demo page, ~1385 lines inline JS)
This is the star page. Verified data flow after clicking **Analyse**:
- `finalizeAnalysis()` → `runFullPipeline()` (backend `/analyze/pipeline`) → `updatePipelineUI()`.
- Populated correctly: overall risk display, timeline chart (`truthChart`), transcript (`segTransLabel_*`/`segTransText_*` dynamic IDs), NLP card (`nlpFlagsContainer`, `nlpSummaryText`, language toggle), vocal timeline table (`frameTableBody`), 6 face tabs (`emotionTableBody`, `eyeGazeTableBody`, `lipJawTableBody`, `headPoseTableBody`, `asymmetryTableBody`, `touchTableBody`), fusion breakdown bars (`fbFaceBehavioral` + `barFaceBehavioral`, etc.), cross-modal flags, bilingual verdict (`fusionVerdictText`), output video (`sessionOutputVideo`).
- Face tab switching works (`switchFaceTab`).
- **Dead/hidden UI to be aware of:** `frameOverlay` + `currentFrameNum` + `currentFrameEmotion` — a decorative "frame overlay" that is `display:none` and never updated. Harmless, but if an examiner inspects the DOM they'll see placeholder text ("Frame 0001 / 0144", "Anger: 88.4%"). Optional cleanup.
- **Duplicate script loads:** `constants.js`, `sidebar.js`, `vault-component.js` are loaded twice in this page (once in `<head>`, once in body). Harmless (browser dedupes) but sloppy — fix by removing the duplicate block.

---

### 4.4 `facial-expression.html` — ⚠️ WORKS but has dead/duplicate UI
- Inline JS (~960 lines) correctly populates: emotion/gaze/lip-jaw/head/pose/asymmetry charts + tables, `statusTag`, `webcam`, `videoOutputGrid`.
- **Real issue #1 — duplicate IDs:** `mainVideoWrap` appears **3×** and `outputVideoSingle` **2×** in the HTML (leftover duplicated blocks). Duplicate IDs are invalid HTML; `getElementById` returns the first match. The page still works, but this is sloppy and an examiner might notice in devtools.
- **Real issue #2 — dead IDs:** `asymScoreLabel`, `oralScoreLabel` exist but are never updated (the percent value updates, the label stays at default "Balance"/"Activity"). Cosmetic.
- `clearVaultBtn`, `circularGraphsSection` are referenced in the page's JS partially — `circularGraphsSection` itself is never toggled (its children are updated directly). Cosmetic.

---

### 4.5 `voice-analysis.html` — ✅ WORKING
- Loads `voice-analysis.js` + inline script. Verified flow: record → save → `finalizeAnalysis()` → `runVoiceAnalysis()` (backend `/analyze/voice`) → `updateUI()` populates score, jitter/shimmer, HNR, centroid, WPM, pause ratio, transcription, verdict.
- `waveform` (6 refs) works (WaveSurfer). `statusTag`/`verdictBox` are updated via `updateStatusUI` (uses class selectors) — work fine.
- Save report flow works (`saveVoiceReport`).

---

### 4.6 `uploads.html` — ✅ WORKING
- Inline JS handles: file upload (chunked via `initiate_upload`/`append_upload_chunk`/`finalize_upload`), media list render, preview (media-preview.js IS loaded here — it is the only page that uses it), delete with confirm modal (`confirm-modal`, `modal-confirm`), toast notifications.
- `fileInput`, `mediaList`, `toast-container` all referenced. Works.

---

### 4.7 `reports.html` — ✅ WORKING
- Inline JS: loads all reports, search (`searchInput`), section filter tabs, renders cards with risk color coding, export JSON, delete modal (`deleteModal`, `confirmDeleteBtn`, `deleteBtnText`, `deleteSpinner`). Verified `viewReport(id)` → `report-detail.html?id=...`. All good.

---

### 4.8 `report-detail.html` — ⚠️ WORKS but has 2 dead items
- Inline JS (~575 lines) renders the report: score display, radial metrics, `truthChart` timeline, transcript with click-to-seek into `reportVideo`, `archiveNotes` loading.
- **Real issue — dead "Save Notes" button:** `saveNotesBtn` exists in HTML but **no JS references it** — clicking it does nothing. Either wire it (save `archiveNotes` to DB) or hide/remove it before the demo. This is the most user-visible dead button in the app — an examiner clicking it will notice.
- `voiceWaveform` ID exists but is never populated (no WaveSurfer attached in this page). Cosmetic — consider removing.

---

### 4.9 `profile.html` — ✅ WORKING (with one dead ID)
- Inline JS: loads user, shows avatar/name/email/member-since, edit modal (`edit-modal`), password change (`edit-current-pwd`, `edit-new-pwd`), avatar upload (`avatar-upload`), `saveProfile()` wired to the Save button. Works.
- Dead ID: `avatar-container` (unused; the display avatar uses `display-avatar`). Cosmetic.
- Note: `profile.js` (external) is NOT loaded — logic is inline. See architecture note.

---

### 4.10 `settings.html` — ✅ WORKING
- Inline JS: camera/mic selectors (`camSelect`), brightness/contrast/saturation sliders, mirror toggle, status tag, toggles — all referenced and wired. Works.
- `settings.js` external file NOT loaded — logic inline (see architecture note).

---

### 4.11 `vault-component.js` / `loader.js` / `sidebar.js` / `media-recorder.js` — ✅ WORKING
- `vault-component.js` loads on start-session, uploads, voice-analysis, facial-expression — modal (`deceptronVaultModal`, `vaultList`, `vaultSearch`) is created dynamically by JS (which is why the audit didn't find them as static HTML — they are generated at runtime, correctly).
- `loader.js` used by multiple pages; `sidebar.js` on every page; `media-recorder.js` on start-session/voice pages. All fine.

---

## 5. Suggested Fix Plan (in priority order — do NOT do these during the demo)

| # | Fix | Effort | Why |
|---|---|---|---|
| 1 | **Wire or hide `saveNotesBtn` in `report-detail.html`** | Small | Dead button visible to examiners |
| 2 | **Remove duplicate `mainVideoWrap`/`outputVideoSingle` blocks in `facial-expression.html`** | Small | Invalid HTML (duplicate IDs) |
| 3 | **Remove duplicate script loads in `start-session.html`** | Tiny | Sloppy, easy to fix |
| 4 | **Remove unused `frameOverlay` block in `start-session.html`** | Tiny | Placeholder text in DOM |
| 5 | **Delete or archive the 6 unused page-JS files** (`dashboard.js`, `facial-expression.js`, `profile.js`, `settings.js`, `start-session.js`, `uploads.js`) | Tiny | Dead code; avoid examiner confusion |
| 6 | Remove `recentAnalysisContainer` dead ID (dashboard) + `avatar-container` (profile) + `voiceWaveform` (report-detail) | Tiny | Cleanliness |
| 7 | Update `asymScoreLabel`/`oralScoreLabel` in facial-expression (or remove) | Small | Stuck default labels |
| 8 | **Regenerate or remove `Output of pipeline api.txt`** | Tiny | Old output shows reasoning that contradicts its own verdict ("VERDICT: DECEPTIVE" while score 47.5 < 50 and `is_deceptive:false`) — an honesty trap if read aloud |
| 9 | Move test videos into a `test_media/` folder | Tiny | Project tidiness |

---

## 6. Final Pre-Demo Checklist

- [ ] Run the full app start-to-finish the day before (backend → frontend → record → analyse).
- [ ] Record a REAL human test clip; verify NLP works (Groq key valid).
- [ ] Verify fusion breakdown bars + bilingual verdict render after a real run.
- [ ] Check that the report-detail "Save Notes" button is hidden or fixed.
- [ ] Have the 89.1% explanation open (`SYSTEM_ACCURACY_EXPLANATION.md`).
- [ ] Laptop charged; backup recording on disk; offline fallback plan ready.

---

*Prepared as a read-only analysis. No application code was modified in producing this guide.*
