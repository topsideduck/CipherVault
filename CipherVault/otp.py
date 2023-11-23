#  Copyright (c) 2023 Harikeshav R
#  All rights reserved.

import random
import string

import yagmail


class OTP:
    def __init__(self, email_address: str, password: str, target_username: str, target_email: str):
        self.server = yagmail.SMTP(email_address, password)
        self.otp = ''.join(random.choices(string.digits, k=6))

        self.target_username = target_username
        self.target_email = target_email

        self.send_otp()

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

    def send_otp(self):
        self.send_email(
            target_email=self.target_email,
            subject="OTP to access CipherVault",
            body=f"Welcome back to CipherVault, {self.target_username}!"
                 f"Please use the OTP given to complete your authentication.\n"
                 f"OTP: {self.otp}"
        )
