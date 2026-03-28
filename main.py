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

if __name__ == "__main__":
    main()