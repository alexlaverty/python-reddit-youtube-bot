"""Base64 encoding utilities."""
import base64


def base64_encode_string(message: str) -> None:
    """Encode a string to base64.

    Args:
        message: The string to be encoded.
    """
    # TODO: What is my purpose?
    message_bytes = message.encode("ascii")
    base64_bytes = base64.b64encode(message_bytes)
    base64_message = base64_bytes.decode("ascii")
    print(base64_message)


def base64_decode_string(message: str) -> str:
    """Decode a base64 encoded string to ASCII format.

    Args:
        message: The base64 string to be decoded.

    Returns:
        The decoded ASCII string.
    """
    return base64.b64decode(message.encode("ascii")).decode("ascii")


# Ignored keywords Testing the encoding function?
message = "porn,sex,jerking off,slut,rape"
base64_encode_string(message)

# Encoded keywords. Testing the decoding function?
message = "cG9ybixzZXgsamVya2luZyBvZmYsc2x1dCxyYXBl"
decoded_string = base64_decode_string(message)
print(decoded_string)
print(decoded_string.split(","))
