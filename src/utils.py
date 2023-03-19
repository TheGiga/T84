# Created by me, minimized size by Fenrir#6682
def progress_bar(percent: int) -> str:
    bar = "⬛" * 10
    bar = bar.replace("⬛", "🟨", round(max(min(percent, 100), 0) / 10))
    return bar

def boolean_emoji(boolean: bool) -> str:
    return "✅" if boolean else "❌"