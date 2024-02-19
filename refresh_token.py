"""Helpers to fresh stale GitHub secrets."""
import os
from base64 import b64encode
from pathlib import Path
from typing import Any, Dict

import requests
from nacl import encoding
from nacl.public import PublicKey, SealedBox
from requests import Response

github_user = "alexlaverty"
github_repo = "ttsvibelounge"
github_token = os.getenv("GH_TOKEN")
secret_name = "CREDENTIALS_STORAGE"  # noqa: S105
api_endpoint = f"https://api.github.com/repos/{github_user}/{github_repo}"


def get_repo_key() -> Dict:
    """Get the key to a GitHub repository.

    Returns:
        The GitHub repository key.
    """
    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "Authorization": f"Bearer {github_token}",
    }
    return requests.get(
        f"{api_endpoint}/actions/secrets/public-key", headers=headers, timeout=120
    ).json()


def encrypt(public_key: str, secret_value: str) -> str:
    """Encrypt a Unicode string using the public key.

    Args:
        public_key: Public encryption key.
        secret_value: Secret to be encrypted.

    Returns:
        Returns the base64 encoded, encrypted secret.
    """
    public_key: PublicKey = PublicKey(
        public_key.encode("utf-8"), encoding.Base64Encoder()
    )
    sealed_box: SealedBox = SealedBox(public_key)
    encrypted: Any = sealed_box.encrypt(secret_value.encode("utf-8"))
    return b64encode(encrypted).decode("utf-8")


def write_secret(repo_key: Any, secret_encrypted_string: str) -> None:
    """Add a secret to GitHub.

    Args:
        repo_key: Name of the repository that should contain the secret.
        secret_encrypted_string: Secret value.
    """
    url: str = f"https://api.github.com/repos/{github_user}/{github_repo}/actions/secrets/{secret_name}"
    headers: Dict[str, str] = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "Authorization": f"Bearer {github_token}",
    }
    data: Dict[str, str] = {
        "encrypted_value": secret_encrypted_string,
        "key_id": repo_key["key_id"],
    }
    print("---------------------------------")
    print(url)
    print(headers)
    print(data)
    print("---------------------------------")
    x: Response = requests.put(url, json=data, headers=headers, timeout=120)
    print(x.text)


def get_file_contents(filename: Path) -> str:
    """Read the contents of a text file.

    Args:
        filename: Path to the file to read.

    Returns:
        The file contents.
    """
    with open(filename, "r") as f:
        return f.read()


file_contents: str = get_file_contents("credentials.storage")

repo_key: Any = get_repo_key()
print(repo_key)

encrypted_secret: str = encrypt(repo_key["key"], file_contents)
write_secret(repo_key, encrypted_secret)
