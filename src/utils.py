from typing import Union


def decimal(value: Union[int, float]):
    return f"{int(value * 100) / 100:.2f}"
