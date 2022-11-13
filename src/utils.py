def progress_bar(percent: int) -> str:
    raw_percents = percent // 10
    bar = ""

    for _ in range(raw_percents):
        bar += "🟨"

    return bar.ljust(10, "⬛")
