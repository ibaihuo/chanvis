from comm.conf import ALL_SYMBOLS, STOCK_DB
from utils.nlchan import sym_float

SUPPORT_SYMBOLS = []

for symbol in ALL_SYMBOLS:
    sym, minmov = symbol['symbol'], symbol['minmov']

    if sym == 'TUSD':
        continue

    # ps = 1
    # for chr in minmov:
    #     if chr == '.':
    #         continue
    #     if chr == '1':
    #         break
    #     ps *= 10
    #
    # # 小数点的位数
    # ps = int(ps)
    # # print(sym, minmov, ps)
    ps, _ = sym_float(minmov)

    sym_info = {"name": sym,
                "symbol": sym,
                "description": sym,
                "exchange": "自然之缠",
                "minmov": 1,
                "minmov2": 0,
                "pricescale": ps,
                "has_intraday": True,
                "type": "bitcoin",
                "ticker": sym,
                "session": "24x7",
                "timezone": "Asia/Shanghai",
                "intraday_multipliers": ["1", "5", "30", "240", "D"],
                }
    SUPPORT_SYMBOLS.append(sym_info)


"""
股票数据
"""


stock_info = list(STOCK_DB['stock_names'].find({},
                                              {'_id': False, 'code': True, 'display_name': True, 'name': True})
                  )
# print(stock_info)


for item in stock_info:
    code, display_name, name = item['code'], item['display_name'], item['name']
    stk_info = {"name": name,
                "symbol": code,
                "description": f'{display_name}[{code}]',
                "exchange": "自然之缠",
                "minmov": 1,
                "minmov2": 0,
                "pricescale": 100,
                "has_intraday": True,
                "type": "stock",
                "ticker": code,      # 这个字段，才是前端调用需要的字段
                "session": "24x7",   # 这个如果设置为0930-1530的话，小时，2小数，8分钟这样的数据就无法获取到；
                "timezone": "Asia/Shanghai",
                "intraday_multipliers": ["1", "5", "30", "D"],
                }
    SUPPORT_SYMBOLS.append(stk_info)


if __name__ == '__main__':
    from pprint import pprint
    pprint(SUPPORT_SYMBOLS[:10])