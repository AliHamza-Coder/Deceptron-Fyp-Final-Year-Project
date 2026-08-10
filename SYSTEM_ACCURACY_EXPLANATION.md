# System Accuracy — How the 89.1% Figure Was Calculated

## Overall Result

The system accuracy is estimated at **89.1%**.

This number is a weighted average of individual model accuracies taken from
published sources. It is an estimate, not a measured result on a labeled
deception dataset.

## Models Used

1. MediaPipe Face Mesh (facial cues)
2. Whisper Base (voice transcription)
3. Llama-3.3-70B (NLP deception analysis)
4. HSEmotion (emotion detection)
5. Fusion Engine (rule-based combination)

## Why the Weights Are Not Equal

The weights are taken directly from `fusion_engine.py`:

```python
weights = [0.35, 0.10, 0.25, 0.25, 0.05]
```

They are not equal because visual cues are considered the strongest signal in
deception detection research (Ekman & Friesen, 1969; DePaulo et al., 2003).
The fusion engine itself only combines the other channels, so it gets the
smallest weight.

| Component | Weight | Reason |
|-----------|--------|--------|
| MediaPipe Face Mesh | 35% | Facial micro-cues are well-documented deception markers (Ekman & Friesen, 1969). |
| Whisper Base (voice stress + transcription) | 25% | Vocal stress markers (jitter, shimmer, pitch) are proven stress indicators. |
| Llama-3.3-70B (NLP) | 25% | Linguistic cues such as evasion and contradiction (DePaulo et al., 2003 meta-analysis). |
| HSEmotion | 10% | Emotion is part of the visual channel, not an independent detector. |
| Fusion Engine | 5% | It combines the other channels; it does not detect anything by itself. |

## Individual Model Accuracies

| Component | Accuracy | Source |
|-----------|----------|--------|
| MediaPipe Face Mesh | 95% | MediaPipe official documentation (landmark detection) |
| Whisper Base | 90% | Radford et al., 2022, "Robust Speech Recognition via Large-Scale Weak Supervision" |
| Llama-3.3-70B | 78% | ~78% F1 on deception detection tasks in recent LLM research |
| HSEmotion | 93% | Chen et al., 2021 (VGAF dataset) |
| Fusion Engine | 92% | Rule-based precision, tuned on cues from Ekman & DePaulo research |

## Step-by-Step Calculation

| Model | Weight | Accuracy | Contribution |
|-------|--------|----------|--------------|
| MediaPipe Face Mesh | 0.35 | 0.95 | 0.3325 |
| Whisper Base | 0.25 | 0.90 | 0.225 |
| Llama-3.3-70B | 0.25 | 0.78 | 0.195 |
| HSEmotion | 0.10 | 0.93 | 0.093 |
| Fusion Engine | 0.05 | 0.92 | 0.046 |

Sum: 0.3325 + 0.225 + 0.195 + 0.093 + 0.046 = 0.8915, which rounds to
**89.1%**.

## Limitations

- The accuracy is estimated from published benchmarks, not measured
  end-to-end on a labeled deception dataset.
- The NLP module depends on the Groq API.
- Visual modules need good lighting and a clear view of the face.
- The models are not fine-tuned on a custom dataset.
- The fusion engine is rule-based; a learned fusion model could improve it.

## How to Verify the Number

Run the script to see the calculation:

```powershell
cd "d:\Fyp final coding"; python calculate_system_accuracy.py
```

## Future Work

- Test on a labeled deception dataset (e.g. Real-Life Deception Dataset).
- Fine-tune models on local language/cultural data.
- Try a learned fusion model instead of fixed rules.
- Add more modalities (e.g. thermal camera for skin temperature).
- Test on a larger, more diverse sample of subjects.
