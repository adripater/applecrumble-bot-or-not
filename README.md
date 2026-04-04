# 🍏 AppleCrumble - Bot or Not 2026

## 📌 Overview

This project implements a **rule-based bot detection system** for the Bot or Not 2026 competition.

The goal is to classify users as bots or humans based on their posting behavior.
The approach prioritizes **minimizing false positives**, as required by the competition scoring:

```
score = (2 × TP) − (6 × FP) − (2 × FN)
```

---

## 🧠 Approach

The system analyzes users by aggregating their posts and extracting behavioral features.

### Extracted Features

* `num_posts` — total number of posts per user
* `avg_text_length` — average length of posts
* `link_ratio` — proportion of posts containing links
* `hashtag_ratio` — proportion of posts containing hashtags
* `mention_ratio` — proportion of posts containing mentions
* `unique_text_ratio` — diversity of text
* `repeated_ratio` — repetition of content

---

## 🌍 Language-Specific Models

Two separate predictors are used:

### 🇫🇷 French Model — `predict_bot`

Designed to capture:

* hashtag-heavy accounts
* structured / repetitive content
* moderate link usage

### 🇬🇧 English Model — `predict_bot_en`

More conservative to avoid false positives:

* protects conversational users (mentions)
* protects high-link, low-hashtag accounts
* detects only strong bot patterns

👉 This separation improves robustness since posting behavior differs between languages.

---

## 📂 Project Structure

```
applecrumble-bot-or-not/
│
├── data/
│   ├── dataset.posts&users.X.json
│   ├── dataset.bots.X.txt (training only)
│
├── main.py
├── README.md
```

---

## 🚀 How to Run (Final Submission)

### 1. Place datasets

Put the final datasets inside the `data/` folder:

```
data/dataset.posts&users.7.json   # English
data/dataset.posts&users.8.json   # French
```

---

### 2. Run the script

```
python main.py
```

---

### 3. Output

Two files will be generated:

```
applecrumble.detections.en.txt
applecrumble.detections.fr.txt
```

Each file contains:

* one `user_id` per line
* no headers
* no extra formatting

---

## 🧪 Evaluation (Optional)

To evaluate on training datasets:

```python
evaluate_dataset(dataset_number, predictor)
```

Example:

```python
evaluate_dataset(1, predict_bot_en)
```

---

## ⚙️ Design Choices

* Rule-based approach for full control over predictions
* Conservative thresholds to reduce false positives
* Separate models for French and English datasets
* Robust data handling (`.get()`, regex detection)

---

## 🔮 Possible Improvements

Future work could include:

* counting exact number of hashtags and mentions per post
* detecting repeated templates or structured content
* analyzing variability of text length
* incorporating lightweight ML models (e.g., decision trees)
* improving detection of hybrid or semi-automated accounts

---

## 🙌 Final Notes

This project was developed as part of the Bot or Not 2026 competition.

The experience was both challenging and rewarding, especially in balancing detection performance with strict constraints on false positives.

I would be very interested in continuing to improve this approach and further exploring bot detection techniques in future iterations.

Thank you for the opportunity - this was a great experience 🚀
