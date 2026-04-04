import json
from collections import Counter
from datetime import datetime
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

    timestamps_by_minute = []

    for post in posts:
        dt = datetime.fromisoformat(post["created_at"].replace("Z", "+00:00"))
        minute_key = dt.strftime("%Y-%m-%d %H:%M")
        timestamps_by_minute.append(minute_key)

    minute_counts = Counter(timestamps_by_minute)
    max_posts_same_minute = max(minute_counts.values()) if minute_counts else 0

    return {
        "user_id": user_id,
        "num_posts": total_posts,
        "avg_text_length": round(mean(lengths), 2) if lengths else 0,
        "link_ratio": round(num_links / total_posts, 3) if total_posts else 0,
        "hashtag_ratio": round(num_hashtags / total_posts, 3) if total_posts else 0,
        "mention_ratio": round(num_mentions / total_posts, 3) if total_posts else 0,
        "unique_text_ratio": round(unique_texts / total_posts, 3) if total_posts else 0,
        "repeated_ratio": round(1 - (unique_texts / total_posts), 3) if total_posts else 0,
        "max_posts_same_minute": max_posts_same_minute,
    }


def is_obvious_human(
    features,
    human_link_posts,
    human_link_ratio,
    human_hashtag_max,
    low_volume_posts,
    low_volume_hashtag,
):
    human_links = (
        features["num_posts"] >= human_link_posts
        and features["link_ratio"] >= human_link_ratio
        and features["hashtag_ratio"] <= human_hashtag_max
    )

    human_low_volume_hashtag = (
        features["num_posts"] <= low_volume_posts
        and features["hashtag_ratio"] >= low_volume_hashtag
    )

    return human_links or human_low_volume_hashtag


def predict_bot(
    features,
    human_link_posts,
    human_link_ratio,
    human_hashtag_max,
    low_volume_posts,
    low_volume_hashtag,
    bot_hashtag_min,
    bot_hashtag_posts,
    bot_hashtag_mention_max,
    bot_link_posts,
    bot_link_min,
    bot_link_max,
    bot_link_hashtag_min,
    bot_link_mention_max,
    bot_burst_posts,
    bot_burst_minute_max,
    bot_burst_mention_max,
):
    if is_obvious_human(
        features,
        human_link_posts,
        human_link_ratio,
        human_hashtag_max,
        low_volume_posts,
        low_volume_hashtag,
    ):
        return False

    bot_hashtag = (
        features["hashtag_ratio"] >= bot_hashtag_min
        and features["num_posts"] >= bot_hashtag_posts
        and features["mention_ratio"] <= bot_hashtag_mention_max
    )

    bot_links = (
        features["num_posts"] >= bot_link_posts
        and bot_link_min <= features["link_ratio"] <= bot_link_max
        and features["hashtag_ratio"] >= bot_link_hashtag_min
        and features["mention_ratio"] <= bot_link_mention_max
    )

    bot_timeburst = (
        features["num_posts"] >= bot_burst_posts
        and features["max_posts_same_minute"] >= bot_burst_minute_max
        and features["mention_ratio"] <= bot_burst_mention_max
    )

    return bot_hashtag or bot_links or bot_timeburst


def compute_score(tp, fp, fn):
    return (2 * tp) - (6 * fp) - (2 * fn)


def prepare_dataset(dataset_number):
    dataset_path = f"data/dataset.posts&users.{dataset_number}.json"
    bots_path = f"data/dataset.bots.{dataset_number}.txt"

    data = load_dataset(dataset_path)
    bot_ids = load_bot_ids(bots_path)
    posts_by_user = group_posts_by_user(data["posts"])

    prepared_rows = []

    for user_id, posts in posts_by_user.items():
        features = extract_user_features(user_id, posts)
        features["is_bot"] = user_id in bot_ids
        prepared_rows.append(features)

    return prepared_rows


def evaluate_prepared_dataset(rows, params):
    tp = fp = fn = tn = 0

    for row in rows:
        predicted_bot = predict_bot(row, **params)

        if row["is_bot"] and predicted_bot:
            tp += 1
        elif not row["is_bot"] and predicted_bot:
            fp += 1
        elif row["is_bot"] and not predicted_bot:
            fn += 1
        else:
            tn += 1

    return {
        "tp": tp,
        "fp": fp,
        "fn": fn,
        "tn": tn,
        "score": compute_score(tp, fp, fn),
    }


def main():
    dataset_numbers = [2, 4, 6]

    print("Loading and preparing datasets once...")
    prepared_datasets = {
        dataset_number: prepare_dataset(dataset_number)
        for dataset_number in dataset_numbers
    }
    print("Datasets ready.\n")

    all_results = []

    for human_link_ratio in [0.80, 0.85]:
        for bot_hashtag_min in [0.75, 0.80]:
            for bot_hashtag_posts in [25, 30]:
                for bot_link_posts in [25, 30]:
                    for bot_link_min in [0.45, 0.50]:
                        for bot_link_hashtag_min in [0.03, 0.05]:
                            for bot_burst_posts in [15, 20, 25]:
                                for bot_burst_minute_max in [2, 3]:
                                    params = {
                                        "human_link_posts": 40,
                                        "human_link_ratio": human_link_ratio,
                                        "human_hashtag_max": 0.05,
                                        "low_volume_posts": 20,
                                        "low_volume_hashtag": 0.80,
                                        "bot_hashtag_min": bot_hashtag_min,
                                        "bot_hashtag_posts": bot_hashtag_posts,
                                        "bot_hashtag_mention_max": 0.10,
                                        "bot_link_posts": bot_link_posts,
                                        "bot_link_min": bot_link_min,
                                        "bot_link_max": 0.70,
                                        "bot_link_hashtag_min": bot_link_hashtag_min,
                                        "bot_link_mention_max": 0.10,
                                        "bot_burst_posts": bot_burst_posts,
                                        "bot_burst_minute_max": bot_burst_minute_max,
                                        "bot_burst_mention_max": 0.10,
                                    }

                                    dataset_results = []
                                    total_score = 0
                                    total_fp = 0

                                    for dataset_number in dataset_numbers:
                                        result = evaluate_prepared_dataset(
                                            prepared_datasets[dataset_number],
                                            params,
                                        )
                                        result["dataset"] = dataset_number
                                        dataset_results.append(result)
                                        total_score += result["score"]
                                        total_fp += result["fp"]

                                    avg_score = total_score / len(dataset_numbers)

                                    all_results.append({
                                        "params": params,
                                        "dataset_results": dataset_results,
                                        "total_score": total_score,
                                        "avg_score": avg_score,
                                        "total_fp": total_fp,
                                    })

    all_results.sort(
        key=lambda x: (x["total_score"], -x["total_fp"]),
        reverse=True
    )

    print("TOP 5 CONFIGURATIONS\n")

    for i, result in enumerate(all_results[:5], start=1):
        print(f"=== CONFIG {i} ===")
        print("params:", result["params"])
        print("total_score:", result["total_score"])
        print("avg_score:", round(result["avg_score"], 2))
        print("total_fp:", result["total_fp"])

        for r in result["dataset_results"]:
            print(
                f"dataset {r['dataset']} -> "
                f"TP={r['tp']} FP={r['fp']} FN={r['fn']} TN={r['tn']} score={r['score']}"
            )
        print()


if __name__ == "__main__":
    main()