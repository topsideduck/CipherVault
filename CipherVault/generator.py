#  Copyright (c) 2023 Harikeshav R
#  All rights reserved.

import os
import random
import secrets
import string


class Generator:
    def __init__(self):
        pass

    @staticmethod
    def generate_username():
        data_dir = os.path.join(os.path.dirname(__file__), 'data')

        noun = random.choice(
            open(os.path.join(data_dir, 'nouns.txt'), 'r').read().strip().split()).lower().capitalize()
        adjective = random.choice(
            open(os.path.join(data_dir, 'adjectives.txt'), 'r').read().strip().split()).capitalize()
        number = str(random.randint(1, 99))

        return adjective + noun + number

    @staticmethod
    def generate_password(password_length: int,
                          minimum_uppercase_characters: int,
                          minimum_numerical_characters: int,
                          minimum_special_characters: int):
        character_set = string.ascii_letters + string.digits + string.punctuation

        while True:
            password = ''.join(secrets.choice(character_set) for _ in range(password_length))
            if (sum(c.isupper() for c in password) >= minimum_uppercase_characters
                and sum(c.isdigit() for c in password) >= minimum_numerical_characters) \
                    and sum(True for c in password if c in string.punctuation) >= minimum_special_characters:
                return password

# generator = Generator(16, 2, 3, 4)
# print(generator.generate_username())
# print(generator.generate_password())
