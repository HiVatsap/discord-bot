def load_words():
    try:
        with open('words.txt', 'r', encoding="utf-8") as f:
            return [line.strip().lower() for line in f if line.strip()]
    except FileNotFoundError:
        return ["привет", "hi", "hello", "привіт", "ahoj", "labas"]

def save_words(variants):
    with open('words.txt', 'w', encoding="utf-8") as f:
        for word in variants:
            f.write(f"{word}\n")

hello_variants = load_words()