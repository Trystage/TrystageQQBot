from random import randint, seed
from time import time

def dice(d: int, _seed):
    """骰子

    Args:
        d (int): 上限
        _seed (_type_): 随机数种子

    Returns:
        int: 值
    """

    seed(int(time()) ^ int(d) ^ int(_seed))
    return randint(1, int(d))