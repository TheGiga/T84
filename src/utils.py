def progress_bar(percent: int) -> str:
    bar = ""

    for i in range(round(max(min(percent, 100), 0) / 10)):
        bar += "🟨"

    return bar.ljust(10, "⬛")
