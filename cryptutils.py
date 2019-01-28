from Crypto.Cipher import AES
import base64
import os
import constants

key = os.environ.get(constants.KEY_NAME_VAR)
key32 = "{: <32}".format(key).encode("utf-8")
cipher = AES.new(key32, AES.MODE_ECB)


def encodestr(message: str):
    to_encode = message.rjust(32)
    return base64.b64encode(cipher.encrypt(to_encode))


def decodestr(message: str):
    return cipher.decrypt(base64.b64decode(message))
