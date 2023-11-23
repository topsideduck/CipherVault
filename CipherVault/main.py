#  Copyright (c) 2023 Harikeshav R
#  All rights reserved.

import sys

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, IntPrompt, Confirm
from rich.table import Table

from biometrics import Biometrics
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

        self.biometrics = Biometrics()
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

    def process_otp(self, master_username: str, master_email_address: str):
        while True:
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

        self.console.print(
            "[cyan]For an additional layer of security, please register your face for biometric authentication."
            " Press space to capture your face to use Face ID.")

        face_path = self.biometrics.register_new_face()

        self.console.print("[bold green]Your face has been registered!")

        if not self.database.create_master(master_username, master_email_address, master_password_hashed, face_path):
            self.console.print(
                "[bold red]There was an error while creating your master account. Please try again later.")
            sys.exit()

        self.console.print("[bold green]Your account has been successfully created. Thank you for using CipherVault!")

        if Confirm.ask("[cyan]Do you want to login now?"):
            self.console.clear()
            self.login()

        else:
            self.console.print("[cyan]Exiting...")
            sys.exit()

    def login(self):
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

        with self.console.status("[cyan]Authenticating via Face ID..."):
            if not self.biometrics.recognise(master_account[4]):
                self.console.print(
                    "[bold red]Face ID authentication failed! Please try OTP verification instead.")
                face_id = False

            else:
                self.console.print("[bold green]Successfully authenticated via Face ID!")
                face_id = True

        if not face_id:
            self.process_otp(master_username, master_email_address)

        self.master_id = master_account[0]
        self.master_username = master_username
        self.master_email_address = master_email_address
        self.master_password = master_password
        self.master_face_path = master_account[4]

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

        if not self.database.create_credential(self.master_id, website, username, encrypted_password):
            self.console.print(
                "[bold red]An error occurred, and the storage of new credentials failed. Please try again later.")
            return

        self.console.print(f"[bold green]Your login details for {website} have been stored successfully!")

    def list_all_entries(self):
        all_entries = self.database.read_all_credentials(self.master_id)

        if not all_entries:
            self.console.print(
                "[bold red]An error occurred, and the fetching of credentials failed. Please try again later.")
            return

        all_entries_table = Table(title=f"All stored credentials for {self.master_username}")

        all_entries_table.add_column("ID", justify="center", style="turquoise2")
        all_entries_table.add_column("Website", justify="center", style="yellow")
        all_entries_table.add_column("Username", justify="center", style="bright_magenta")
        all_entries_table.add_column("Encrypted Password", justify="center", style="red")

        for entry in all_entries:
            all_entries_table.add_row(str(entry[0]), str(entry[2]), str(entry[3]), str(entry[4]))

        self.console.print(all_entries_table)

    def list_specific_entry(self, _id: int):
        entry = self.database.read_single_credential(_id)

        if not entry:
            self.console.print(
                "[bold red]An error occurred, and the fetching of credentials failed. Please try again later.")
            return

        entry_table = Table(title=f"Credential ID: {_id}")
        entry_table.add_column("Website", justify="center", style="yellow")
        entry_table.add_column("Username", justify="center", style="bright_magenta")
        entry_table.add_column("Decrypted Password", justify="center", style="red")
        entry_table.add_row(
            str(entry[2]),
            str(entry[3]),
            str(self.credentials_encryption_handler.decrypt(entry[4]))
        )

        self.console.print(entry_table)

    def update_entry(self, _id: int):
        self.list_specific_entry(_id)

        if Confirm.ask("[cyan]Do you want to update the website?"):
            website = Prompt.ask("[cyan]Enter the new website")

        else:
            website = None

        if Confirm.ask("[cyan]Do you want to update the username?"):
            if Confirm.ask("[cyan]Do you want a randomly generated username?"):
                while True:
                    username = self.generator.generate_username()

                    if Confirm.ask(f"[cyan]Do you want to use the username {username} ?"):
                        break

            else:
                username = Prompt.ask(f"[cyan]Enter a new username")

        else:
            username = None

        if Confirm.ask("[cyan]Do you want to update the password?"):
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

                    if Confirm.ask(f"[cyan]Do you want to use the password {password} ?"):
                        break

            else:
                password = Prompt.ask(f"[cyan]Enter the updated password", password=True)

        else:
            password = None

        if password is not None:
            encrypted_password = self.credentials_encryption_handler.encrypt(password)

        else:
            encrypted_password = None

        if not self.database.update_credential(_id, website, username, encrypted_password):
            self.console.print(
                "[bold red]An error occurred, and the updating of new credentials failed. Please try again later.")
            return

        self.console.print(f"[bold green]Your login details have been updated successfully!")

    def delete_entry(self, _id: int):
        if not Confirm.ask("[red]Are you sure you want to delete this record? This action cannot be undone."):
            return

        if not self.database.delete_entry(_id):
            self.console.print(
                "[bold red]An error occurred, and the credentials could not be deleted. Please try again later.")
            return

        self.console.print("[bold green]The record was successfully deleted!")

    def delete_master_account(self):
        self.console.print("[bold red]DANGER")

        if not Confirm.ask("[bold red]Are you sure you want to delete all records and wipe your master account?"
                           " This action cannot be undone."):
            return

        while True:
            if Prompt.ask(
                    "[red]As this is a sensitive command, please enter your password to continue",
                    password=True) == self.master_password:
                break

            self.console.print("[red]Invalid password! Please try again.")

        if not self.database.delete_account(self.master_id):
            self.console.print(
                "[bold red]An error occurred, and your account could not be deleted. Please try again later.")
            return

        self.console.print("[bold green]Your account and all records associated with it were successfully deleted!")
        self.console.print("[cyan]Exiting...")
        sys.exit()

    def menu(self):
        while True:
            self.console.print(Panel("[bold yellow]Welcome to CipherVault", border_style="red", highlight=True,
                                     title="CipherVault Password Manager", subtitle="Version 0.1 alpha"),
                               justify="center")

            self.console.print(f"[cyan]1: [turquoise2]Create a new credential entry.")
            self.console.print(f"[cyan]2: [turquoise2]List all credential entries.")
            self.console.print(f"[cyan]3: [turquoise2]Decrypt a specific entry.")
            self.console.print(f"[cyan]4: [turquoise2]Update a specific entry.")
            self.console.print(f"[bold red]5: [red]Delete a specific entry.")
            self.console.print(f"[bold red]6: [red]Delete all entries and wipe your account.")
            self.console.print(f"[cyan]7: [turquoise2]Exit CipherVault.")

            choice = IntPrompt.ask("Choose an option", choices=[str(i) for i in range(1, 8)])

            with self.console.status("[cyan]Authenticating via Face ID..."):
                if not self.biometrics.recognise(self.master_face_path):
                    self.console.print(
                        "[bold red]Face ID authentication failed. Unauthorised!")
                    face_id = False

                else:
                    self.console.print("[bold green]Authenticated via Face ID!")
                    face_id = True

            if not face_id:
                self.console.print(
                    "[cyan]For security purposes, your screen will be cleared. Press enter to continue.")
                input()
                self.console.clear()
                continue

            match choice:
                case 1:
                    self.create_new_entry()
                case 2:
                    self.list_all_entries()
                case 3:
                    records = self.database.read_all_credentials(self.master_id)
                    _id = IntPrompt.ask("Enter the ID of the entry you want to decrypt",
                                        choices=[str(i[0]) for i in records])
                    self.list_specific_entry(_id)
                case 4:
                    records = self.database.read_all_credentials(self.master_id)
                    _id = IntPrompt.ask("Enter the ID of the entry you want to update",
                                        choices=[str(i[0]) for i in records])
                    self.update_entry(_id)
                case 5:
                    records = self.database.read_all_credentials(self.master_id)
                    _id = IntPrompt.ask("Enter the ID of the entry you want to delete",
                                        choices=[str(i[0]) for i in records])
                    self.delete_entry(_id)
                case 6:
                    self.delete_master_account()
                case 7:
                    self.console.print("[cyan]Exiting...")
                    sys.exit()

            self.console.print("[cyan]For security purposes, your screen will be cleared. Press enter to continue.")
            input()
            self.console.clear()

    def execute(self):
        self.authenticate()
        self.menu()


a = App()
a.execute()
