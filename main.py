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


def predict_bot(features):
    rule_hashtag = (
        features["hashtag_ratio"] >= 0.75
        and features["num_posts"] >= 20
    )

    rule_links = (
        features["num_posts"] >= 30
        and 0.50 <= features["link_ratio"] <= 0.75
        and (
            features["hashtag_ratio"] >= 0.08
            or features["mention_ratio"] >= 0.04
        )
    )

    rule_medium = (
        features["num_posts"] >= 30   # antes 20
        and features["hashtag_ratio"] >= 0.4
        and features["link_ratio"] <= 0.7
    )

    return rule_hashtag or rule_links or rule_medium


def compute_competition_score(tp, fp, fn):
    return (2 * tp) - (6 * fp) - (2 * fn)


def main():
    dataset_path = "data/dataset.posts&users.2.json"
    bots_path = "data/dataset.bots.2.txt"

    print("Loading dataset...")
    data = load_dataset(dataset_path)
    bot_ids = load_bot_ids(bots_path)
    print("Dataset loaded!")

    posts_by_user = group_posts_by_user(data["posts"])
    user_features = []

    for user_id, posts in posts_by_user.items():
        features = extract_user_features(user_id, posts)
        features["is_bot"] = user_id in bot_ids
        features["predicted_bot"] = predict_bot(features)
        user_features.append(features)

    tp = 0
    fp = 0
    fn = 0
    tn = 0

    detected_bots = []
    missed_bots = []
    false_positives = []

    for row in user_features:
        if row["is_bot"] and row["predicted_bot"]:
            tp += 1
            detected_bots.append(row)
        elif not row["is_bot"] and row["predicted_bot"]:
            fp += 1
            false_positives.append(row)
        elif row["is_bot"] and not row["predicted_bot"]:
            fn += 1
            missed_bots.append(row)
        else:
            tn += 1

    score = compute_competition_score(tp, fp, fn)

    print("\nResults with current rule:")
    print("TP:", tp)
    print("FP:", fp)
    print("FN:", fn)
    print("TN:", tn)
    print("Competition score:", score)

    print("\nDetected bots:")
    for row in detected_bots[:10]:
        print(row)

    print("\nMissed bots:")
    for row in missed_bots[:15]:
        print(row)

    print("\nFalse positives:")
    for row in false_positives[:10]:
        print(row)


if __name__ == "__main__":
    main()