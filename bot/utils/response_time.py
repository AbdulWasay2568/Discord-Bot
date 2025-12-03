import time

def format_elapsed_time(start_time: float) -> str:
    elapsed = time.time() - start_time
    if elapsed < 1:
        return f"{elapsed*1000:.0f}ms"
    return f"{elapsed:.2f}s"
