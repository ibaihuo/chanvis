"""
chan相关的utils方法
"""


def sym_float(minmov):
    """获取小数点的位数
    """
    minmov = str(minmov)

    ps = 1
    bits = 0

    for chr in minmov:
        if chr == '.':
            continue
        if chr == '1':
            break
        ps *= 10
        bits += 1

    # 小数点的位数
    ps = int(ps)

    return ps, bits