"""Common helpers to keep the codebase DRY."""
from random import SystemRandom
import re
import os
from pathlib import Path


def random_hex_colour() -> str:
    """Generate a random hex value that represents a colour.

    Returns:
        A HTML colour expressed in hex format, for example - 0F37A1.
    """
    rnd: SystemRandom = SystemRandom()
    r = rnd.randint(0, 255)
    rcolor = "#%02X%02X%02X" % (r(), r(), r())
    return rcolor


def random_rgb_colour() -> int:
    """Generate a random integer between 0 and 255.

    Returns:
        A random integer.
    """
    rnd: SystemRandom = SystemRandom()
    rbg_colour: int = rnd.choices(range(256), k=3)
    print("Generated random rgb colour")
    print(rbg_colour)
    return rbg_colour


def give_emoji_free_text(data: str) -> str:
    """Strip special characters from a string.

    This function will santize strings by removing emoticons, symbols and
    chinese characters.

    Args:
        data: The raw string to be processed.

    Returns:
        A santized string with special characters removed.
    """
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


def safe_filename(text: str) -> str:
    """Replace all spaces in a string with an underscore.

    Args:
        text: string to be processed.

    Returns:
        The processed string, with all spaces converted to underscores.
    """
    text = text.replace(" ", "_")
    return "".join([c for c in text if re.match(r"\w", c)])[:50]


def create_directory(folder_path: Path) -> None:
    """Create a directory path on the filesystem.

    Args:
        folder_path: Path to be created.
    """
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)


def contains_url(text: str) -> bool:
    """Validate if a string is a valid URL.

    This just does a simple protocol check. If the string starts with http://
    or https://, it's assumed to be a valid URL.

    Args:
        text: string to be evaluated.

    Returns:
        `True` if the string is a URL, otherwise `False`.
    """
    matches = ["http://", "https://"]
    if any(x in text for x in matches):
        return True


def sanitize_text(text: str) -> str:
    r"""Sanitize the text for tts.

    What gets removed:
        - following characters `^_~@!&;#:-%“”‘"%*/{}[]()\|<>?=+`
        - any http or https links

    Args:
        text: Text to be sanitized

    Returns:
        str: Sanitized text
    """
    # Remove age related info
    # fmt: off
    text: str = re.sub(
        r"(\[|\()[0-9]{1,2}\s*(m|f)?(\)|\])",
        "",
        text,
        flags=re.IGNORECASE
    )

    # remove any urls from the text
    regex_urls: str = (
        r"((http|https)\:\/\/)"
        r"?[a-zA-Z0-9\.\/\?\:@\-_=#]"
        r"+\."
        r"([a-zA-Z]){2,6}"
        r"([a-zA-Z0-9\.\&\/\?\:@\-_=#])"
        r"*"
    )

    result: str = re.sub(regex_urls, " ", text)

    # note: not removing apostrophes
    regex_expr: str = r"\s['|’]|['|’]\s|[\^_~@!&;#:\-–—%“”‘\"%\*/{}\[\]\(\)\\|<>=+]"
    result: str = re.sub(regex_expr, " ", result)
    result = result.replace("+", "plus").replace("&", "and")

    # remove extra whitespace
    # return " ".join(result.split())
    return result
