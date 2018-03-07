import math
import os


def limitedchaos():
    return ord(os.urandom(1)) / 256.0


def randint():
    return int(math.floor(limitedchaos() * 10 + 1))


def randrange(start=0, end=10):
    return int(math.floor(limitedchaos() * ((end - start) + 1) + start))
