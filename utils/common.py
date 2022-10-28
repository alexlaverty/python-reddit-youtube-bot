import random
import re
import os


def random_hex_colour():
    r = lambda: random.randint(0, 255)
    rcolor = "#%02X%02X%02X" % (r(), r(), r())
    return rcolor


def random_rgb_colour():
    rbg_colour = random.choices(range(256), k=3)
    print("Generated random rgb colour")
    print(rbg_colour)
    return rbg_colour


def give_emoji_free_text(data):
    emoj = re.compile(
        "["
        "\U0001F600-\U0001F64F"  # emoticons
        "\U0001F300-\U0001F5FF"  # symbols & pictographs
        "\U0001F680-\U0001F6FF"  # transport & map symbols
        "\U0001F1E0-\U0001F1FF"  # flags (iOS)
        "\U00002500-\U00002BEF"  # chinese char
        "\U00002702-\U000027B0"
        "\U00002702-\U000027B0"
        "\U000024C2-\U0001F251"
        "\U0001f926-\U0001f937"
        "\U00010000-\U0010ffff"
        "\u2640-\u2642"
        "\u2600-\u2B55"
        "\u200d"
        "\u23cf"
        "\u23e9"
        "\u231a"
        "\ufe0f"  # dingbats
        "\u3030"
        "]+",
        re.UNICODE,
    )
    return re.sub(emoj, "", data)


def safe_filename(text):
    text = text.replace(" ", "_")
    return "".join([c for c in text if re.match(r"\w", c)])[:50]


def create_directory(folder_path):
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)


def contains_url(text):
    matches = ["http://", "https://"]
    if any(x in text for x in matches):
        return True
