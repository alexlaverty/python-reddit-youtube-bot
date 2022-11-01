import base64

def base64_encode_string(message):
    message_bytes = message.encode('ascii')
    base64_bytes = base64.b64encode(message_bytes)
    base64_message = base64_bytes.decode('ascii')
    print(base64_message)

def base64_decode_string(message):
    return base64.b64decode(message.encode('ascii')).decode('ascii')



message = "porn,sex,jerking off,slut,rape"
base64_encode_string(message)

message = "cG9ybixzZXgsamVya2luZyBvZmYsc2x1dCxyYXBl"
decoded_string = base64_decode_string(message)
print(decoded_string)
print(decoded_string.split(","))
