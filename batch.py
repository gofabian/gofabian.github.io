import math
import time
from datetime import datetime, timedelta

from log import log


def batch(symbols: list[str], batch_size: int, sleep_secs: int, fn):
    total = len(symbols)
    num_batches = math.ceil(total / batch_size)

    log(f"Verarbeite {total} Symbole in {num_batches} Batches...")

    for batch_num in range(num_batches):
        start = batch_num * batch_size
        end = min(start + batch_size, total)
        symbols_batch = symbols[start:end]

        log(f"Batch {batch_num + 1}/{num_batches}: {len(symbols_batch)} Symbols")
        datetime_before = datetime.now()
        fn(symbols_batch, batch_num, num_batches)

        if batch_num < num_batches - 1:
            sleep_secs_rest = (datetime_before + timedelta(seconds=sleep_secs) - datetime.now()).total_seconds()
            log(f"⏳ Warte {sleep_secs_rest}s, um IB-Pacing einzuhalten...")
            if sleep_secs_rest > 0:
                time.sleep(sleep_secs)
