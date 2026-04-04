import json
from statistics import mean


def load_dataset(path):
    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)


def load_bot_ids(path):
    with open(path, "r", encoding="utf-8") as file:
        return {line.strip() for line in file if line.strip()}


def group_posts_by_user(posts):
    posts_by_user = {}

    for post in posts:
        user_id = post["author_id"]
        if user_id not in posts_by_user:
            posts_by_user[user_id] = []
        posts_by_user[user_id].append(post)

    return posts_by_user


def extract_user_features(user_id, posts):
    texts = [post["text"] for post in posts]
    lengths = [len(text) for text in texts]

    num_links = sum("https://t.co/" in text for text in texts)
    num_hashtags = sum("#" in text for text in texts)
    num_mentions = sum("@mention" in text for text in texts)

    unique_texts = len(set(texts))
    total_posts = len(texts)

    return {
        "user_id": user_id,
        "num_posts": total_posts,
        "avg_text_length": round(mean(lengths), 2) if lengths else 0,
        "link_ratio": round(num_links / total_posts, 3) if total_posts else 0,
        "hashtag_ratio": round(num_hashtags / total_posts, 3) if total_posts else 0,
        "mention_ratio": round(num_mentions / total_posts, 3) if total_posts else 0,
        "unique_text_ratio": round(unique_texts / total_posts, 3) if total_posts else 0,
        "repeated_ratio": round(1 - (unique_texts / total_posts), 3) if total_posts else 0,
    }


def is_obvious_human(features):
    human_links = (
        features["num_posts"] >= 40
        and features["link_ratio"] >= 0.8
        and features["hashtag_ratio"] <= 0.05
    )

    human_low_volume_hashtag = (
        features["num_posts"] <= 20
        and features["hashtag_ratio"] >= 0.8
    )

    return human_links or human_low_volume_hashtag


def predict_bot(features):
    if is_obvious_human(features):
        return False

    bot_hashtag = (
        features["hashtag_ratio"] >= 0.75
        and features["num_posts"] >= 30
        and features["mention_ratio"] <= 0.1
    )

    bot_links = (
        features["num_posts"] >= 30
        and 0.50 <= features["link_ratio"] <= 0.70
        and features["hashtag_ratio"] >= 0.05
        and features["mention_ratio"] <= 0.1
    )

    return bot_hashtag or bot_links


def predict_bot_en(features):
    if (
        features["mention_ratio"] >= 0.15
        or (
            features["num_posts"] >= 40
            and features["link_ratio"] >= 0.80
            and features["hashtag_ratio"] <= 0.02
        )
    ):
        return False

    bot_hashtag = (
        features["hashtag_ratio"] >= 0.90
        and features["num_posts"] >= 20
        and features["mention_ratio"] <= 0.10
    )

    bot_links = (
        features["num_posts"] >= 40
        and 0.50 <= features["link_ratio"] <= 0.65
        and features["mention_ratio"] <= 0.03
        and features["hashtag_ratio"] >= 0.02
    )

    return bot_hashtag or bot_links

def write_detection_file(dataset_path, predictor, output_path):
    data = load_dataset(dataset_path)
    posts_by_user = group_posts_by_user(data["posts"])

    predicted_bot_ids = []

    for user_id, posts in posts_by_user.items():
        features = extract_user_features(user_id, posts)

        if predictor(features):
            predicted_bot_ids.append(user_id)

    predicted_bot_ids.sort()

    with open(output_path, "w", encoding="utf-8") as file:
        for user_id in predicted_bot_ids:
            file.write(f"{user_id}\n")

    print(f"File created: {output_path}")


def compute_score(tp, fp, fn):
    return (2 * tp) - (6 * fp) - (2 * fn)


def evaluate_dataset(dataset_number, predictor):
    dataset_path = f"data/dataset.posts&users.{dataset_number}.json"
    bots_path = f"data/dataset.bots.{dataset_number}.txt"

    data = load_dataset(dataset_path)
    bot_ids = load_bot_ids(bots_path)
    posts_by_user = group_posts_by_user(data["posts"])

    tp = fp = fn = tn = 0

    for user_id, posts in posts_by_user.items():
        features = extract_user_features(user_id, posts)
        is_bot = user_id in bot_ids
        predicted_bot = predictor(features)

        if is_bot and predicted_bot:
            tp += 1
        elif not is_bot and predicted_bot:
            fp += 1
        elif is_bot and not predicted_bot:
            fn += 1
        else:
            tn += 1

    score = compute_score(tp, fp, fn)

    return {
        "dataset": dataset_number,
        "tp": tp,
        "fp": fp,
        "fn": fn,
        "tn": tn,
        "score": score,
    }


def main():
    for dataset_number in [1, 3, 5]:
        result = evaluate_dataset(dataset_number, predict_bot_en)

        print("\n==============================")
        print(f"DATASET {result['dataset']}")
        print("==============================")
        print(f"TP: {result['tp']}")
        print(f"FP: {result['fp']}")
        print(f"FN: {result['fn']}")
        print(f"TN: {result['tn']}")
        print(f"Score: {result['score']}")


if __name__ == "__main__":
    main()