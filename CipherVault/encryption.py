#  Copyright (c) 2023 Harikeshav R
#  All rights reserved.

import base64
import hashlib

import bcrypt
from Crypto import Random
from Crypto.Cipher import AES


class MasterEncryption:
    def __init__(self, master_password):
        self.master_password = master_password

    def get_hashed_password(self):
        return bcrypt.hashpw(self.master_password, bcrypt.gensalt())

    def check_password(self, hashed_password):
        return bcrypt.checkpw(self.master_password, hashed_password)


class CredentialEncryption:
    def __init__(self, key):
        self.key = hashlib.sha256(key.encode()).digest()

    def encrypt(self, raw):
        raw = self._pad(raw)
        iv = Random.new().read(AES.block_size)
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return base64.b64encode(iv + cipher.encrypt(raw.encode()))

    def decrypt(self, enc):
        enc = base64.b64decode(enc)
        iv = enc[:AES.block_size]
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return self._unpad(cipher.decrypt(enc[AES.block_size:])).decode('utf-8')

    @staticmethod
    def _pad(s):
        return s + (AES.block_size - len(s) % AES.block_size) * chr(AES.block_size - len(s) % AES.block_size)

    @staticmethod
    def _unpad(s):
        return s[:-ord(s[len(s) - 1:])]
