import json

def load_dataset(path):
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data

def main():
    print("Loading dataset...")

    data = load_dataset("data/dataset.posts&users.30.json")

    print("Dataset loaded!")

    print("\nKeys in dataset:")
    print(data.keys())

    print("\nNumber of posts:")
    print(len(data["posts"]))

    print("\nExample post:")
    print(data["posts"][0])

    print("\nNumber of users:")
    print(len(data["users"]))

    print("\nGrouping posts by user...")

    posts_by_user = {}

    for post in data["posts"]:
        user_id = post["author_id"]

        if user_id not in posts_by_user:
            posts_by_user[user_id] = []

        posts_by_user[user_id].append(post)

    print("Done grouping!")

    print("\nNumber of users in grouping:")
    print(len(posts_by_user))

    # exemple user ID and number of posts for that user
    some_user = list(posts_by_user.keys())[0]
    print("\nExample user ID:")
    print(some_user)

    print("Number of posts for this user:")
    print(len(posts_by_user[some_user]))

if __name__ == "__main__":
    main()