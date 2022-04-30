
import os.path
import arrow
import logging
from pymongo import MongoClient

DEBUG = False

ROOT_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DATA_PATH = os.path.join(ROOT_PATH, 'data')

RESOU_DICT = {"1": "1m",
              "5": "5m",
              "15": "15m",
              "30": "30m",
              "60": "1h",
              "240": "4h",
              "1D": "1d",
              "1W": "1w",
              }


# 时间周期与对应的秒，用于计算高低点之间的K线数量（因为K线是连续的）
TF_SEC_MAP = {'1m': 1 * 60,
              '5m': 5 * 60,
              '30m': 30 * 60,
              '1h': 1 * 60 * 60,
              '4h': 4 * 60 * 60,
              '1d': 24 * 60 * 60,
              '1w': 7 * 24 * 60 * 60,
              }

# 一天中，不同的时间周期，应该有的K线数据量
TF_DAY_KLINE_CNT = {'1m': 1440,
                    '5m': 1440 // 5,
                    '30m': 1440 // 30,
                    '1h': 1440 // 60,
                    '4h': 1440 // 240,
                    '1d': 1440 // 1440,
                    }



# "volume" 成交量(张)
# "count": 成交笔数,
# "amount": 成交量(币), 即 sum(每一笔成交量(张)*单张合约面值/该笔成交价)

HB_KDATA_COLUMNS = ['id', 'datetime', 'open', 'high', 'low', 'close', 'count', 'vol', 'amount']

OK_KDATA_COLUMNS = ['datetime', 'open', 'high', 'low', 'close', 'volume', 'amount']

BA_KDATA_COLUMNS = ['id', 'open', 'high', 'low', 'close', 'volume', 'amount']

OK_KDATA_COLUMNS = ['ts', 'datetime',
                    'open', 'high', 'low', 'close',
                    'cnt', 'volume', 'currency_volume']

STAND_KDATA_COLUMNS = ['id', 'datetime', 'open', 'high', 'low', 'close', 'volume', 'amount']

E_KDATA_COLUMNS = ["ts", "datetime", "open", "high", "low", "close", "volume"]

GP_KDATA_COLUMNS = ["ts", "datetime", "open", "high", "low", "close", "volume"]

DAY_COLUMNS = ["ts", "date", "open", "high", "low", "close", "volume"]

DTRANGE = {'0001': [],

           # boll带判断二卖
           '0003': ['2007-10-08', '2007-11-30'],
           '0004': ['2006-12-01', '2007-12-31'],

           # 研究小转大
           '0005': ['2019-09-01', '2019-10-16'],

           '0006': ['2019-03-10', '2019-06-10'],

           # 研究百年一人的均线及平方法则
           '0007': ['2001-01-01', '2010-01-01']
           }

if DEBUG:
    # ALL_TIMEFRAMES = ("5m", "30m")
    ALL_TIMEFRAMES = ("30m", "5m", "4h", "1d", "1m")
else:
    ALL_TIMEFRAMES = ("30m", "5m", "4h", "1d", "1m")

# 所有币圈的符号
ALL_SYMBOLS = []

SPECILS = ['DAI', 'TUSD']

if DEBUG:
    fname = os.path.join(ROOT_PATH, 'hetl/selcoin/binance_syms.debug')
else:
    fname = os.path.join(ROOT_PATH, 'hetl/selcoin/binance_syms.txt')

with open(fname) as f:
    for line in f:
        line = line.strip()
        sym, minmov = line.split()

        if sym in SPECILS:
            continue

        item = {'symbol': sym,
                'minmov': minmov,
                }
        ALL_SYMBOLS.append(item)


now = arrow.now()
base_days = 60

DATE_START_TS = {'1m': 1635724800,  # 2021-11-01 08:00:00
                 '5m': now.shift(days=-base_days).int_timestamp,
                 '30m': now.shift(days=-base_days * 6).int_timestamp,
                 '1h': now.shift(days=-base_days * 12).int_timestamp,
                 '4h': now.shift(days=-base_days * 48).int_timestamp,
                 '1d': now.shift(days=-base_days * 48).int_timestamp,
                 '1w': now.shift(days=-base_days * 48).int_timestamp,
                 }

# DATE_START_TS = {'5m': arrow.get('2021-11-27 00:00:00').int_timestamp,
#                  '30m': now.shift(days=-base_days * 6).int_timestamp,
#                  '1h': now.shift(days=-base_days * 12).int_timestamp,
#                  '4h': now.shift(days=-base_days * 48).int_timestamp,
#                  '1d': now.shift(days=-base_days * 48).int_timestamp,
#                  '1w': now.shift(days=-base_days * 48).int_timestamp,
#                  }

# 线段的最大条数
MAX_XD_LEN = 500


# ALL_SYMBOLS = [{'BTC'}, ]



logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)6s - %(name)s - %(funcName)s - %(message)s')


client = MongoClient('localhost', 27017)
CHAN_DB = client.nlchan
HIST_DB = client.ohlcv
STOCK_DB = client.stock
CONF_DB = client.config

BIGEST_PRICE = 999999999

ESSENCE_XD_COL = 'essence_xd_{sym}_{tf}'

ESSENCE_ZS_COL = 'essence_zs_{sym}_{tf}'

LNCHAN_XD_COL = 'lnchan_xd_{sym}_{tf}'

LNCHAN_ZS_COL = 'lnchan_zs_{sym}_{tf}'


if __name__ == '__main__':
    for key, value in DATE_START_TS.items():
        print(key, arrow.get(int(value)).format('YYYY-MM-DD HH:mm:ss'))
        # print(DATE_START_TS)

    print(ALL_SYMBOLS)
    print(ALL_TIMEFRAMES)