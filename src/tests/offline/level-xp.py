import math
from math import sqrt, floor

import config


def level_to_xp(level: int) -> int:
    xp = level // config.XP_MULTIPLIER
    xp = xp ** 2

    return floor(xp)


def xp_to_level(xp: int) -> int:
    lvl_raw = config.XP_MULTIPLIER * sqrt(xp)
    lvl = floor(lvl_raw)

    return lvl


if __name__ == "__main__":
    x = 1
    level = 0
    while True:
        new_level = xp_to_level(x)

        if new_level != level:
            print(f"XP {x:1,} = {new_level}")
            level = new_level

        x += 1

        if level > 100:
            break

    print("XP_TO_LEVEL ^ ------------- LEVEL_TO_XP v")

    y = 1
    xp = 0

    while True:
        new_xp = level_to_xp(y)

        if new_xp != xp:
            print(f"LEVEL {y} = {new_xp:1,}")
            xp = new_xp

        y += 1

        if xp > 160_000:
            break
