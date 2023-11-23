#  Copyright (c) 2023 Harikeshav R
#  All rights reserved.

import sys

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, IntPrompt, Confirm

from database import Database
from encryption import MasterEncryption, CredentialEncryption
from generator import Generator
from otp import OTP


class App:
    def __init__(self):
        self.master_id: int
        self.master_username: str
        self.master_email_address: str
        self.master_password: str

        self.master_encryption_handler: MasterEncryption
        self.credentials_encryption_handler: CredentialEncryption

        self.database = Database("localhost", "CipherVault", "hEN!M&bDdkCHN3S%")
        self.generator = Generator()
        self.otp = OTP()

        self.console = Console()
        self.console.clear()

        self.console.print(Panel("[bold yellow]Welcome to CipherVault", border_style="red", highlight=True,
                                 title="CipherVault Password Manager", subtitle="Version 0.1 alpha"), justify="center")

    def authenticate(self):
        signup_or_login = Prompt.ask("[cyan]Do you want to sign up or login?", choices=["Signup", "Login"])

        if signup_or_login.lower() == "signup":
            self.signup()

        elif signup_or_login.lower() == "login":
            self.login()

    def process_otp(self, master_username: str, master_email_address: str, otp_needed: bool = True):
        while otp_needed:
            with self.console.status("[yellow]Working...", spinner="point"):
                self.otp.send_otp(master_username, master_email_address)

            user_otp = Prompt.ask(
                "[cyan]An OTP was just sent to your registered email address. Please enter it here for verification")

            if self.otp.otp == user_otp:
                self.console.print("[bold green]Your OTP was correct!")
                break

            else:
                self.console.print(
                    "[bold red]The entered OTP was wrong! A new OTP has been sent, please enter the new otp again.")

    def signup(self):
        master_username = Prompt.ask("[cyan]Please create a username")
        master_email_address = Prompt.ask("[cyan]Please enter your email address")

        while True:
            master_password = Prompt.ask(
                "[cyan]Please create a master password. You must remember this password, as it cannot be recovered",
                password=True)
            master_password_reconfirm = Prompt.ask("[cyan]Please enter your master password again to confirm",
                                                   password=True)

            if master_password == master_password_reconfirm:
                break

            self.console.print("[red]Your passwords did not match. Please check your passwords again.")

        self.process_otp(master_username, master_email_address)

        self.master_encryption_handler = MasterEncryption(master_password.encode())
        self.credentials_encryption_handler = CredentialEncryption(master_password)

        master_password_hashed = self.master_encryption_handler.get_hashed_password()

        if not self.database.create_master(master_username, master_email_address, master_password_hashed):
            self.console.print(
                "[bold red]There was an error while creating your master account. Please try again later.")
            sys.exit()

        self.console.print("[bold green]Your account has been successfully created. Thank you for using CipherVault!")

        if Confirm.ask("[cyan]Do you want to login now?"):
            self.console.clear()
            self.login(otp_needed=False)

        else:
            self.console.print("[cyan]Exiting...")
            sys.exit()

    def login(self, otp_needed: bool = True):
        while True:
            master_username = Prompt.ask("[cyan]Please enter your username")
            master_password = Prompt.ask("[cyan]Please enter your password", password=True)

            self.master_encryption_handler = MasterEncryption(master_password.encode())
            self.credentials_encryption_handler = CredentialEncryption(master_password)

            master_account = self.database.read_master(master_username)

            if not master_account:
                self.console.print(
                    "[bold red]Unable to login! Please check your login credentials and try again.")
                continue

            if self.master_encryption_handler.check_password(master_account[3].encode()):
                break

            self.console.print(
                "[bold red]Unable to login! Please check your login credentials and try again.")

        master_email_address = master_account[2]
        self.process_otp(master_username, master_email_address, otp_needed)

        self.master_id = master_account[0]
        self.master_username = master_username
        self.master_email_address = master_email_address
        self.master_password = master_password

        self.console.print(f"[bold green]Successfully logged in as {master_username}!")

    def create_new_entry(self):
        website = Prompt.ask("[cyan]Enter the website to store credentials for")

        if Confirm.ask("[cyan]Do you want a randomly generated username?"):
            while True:
                username = self.generator.generate_username()

                if Confirm.ask(f"[cyan]Do you want to use the username {username} for the website {website} ?"):
                    break

        else:
            username = Prompt.ask(f"[cyan]Enter a username for the website {website}")

        if Confirm.ask("[cyan]Do you want a randomly generated password?"):
            password_length = IntPrompt.ask("[cyan]Enter the password length", default=16)
            minimum_uppercase_characters = IntPrompt.ask("[cyan]Enter the minimum number of uppercase characters",
                                                         default=1)
            minimum_numerical_characters = IntPrompt.ask("[cyan]Enter the minimum number of numerical characters",
                                                         default=1)
            minimum_special_characters = IntPrompt.ask("[cyan]Enter the minimum number of special characters",
                                                       default=1)

            while True:
                password = self.generator.generate_password(
                    password_length,
                    minimum_uppercase_characters,
                    minimum_numerical_characters,
                    minimum_special_characters
                )

                if Confirm.ask(f"[cyan]Do you want to use the password {password} for the website {website} ?"):
                    break

        else:
            password = Prompt.ask(f"[cyan]Enter a password for the website {website}", password=True)

        encrypted_password = self.credentials_encryption_handler.encrypt(password)
        self.database.create_credential(self.master_id, website, username, encrypted_password)

        self.console.print(f"[bold green]Your login details for {website} have been stored successfully!")

    def execute(self):
        self.authenticate()
        self.create_new_entry()


a = App()
a.execute()
