import time
import datetime

import pandas as pd
from dateutil import tz
# from dateutil.tz import tzlocal
from comm.conf import OK_KDATA_COLUMNS, STAND_KDATA_COLUMNS, BA_KDATA_COLUMNS

from datetime import datetime, timedelta, timezone

from termcolor import colored


def print_red(info):
    print(colored(info, "red"), flush=True)


def print_green(info):
    print(colored(info, "green"), flush=True)


def time2int(tt):
    return int(time.mktime(time.strptime(tt, "%Y-%m-%d %H:%M:%S")))


def slash_time2int(tt):
    return int(time.mktime(time.strptime(tt, "%Y/%m/%d %H:%M")))


def gmt2int(gmt):
    # xx = time.strptime(gmt, '%Y-%m-%dT%H:%M:%S.%fZ')
    xx = time.strptime(gmt, '%Y-%m-%d %H:%M:%S')

    ts = int(time.mktime(xx))

    return ts


def gmt2local(gmt):
    # get local time zone name
    # print(datetime.now(tzlocal()).tzname())
    # from_zone = tz.gettz('UTC')
    # to_zone = tz.gettz('CST')
    # utc = datetime.utcnow()
    utc = datetime.strptime(str(gmt), '%Y-%m-%dT%H:%M:%S.%fZ')

    # Tell the datetime object that it's in UTC time zone
    # utc = utc.replace(tzinfo=from_zone)
    #
    # tzutc_8 = timezone(timedelta(hours=8))
    #
    # # Convert time zone
    # local = utc.astimezone(tzutc_8)
    #
    # local = datetime.strftime(local, "%Y-%m-%d %H:%M:%S")

    local = utc + timedelta(hours=8)
    local = datetime.strftime(local, "%Y-%m-%d %H:%M:%S")

    # print(gmt, local)

    return local


def make_hist(data):
    df = pd.DataFrame(data, columns=OK_KDATA_COLUMNS)

    # print(df.head())
    df['datetime'] = df['datetime'].map(lambda x: gmt2local(x))
    df['id'] = df['datetime'].map(lambda x: gmt2int(x))
    df['open'] = df['open'].map(lambda x: float(x))
    df['high'] = df['high'].map(lambda x: float(x))
    df['low'] = df['low'].map(lambda x: float(x))
    df['close'] = df['close'].map(lambda x: float(x))

    # add a const 0 for count column
    df['count'] = df['id'].map(lambda x: int(0))

    df['volume'] = df['volume'].map(lambda x: float(x))
    df['amount'] = df['currency_volume'].map(lambda x: float(x))

    df = df[STAND_KDATA_COLUMNS]
    df.columns = STAND_KDATA_COLUMNS

    return df


def okex_make_hist(data):
    df = pd.DataFrame(data, columns=OK_KDATA_COLUMNS)

    # print(df.head())
    df['id'] = df['datetime'].map(lambda x: int(x)//1000)
    df['datetime'] = df['id'].map(lambda x: int2time(x))

    df['open'] = df['open'].map(lambda x: float(x))
    df['high'] = df['high'].map(lambda x: float(x))
    df['low'] = df['low'].map(lambda x: float(x))
    df['close'] = df['close'].map(lambda x: float(x))

    df['volume'] = df['volume'].map(lambda x: int(x))
    df['amount'] = df['amount'].map(lambda x: float(x))

    df = df[STAND_KDATA_COLUMNS]
    df.columns = STAND_KDATA_COLUMNS

    return df



def binance_make_hist(result):
    data = []

    for item in result[::-1]:
        data.append([item.openTime,
                     item.open, item.high, item.low, item.close,
                     item.volume, item.quoteAssetVolume])

    df = pd.DataFrame(data, columns=BA_KDATA_COLUMNS)

    df['id'] = df['id'].map(lambda x: str(x//1000))
    df['datetime'] = df['id'].map(lambda x: int2time(x))

    df['open'] = df['open'].map(lambda x: float(x))
    df['high'] = df['high'].map(lambda x: float(x))
    df['low'] = df['low'].map(lambda x: float(x))
    df['close'] = df['close'].map(lambda x: float(x))

    df['count'] = df['id'].map(lambda x: int(0))

    df = df[STAND_KDATA_COLUMNS]
    df.columns = STAND_KDATA_COLUMNS

    return df


def get_start(mins=200):
    start = (datetime.utcnow() - timedelta(minutes=mins)).isoformat() + 'Z'

    return start


def get_end():
    end = datetime.utcnow().isoformat() + 'Z'

    return end


def int2time(timestamp):
    timestamp = int(timestamp)
    value = time.localtime(timestamp)
    dt = time.strftime('%Y-%m-%d %H:%M:%S', value)

    # print('ts:', dt)
    return dt


def int2hour(timestamp):
    timestamp = int(timestamp)
    value = time.localtime(timestamp)
    dt = time.strftime('%Y-%m-%d:%H', value)

    # print('ts:', dt)
    return dt


def tomerge_15(x):
    h = x // (60 * 60) * (60 * 60)
    m = x % (24 * 60 * 60) % (60 * 60) // (60 * 15) * 15

    return h + m * 60


def tomerge_60(x):
    h = x // (60 * 60) * (60 * 60)
    m = x % (24 * 60 * 60) % (60 * 60) // (60 * 60) * 60

    return int2time(h + m * 60)


def to_4hour(d):
    datestr, hour = d.split()

    if '00:00:00' <= hour < '04:00:00':
        h = '20:00:00'
        date = datetime.datetime.strptime(datestr, '%Y-%m-%d')
        date = date + datetime.timedelta(days=-1)
        datestr = datetime.datetime.strftime(date, '%Y-%m-%d')
    elif '04:00:00' <= hour < '08:00:00':
        h = '00:00:00'
    elif '08:00:00' <= hour < '12:00:00':
        h = '04:00:00'
    elif '12:00:00' <= hour < '16:00:00':
        h = '08:00:00'
    elif '16:00:00' <= hour < '20:00:00':
        h = '12:00:00'
    elif '20:00:00' <= hour < '24:00:00':
        h = '16:00:00'

    return f'{datestr} {h}'


if __name__ == '__main__':
    print(int2time(1551595920))
    print(gmt2local('2019-12-04T10:15:00.000Z'))
    # print(gmt2int('2019-01-23T08:57:00.000Z'))

