from math import log


def pretty_size(n, pow=0, b=1024, u='B', pre=[''] + [p + 'i' for p in 'KMGTPEZY']):
    pow, n = min(int(log(max(n * b ** pow, 1), b)), len(pre) - 1), n * b ** pow
    return "%%.%if %%s%%s" % abs(pow % (-pow - 1)) % (n / b ** float(pow), pre[pow], u)
