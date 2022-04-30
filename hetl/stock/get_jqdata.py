import time
import pandas as pd
import jqdatasdk as api

from utils.dtlib import time2int
from comm.conf import STOCK_DB


"""
请自定义自己的认证
api.auth('login', 'password')
直接注释下面的2行
"""
import jqauth
api = jqauth.auth(api)


def get_all_secs():
    """获取所有的股票，指数，基金数据"""
    all_secs = api.get_all_securities(types=["stock", "index", "fund"], date=None)
    
    # print(all_secs)
    # all_secs.to_csv('jq_stock_all.csv')
    
    all_secs.index.name = "code"
    all_secs.reset_index(level=0, inplace=True)

    col = STOCK_DB['stock_names']
    col.delete_many({})
    col.insert_many(all_secs.to_dict('records'))


def get_day_hist(symbol, tf='1d', start_date="2005-01-01", end_date="2022-12-31"):
    """获取日线数据"""
    hist = api.get_price(symbol, start_date=start_date, end_date=end_date)
    # hist.to_csv('chgf.csv')
    # print(hist)
    # hist = pd.read_csv('hwsw.csv')

    hist.index.name = 'dt'

    hist.reset_index(level=0, inplace=True)

    hist['datetime'] = hist['dt'].apply(lambda _: f'{str(_).replace("00:00:00", "08:00:00")}')
    hist['ts'] = hist['datetime'].apply(time2int)
    hist = hist[["datetime", 'ts', 'open', 'high', 'low', 'close', 'volume']]
    hist = hist.query('volume !=0')
    print(hist)

    hist.dropna(inplace=True)

    if not hist.empty:
        # col = STOCK_DB[f'stk_{symbol.split(".")[0]}_{tf}']
        col = STOCK_DB[f'stk_{symbol}_{tf}']
        col.delete_many({})
        col.insert_many(hist.to_dict('records'))


def get_all_history():
    """获取所有票的历史数据
    """
    # stocks = pd.DataFrame(STOCK_DB[f'stock_names'].find({'type': {'$in': ["stock", "index"]}}, {'_id':False}))
    stocks = pd.read_csv('/Users/baihuo/5-Huo/NaturalChan/chanvis/hetl/stock/jq_stock_all.csv')
    print(stocks)

    i = 1
    for _, row in stocks.iterrows():
        code, name, itype = row['code'], row['display_name'], row['type']
        # 指数，只取上证指数
        if itype == 'index' and code != '000001.XSHG':
            continue

        start_dt, end_dt = str(row['start_date']), str(row['end_date'])
        if start_dt <= '2005-01-01':
            start_dt = '2005-01-01'
        elif start_dt >= '2021-01-01':
            # 数据量太少，直接略过
            continue

        i += 1
        get_day_hist(code, tf='1d', start_date=start_dt, end_date=end_dt)

        print(f'[{i}] processing [{itype}] [{name}], range: [{start_dt}]-[{end_dt}]')
        time.sleep(1)

        # if i > 3:
        #     break
    


if __name__ == '__main__':
    # symbol = '000001.XSHG'
    # symbol = '002291.XSHE'
    # get_day_hist(symbol)
    # get_all_secs()

    get_all_history()
