def even_cuts(start, end, n):
    """Return n evenly spaced cuts between start and end."""
    return [start + (end - start) * i / (n + 1) for i in range(0, n + 2)]


def grouped(l, n):
    """Group a list into n-sized chunks."""
    return [l[i:i + n] for i in range(0, len(l), n)]
