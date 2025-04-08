import hashlib
import base64
from datetime import datetime

from Crypto.Cipher import AES
from Crypto.Util.Padding import pad


class PswUtil:
    @staticmethod
    def sha256(input_string):
        sha256_hash = hashlib.sha256()
        sha256_hash.update(input_string.encode('utf-8'))
        return sha256_hash.hexdigest()

    @staticmethod
    def encode_pwd(username, password, salt, challenge, iterate):
        i = PswUtil.sha256(username + salt + password)
        i = PswUtil.sha256(i + challenge)
        for _ in range(2, iterate):
            i = PswUtil.sha256(i)
        return i

    @staticmethod
    def encode_string(input_str):
        if input_str is None:
            return ""
        return (input_str.replace("&", "&amp;")
                .replace("<", "&lt;")
                .replace(">", "&gt;"))

    @staticmethod
    def get_n(text):
        return base64.b64encode(PswUtil.encode_string(text).encode()).decode()

    @staticmethod
    def get_iv():
        return hashlib.md5(str(datetime.now().timestamp()).encode()).hexdigest()

    @staticmethod
    def get_aes_key(password, username, salt, key_iterate_num):
        if key_iterate_num <= 0:
            return ""

        irreversible_key = PswUtil.get_irreversible_key(password, username, salt) + "AaBbCcDd1234!@#$"
        n = PswUtil.sha256(irreversible_key)

        for _ in range(1, key_iterate_num):
            n = PswUtil.sha256(n)

        return n[:32] if n else ""

    @staticmethod
    def get_irreversible_key(password, username, salt):
        return PswUtil.sha256(username + salt + password)


class AESUtil:
    @staticmethod
    def encode_aes(plain_text, key_hex, iv_hex):
        try:
            key = bytes.fromhex(key_hex)
            iv = bytes.fromhex(iv_hex)

            cipher = AES.new(key, AES.MODE_CBC, iv)
            padded_data = pad(plain_text.encode(), AES.block_size)
            encrypted = cipher.encrypt(padded_data)

            return encrypted.hex()
        except Exception as e:
            print(f"Error in encode_aes: {e}")
            return None

    @staticmethod
    def hex_string_to_bytes(hex_string):
        return bytes.fromhex(hex_string)


if __name__ == "__main__":
    try:
        plain_text = "YWRtaW4="
        key_hex = "525bc266cd0c42adafc2927f016d75e4"
        iv_hex = "476ddbc7757f49125eb536310d6a25f1"

        encrypted_text = AESUtil.encode_aes(plain_text, key_hex, iv_hex)
        print(f"Encrypted Text: {encrypted_text}")
    except Exception as e:
        print(f"Error: {e}")
