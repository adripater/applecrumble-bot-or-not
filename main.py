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
        "avg_text_length": mean(lengths) if lengths else 0,
        "link_ratio": num_links / total_posts if total_posts else 0,
        "hashtag_ratio": num_hashtags / total_posts if total_posts else 0,
        "mention_ratio": num_mentions / total_posts if total_posts else 0,
        "unique_text_ratio": unique_texts / total_posts if total_posts else 0,
        "repeated_ratio": 1 - (unique_texts / total_posts) if total_posts else 0,
    }


def main():
    dataset_path = "data/dataset.posts&users.2.json"
    bots_path = "data/dataset.bots.2.txt"

    print("Loading dataset...")
    data = load_dataset(dataset_path)
    bot_ids = load_bot_ids(bots_path)
    print("Dataset loaded!")

    print("\nDataset language:")
    print(data["lang"])

    print("\nNumber of posts:")
    print(len(data["posts"]))

    print("\nNumber of users:")
    print(len(data["users"]))

    posts_by_user = group_posts_by_user(data["posts"])

    print("\nNumber of grouped users:")
    print(len(posts_by_user))

    user_features = []

    for user_id, posts in posts_by_user.items():
        features = extract_user_features(user_id, posts)
        features["is_bot"] = user_id in bot_ids
        user_features.append(features)

    bots = [row for row in user_features if row["is_bot"]]
    humans = [row for row in user_features if not row["is_bot"]]

    print("\nBots in dataset:")
    print(len(bots))

    print("\nHumans in dataset:")
    print(len(humans))

    if bots:
        print("\nAverage bot stats:")
        print("avg num_posts:", round(mean(row["num_posts"] for row in bots), 2))
        print("avg text length:", round(mean(row["avg_text_length"] for row in bots), 2))
        print("avg link ratio:", round(mean(row["link_ratio"] for row in bots), 2))
        print("avg hashtag ratio:", round(mean(row["hashtag_ratio"] for row in bots), 2))
        print("avg repeated ratio:", round(mean(row["repeated_ratio"] for row in bots), 2))

    if humans:
        print("\nAverage human stats:")
        print("avg num_posts:", round(mean(row["num_posts"] for row in humans), 2))
        print("avg text length:", round(mean(row["avg_text_length"] for row in humans), 2))
        print("avg link ratio:", round(mean(row["link_ratio"] for row in humans), 2))
        print("avg hashtag ratio:", round(mean(row["hashtag_ratio"] for row in humans), 2))
        print("avg repeated ratio:", round(mean(row["repeated_ratio"] for row in humans), 2))

    print("\nExample rows:")
    for row in user_features[:5]:
        print(row)


if __name__ == "__main__":
    main()