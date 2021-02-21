from datetime import datetime, timedelta

TABLE_DATA = [
    {
        "real_url": "https://real_url1/",
        "short_url": "aaaaaa",
        "valid_to": datetime.now() + timedelta(5)
    },
    {
        "real_url": "https://real_url2/",
        "short_url": "aaaaab",
        "valid_to": datetime.now() + timedelta(15)
    },
    {
        "real_url": "https://old_real_url1/",
        "short_url": "dddddd",
        "valid_to": datetime.now() - timedelta(15)
    }
]