from datetime import datetime


def log(*args, **kwargs):
    timestamp = datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
    kwargs = kwargs.copy()
    kwargs['flush'] = True
    print(timestamp, *args, **kwargs)
