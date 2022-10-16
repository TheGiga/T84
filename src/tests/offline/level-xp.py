from math import sqrt, floor


def xp_to_level(xp: int) -> int:
    level_raw = 0.3 * sqrt(xp)
    level = floor(level_raw)

    return level


if __name__ == "__main__":
    x = 1
    level = 0
    while True:
        new_level = xp_to_level(x)

        if new_level != level:
            print(f"XP {x} = {new_level}")
            level = new_level

        x += 1

        if level > 100:
            break
