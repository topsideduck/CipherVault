#  Copyright (c) 2023 Harikeshav R
#  All rights reserved.

import random
import string

import yagmail


class OTP:
    def __init__(self):
        self.otp: int
        self.server = yagmail.SMTP("ciphervault.otp@gmail.com", "teim weav dard ipje", )

    def send_email(
            self,
            target_email: str,
            subject: str,
            body: str,
            attachments: list[str] = [],
            cc: list[str] = [],
            bcc: list[str] = [],
    ):
        self.server.send(
            to=target_email,
            subject=subject,
            contents=body,
            attachments=[yagmail.inline(i) for i in attachments],
            cc=cc,
            bcc=bcc,
        )

    def send_otp(self, target_username, target_email):
        self.otp = ''.join(random.choices(string.digits, k=6))

        self.send_email(
            target_email=target_email,
            subject="OTP to access CipherVault",
            body=f"Welcome back to CipherVault, {target_username}!"
                 f"Please use the OTP given to complete your authentication.\n"
                 f"OTP: {self.otp}"
        )
