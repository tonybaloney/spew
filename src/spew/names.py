import random

FIRST_CHARS = "abcdefghijklmnopqrstuvwxyz"
OTHER_CHARS = "abcdefghijklmnopqrstuvwxyz1234567890_"

def generate() -> str:
    # TODO: create unique names
    name = random.choice(FIRST_CHARS)
    for _ in range(10):
        name += random.choice(OTHER_CHARS)
    return name
    