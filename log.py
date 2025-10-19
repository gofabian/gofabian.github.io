from datetime import datetime


def log(*args, **kwargs):
    timestamp = datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
    print(timestamp, *args, **kwargs)
