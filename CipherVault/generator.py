#  Copyright (c) 2023 Harikeshav R
#  All rights reserved.

import os
import random
import secrets
import string


class Generator:
    def __init__(
            self,
            password_length: int,
            minimum_uppercase_characters: int,
            minimum_numerical_characters: int,
            minimum_special_characters: int
    ):
        self.password_length = password_length
        self.minimum_uppercase_characters = minimum_uppercase_characters
        self.minimum_numerical_characters = minimum_numerical_characters
        self.minimum_special_characters = minimum_special_characters
        self.data_dir = os.path.join(os.path.dirname(__file__), 'data')

    def generate_username(self):
        noun = random.choice(
            open(os.path.join(self.data_dir, 'nouns.txt'), 'r').read().strip().split()).lower().capitalize()
        adjective = random.choice(
            open(os.path.join(self.data_dir, 'adjectives.txt'), 'r').read().strip().split()).capitalize()
        number = str(random.randint(1, 99))

        return adjective + noun + number

    def generate_password(self):
        character_set = string.ascii_letters + string.digits + string.punctuation

        while True:
            password = ''.join(secrets.choice(character_set) for _ in range(self.password_length))
            if (sum(c.isupper() for c in password) >= self.minimum_uppercase_characters
                and sum(c.isdigit() for c in password) >= self.minimum_numerical_characters) \
                    and sum(True for c in password if c in string.punctuation):
                return password


# generator = Generator(16, 2, 3, 4)
# print(generator.generate_username())
# print(generator.generate_password())