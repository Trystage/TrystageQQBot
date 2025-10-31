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

def truncate_error_message(error_msg, max_length=80):
    """截断错误信息到指定长度"""
    if len(error_msg) <= max_length:
        return error_msg
    return error_msg[:max_length] + f"...(完整长度:{len(error_msg)})"