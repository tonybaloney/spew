import random as _random
import typing

TCycle = typing.TypeVar("TCycle")


# Define a cycle that yields a random element in a list until it is exhausted then starts again
def rcycle(l: typing.Iterable[TCycle]) -> typing.Generator[TCycle, None, None]:
    while True:
        items = list(l)
        _random.shuffle(items)
        for item in items:
            yield item
