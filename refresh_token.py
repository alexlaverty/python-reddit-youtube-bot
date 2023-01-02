import requests
import os
from base64 import b64encode
from nacl import encoding, public

github_user = "alexlaverty"
github_repo = "ttsvibelounge"
github_token = os.getenv('GH_TOKEN')
secret_name = "CREDENTIALS_STORAGE"
api_endpoint = f"https://api.github.com/repos/{github_user}/{github_repo}"


def get_repo_key():
    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "Authorization": f"Bearer {github_token}"
    }
    return requests.get(f"{api_endpoint}/actions/secrets/public-key",
                        headers=headers).json()


def encrypt(public_key: str, secret_value: str) -> str:
    """Encrypt a Unicode string using the public key."""
    public_key = public.PublicKey(public_key.encode("utf-8"), encoding.Base64Encoder())
    sealed_box = public.SealedBox(public_key)
    encrypted = sealed_box.encrypt(secret_value.encode("utf-8"))
    return b64encode(encrypted).decode("utf-8")


def write_secret(repo_key, secret_encrypted_string):
    url = f"https://api.github.com/repos/{github_user}/{github_repo}/actions/secrets/{secret_name}"
    headers = {
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "Authorization": f"Bearer {github_token}"
        }
    data = {
            "encrypted_value": secret_encrypted_string,
            "key_id": repo_key["key_id"]
        }
    print("---------------------------------")
    print(url)
    print(headers)
    print(data)
    print("---------------------------------")
    x = requests.put(url,
                     json=data,
                     headers=headers)
    print(x.text)


def get_file_contents(filename):
    f = open(filename, "r")
    return f.read()


file_contents = get_file_contents("credentials.storage")

repo_key = get_repo_key()

print(repo_key)

encrypted_secret = encrypt(repo_key["key"], file_contents)

write_secret(repo_key, encrypted_secret)
