#  Copyright (c) 2023 Harikeshav R
#  All rights reserved.

import mysql.connector


class Database:
    def __init__(self, host: str, mysql_username: str, mysql_password: str):
        self.connector = mysql.connector.connect(host=host, username=mysql_username, password=mysql_password)
        self.cursor = self.connector.cursor()

        self.setup()

    def setup(self):
        self.cursor.execute("CREATE DATABASE IF NOT EXISTS CipherVault")
        self.cursor.execute("USE CipherVault")

        self.cursor.execute("""
CREATE TABLE IF NOT EXISTS Masters
(
    MasterID INT NOT NULL AUTO_INCREMENT,
    MasterUsername VARCHAR(256) UNIQUE NOT NULL,
    MasterEmailAddress VARCHAR(256) UNIQUE NOT NULL,
    MasterPassword VARCHAR(256) NOT NULL,
    PRIMARY KEY (MasterID)
)
        """)

        self.cursor.execute("""
CREATE TABLE IF NOT EXISTS Credentials
(
    CredentialID INT NOT NULL AUTO_INCREMENT,
    MasterID INT NOT NULL,
    Website VARCHAR(256) NOT NULL,
    Username VARCHAR(256) NOT NULL,
    Password VARCHAR(256) NOT NULL,
    PRIMARY KEY (CredentialID),
    INDEX (MasterID),
    FOREIGN KEY (MasterID) REFERENCES Masters(MasterID)
)
        """)

        self.connector.commit()

    def create_master(self, master_username: str, master_email_address: str, master_password_hashed: str):
        try:
            self.cursor.execute(
                "INSERT INTO Masters (MasterUsername, MasterEmailAddress, MasterPassword) VALUES (%s, %s, %s)",
                (master_username, master_email_address, master_password_hashed))

            self.connector.commit()

            return True

        except:
            return False

    def create_credential(self, master_id: int, website: str, username: str, encrypted_password: str):
        try:
            self.cursor.execute(
                "INSERT INTO Credentials (MasterID, Website, Username, Password) VALUES (%s, %s, %s, %s)",
                (master_id, website, username, encrypted_password)
            )

            self.connector.commit()

            return True

        except:
            return False

    def read_master(self, master_username: str):
        try:
            self.cursor.execute(
                "SELECT * FROM Masters WHERE MasterUsername = %s",
                (master_username,))
            return self.cursor.fetchone()

        except:
            return None

    def read_single_credential(self, credential_id: int):
        try:
            self.cursor.execute("SELECT * FROM Credentials WHERE CredentialID = %s", (credential_id,))
            return self.cursor.fetchone()

        except:
            return None

    def read_all_credentials(self, master_id: int):
        try:
            self.cursor.execute("SELECT * FROM Credentials WHERE MasterID = %s", (master_id,))
            return self.cursor.fetchall()

        except:
            return None
