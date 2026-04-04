
# AppleCrumble - Bot or Not

## Team
AppleCrumble

## Overview

This project implements a rule-based system to detect automated accounts (bots) on social media using user-level features extracted from their posts.

The model is designed to minimize false positives due to the competition scoring rule.

---

## How the model works

The system processes the data in three steps:

### 1. Group posts by user

All posts are grouped by `author_id` so each user is analyzed based on their full activity.

### 2. Feature extraction

For each user, the following features are computed:

- num_posts: number of posts  
- avg_text_length: average post length  
- link_ratio: proportion of posts containing links (`https://t.co/`)  
- hashtag_ratio: proportion of posts containing hashtags (`#`)  
- mention_ratio: proportion of posts containing mentions (`@mention`)  
- unique_text_ratio: proportion of unique posts  
- repeated_ratio: proportion of repeated posts  

These features capture user behavior and interaction patterns.

### 3. Bot detection rules

The model uses rule-based heuristics.

#### French model (predict_bot)

In the French datasets, bots tend to:

- use many hashtags  
- have structured posting behavior  
- show low interaction  

The model detects bots using:

- high hashtag ratio with sufficient activity  
- link usage combined with low mentions  
- filtering of obvious human profiles  

#### English model (predict_bot_en)

In the English datasets:

- hashtags are less informative  
- many human users share links  
- interaction (mentions) is more relevant  

The English model is more conservative and detects only clear bots using:

- extreme hashtag usage  
- specific link patterns with very low interaction  
- protection of human-like accounts  

---

## Evaluation

The model is evaluated using the competition metric:

score = (2 × TP) − (6 × FP) − (2 × FN)

False positives are heavily penalized, so the model prioritizes precision.

---

## How to run the model

### French

In main.py, set:

```python
for dataset_number in [2, 4, 6]:
    result = evaluate_dataset(dataset_number, predict_bot)
```

Run:

```
python main.py
```

### English

In main.py, set:

```python
for dataset_number in [1, 3, 5]:
    result = evaluate_dataset(dataset_number, predict_bot_en)
```

Run:

```
python main.py
```

---

## Generating submission files

The function `write_detection_file(dataset_path, predictor, output_path)` generates the required output files.

Each file contains:
- one user ID per line  
- no additional formatting  

### Example

```python
write_detection_file(
    dataset_path="data/final_fr.json",
    predictor=predict_bot,
    output_path="applecrumble.detections.fr.txt",
)

write_detection_file(
    dataset_path="data/final_en.json",
    predictor=predict_bot_en,
    output_path="applecrumble.detections.en.txt",
)
```

---

## Final submission

Submit:

- applecrumble.detections.fr.txt  
- applecrumble.detections.en.txt  
- link to this repository  

---

## Notes

- Separate models are used for French and English  
- The approach is rule-based  
- The model is optimized to reduce false positives  