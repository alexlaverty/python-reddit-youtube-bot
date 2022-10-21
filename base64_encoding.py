import base64

def base64_encode_string(message):
    message_bytes = message.encode('ascii')
    base64_bytes = base64.b64encode(message_bytes)
    base64_message = base64_bytes.decode('ascii')
    print(base64_message)

def base64_decode_string(message):
    message_decoded = base64.b64decode(message.encode('ascii')).decode('ascii').split(",")
    print(message_decoded)


message = "Hello World"
base64_encode_string(message)

message = "SGVsbG8gV29ybGQ="
base64_decode_string(message)
