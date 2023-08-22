import random

FIRST_CHARS = "abcdefghijklmnopqrstuvwxyz"
OTHER_CHARS = "abcdefghijklmnopqrstuvwxyz1234567890_"


def generate(ctx, new: bool = False) -> str:
    # TODO: create unique names
    if not new and ctx.names:
        return random.choice(ctx.names)

    name = random.choice(FIRST_CHARS)
    for _ in range(10):
        name += random.choice(OTHER_CHARS)
    ctx.names.append(name)
    return name
