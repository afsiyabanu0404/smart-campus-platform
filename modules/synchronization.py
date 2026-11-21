def should_retry(status_code):
    # Retry transient server errors and rate limits, not ordinary client errors.
    return status_code == 429 or (isinstance(status_code, int) and 500 <= status_code <= 599)
