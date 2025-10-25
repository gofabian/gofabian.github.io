import math
import time


def batch(symbols: list[str], batch_size: int, sleep_secs: int, fn):
    total = len(symbols)
    num_batches = math.ceil(total / batch_size)

    print(f"Verarbeite {total} Symbole in {num_batches} Batches...")

    for batch_num in range(num_batches):
        start = batch_num * batch_size
        end = min(start + batch_size, total)
        symbols_batch = symbols[start:end]

        print(f"Batch {batch_num + 1}/{num_batches}: {len(symbols_batch)} Symbols")
        fn(symbols_batch)

        if batch_num < num_batches - 1:
            print(f"⏳ Warte 10 Minuten, um IB-Pacing einzuhalten...")
            time.sleep(sleep_secs)
