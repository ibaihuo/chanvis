
import json
import os.path
import sys
import re
import time
from pprint import pprint

import arrow
import pandas as pd
from flask import Blueprint, Flask, jsonify, request, Response
from pymongo import ASCENDING, DESCENDING

root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(root_dir)

from symbol_info import SUPPORT_SYMBOLS
from utils.dtlib import time2int, int2time
from comm.conf import DATA_PATH, RESOU_DICT, MAX_XD_LEN, STOCK_DB, TF_SEC_MAP, CHAN_DB, HIST_DB
from comm.conf import ESSENCE_XD_COL, ESSENCE_ZS_COL, LNCHAN_XD_COL, HIST_DB, CONF_DB


app = Flask(__name__)

NaturalChan = Blueprint('NaturalChan', __name__)


def arg_is_notnull(*args):
    """
    参数不能为空时，返回结果
    """
    arg_names = ', '.join(args)

    data = {"code": "-9",
            "msg": f"[{arg_names}] 参数为空"
            }

    return jsonify(data)


@NaturalChan.route("/api/config")
def config():
    """
    配置信息
    """

    ret = {
        "supports_search": True,
        "supports_group_request": False,
        "supported_resolutions": ["1", "5",
                                  "30", "240", "1D",
                                  "1W", "1M"],
        "supports_marks": False,
        "supports_time": True,
        "sentsupports_timescale_marks": True,  # 使用自定义的时间范围
    }

    return jsonify(ret)


@NaturalChan.route('/api/search')
def search():
    """
    支持搜索的列表
    """
    query = request.args.get('query', 'all')
    if query == "all":
        return jsonify(SUPPORT_SYMBOLS)
    else:
        qre = '.*'.join([_ for _ in query])
        symbols = [_ for _ in SUPPORT_SYMBOLS if re.search(qre, _['name'])]
        return jsonify(symbols)

    # print(support_symbols)


@NaturalChan.route("/api/symbols")
def symbols():
    """
    获取币种，主要是能动态的支持搜索
    """
    symbol = request.args.get('symbol', 'BTC')

    for sym in SUPPORT_SYMBOLS:
        qre = '.*'.join([_ for _ in symbol])
        # print(qre)
        if re.search(qre, sym['name']):
            return sym

        if re.search(qre, sym['symbol']):
            return sym
    else:
        return {}


@NaturalChan.route("/api/history", methods=['GET'])
def history():
    """
    历史数据
    /history?symbol=<ticker_name>&from=<unix_timestamp>&to=<unix_timestamp>&resolution=<resolution>
    """
    symbol = request.args.get('symbol', 'BTC')
    from_ = int(request.args.get('from', None))
    to_ = int(request.args.get('to', None))
    resolution = request.args.get('resolution', 'D')

    tf = RESOU_DICT[resolution]

    db = HIST_DB
    conf_db = CONF_DB

    if re.match(r'\d{6}', symbol):
        # 股票的代码
        db = STOCK_DB
        symbol = f'stk_{symbol}'

    tf_sec = None
    if resolution in ('D', '1D'):
        tf_sec = 1440
    elif resolution == 'W':
        tf_sec = 1440 * 7
    else:
        tf_sec = resolution

    # 为回放设置的点
    col_replay = conf_db[f'replay_config']
    # 更新当前操作的币种和时间周期（为回测代码使用，作为前进的步伐依据）
    col_replay.replace_one({'current_symbol': {'$exists': True}},
                           {'current_symbol': symbol, 'current_tf': tf},
                           True)

    # 查找本周期最新的时间
    rep_ct = col_replay.find_one({'current_ts': {'$exists': 1}})

    # print(rep_ct)

    # 默认的2030-04-04
    current_ts = 1901523203
    if rep_ct:
        current_ts = rep_ct[f'ts_{tf}']

    # 把时间，只限制在回测的最后时间里面
    if to_ > current_ts or from_ > current_ts:
        to_ = current_ts
        from_ = to_ - int(tf_sec) * 60 * 2000

    _xfrom = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(int(from_)))
    _xto = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(int(to_)))

    # 整数的to_
    tf_sec = TF_SEC_MAP[tf]

    int_to_ = to_

    use_partial_k = False
    if current_ts % tf_sec != 0:
        use_partial_k = True

    # 当从小级别到大级别的时候，小级别的1分钟，刚好走到大级别的整数周期
    # 此时，大级别的周期实际上没有完，需要回退一个周期，再使用partial数据
    if rep_ct:
        ts_1m = rep_ct['ts_1m']
        if tf != '1m' and current_ts == ts_1m:
            use_partial_k = True

        # 只处理回测数据在from和to范围内，其他的数据正常处理即可
        if use_partial_k and from_ < current_ts <= to_:
            print('use partial')
            int_to_ = (current_ts // tf_sec - 1) * tf_sec

    col_tf = db[f'{symbol}_{tf}']

    res = col_tf.find({'ts': {'$gte': int(from_),
                              '$lte': int(int_to_)},
                       },
                      sort=[('ts', ASCENDING)]
                      )
    # pprint(list(res))
    res = list(res)

    """
    实现完全的线上回测效果
    以1分钟的数据为最小的；当小级别前进的时候，大级别也只走对应1分钟(部分K线)
    """
    if use_partial_k:
        col = db[f'{symbol}']
        print(current_ts)
        one_k = col.find_one({'ts': {'$eq': current_ts}, },
                             {'ts': True,
                              f'partial_open_{tf}': True,
                              f'partial_high_{tf}': True,
                              f'partial_low_{tf}': True,
                              f'partial_close_{tf}': True,
                              f'partial_volume_{tf}': True,
                              }
                             )

        if one_k:
            partial_kline = dict()
            partial_kline['ts'] = one_k['ts'] // tf_sec * tf_sec
            partial_kline['datetime'] = int2time(partial_kline['ts'])

            for _c in ('open', 'high', 'low', 'close', 'volume'):
                partial_kline[_c] = one_k[f'partial_{_c}_{tf}']

            res.append(partial_kline)

    last = col_tf.find_one(sort=[('ts', DESCENDING)])
    # print(last, type(last))
    lts = last['ts']

    print(f'GET DATA: [{symbol}] [{resolution}] [{_xfrom}] - [{_xto}], Length: {len(res)}, Latest: {lts}')
    print(f"db.{symbol}_{tf}.find({{'ts': {{'$gte': {from_}, '$lte': {to_} }} }})")

    if len(res) == 0:
        ret = {
            's': 'no_data',
            'nextTime': lts,
        }

        return ret

    ret = {
        's': 'ok',
        't': [int(_['ts']) for _ in res],
        'd': [_['datetime'] for _ in res],
        'o': [_['open'] for _ in res],
        'h': [_['high'] for _ in res],
        'l': [_['low'] for _ in res],
        'c': [_['close'] for _ in res],
        'v': [_['volume'] for _ in res],
    }

    return jsonify(ret)


@NaturalChan.route("/api/time", methods=['GET'])
def get_time():
    ts = str(arrow.get('2008-01-01').int_timestamp)

    return Response(ts)


@NaturalChan.route("/api/get_bspoint", methods=['GET'])
def get_bspoint():
    """获取买卖点
    """
    sym = request.args.get('symbol', 'btc')
    freq = request.args.get('resolution', '1')

    if sym in ('BTC', 'BHCoin'):
        sym = 'btc'

    if sym in ('SH',):
        sym = 'sh'

    freq = RESOU_DICT[freq]

    print(sym, freq)

    if freq == '1D':
        freq = '1440'
    elif freq == '1W':
        freq = '10080'

    bs_point = []
    with open(f'{DATA_PATH}/{sym}/bs-{freq}.csv') as f:
        for line in f:
            _, dt, bs_type = line.strip().split(',')
            bs_point.append({"dt": dt,
                             "bs_type": bs_type})

    ret = {'status': 'ok',
           'data': bs_point
           }

    return jsonify(ret)


@NaturalChan.route("/api/bzxd_mark", methods=['GET'])
def bzxd_mark():
    """
    线段的标记的点
    """
    mtype = request.args.get('mtype', 'zzk')
    sym = request.args.get('symbol', 'BTC')
    tf = request.args.get('tf', '1')

    tf = RESOU_DICT[tf]

    col = CHAN_DB[ESSENCE_XD_COL.format(sym=sym, tf=tf)]

    tf_sec = TF_SEC_MAP[tf]

    # 查找本周期最新的时间
    rep_ct = CONF_DB[f'replay_config'].find_one({'current_ts': {'$exists': True}})
    current_dt = int2time(rep_ct[f'ts_{tf}'] + tf_sec * 20)

    condit = None
    rcol = {'_id': False,
            'dt': True,
            }

    print(mtype)

    # if mtype == 'ma5ma34cross':
    #     condit = {'ma5ma34cross': {'$ne': '-'}, 'dt': {'$lte': current_dt}, }
    #     rcol['ma5ma34cross'] = True
    # # elif mtype == 'ma5_dg':
    # #     condit = {'ma5_dg': {'$ne': '-'}, 'dt': {'$lte': current_dt}, }
    # #     rcol['ma5_dg'] = True
    # elif mtype == 'xd_dg_comp':
    #     condit = {'xd_dg': {'$ne': '-'}, 'dt': {'$lte': current_dt}, }
    #     rcol['xd_dg'] = True

    data = list(col.find(condit, rcol))

    if mtype == 'zzk':
        data = list(col.find({'xddg_ind': {'$ne': {}},
                              'dt': {'$lte': current_dt},
                              },
                             {'_id': False, 'xddg_ind': True}
                             ))
        data = [_['xddg_ind'] for _ in data]
        data = [_['zzk'] for _ in data if _['xd_dg'] and _['xd_dg']['status'] in ('ok', 'merged', 'extended', 'divergence')]
    elif mtype == 'ma5_dg':
        data = list(col.find({'xddg_ind': {'$ne': {}},
                              'dt': {'$lte': current_dt},
                              },
                             {'_id': False, 'xddg_ind': True}
                             ))
        data = [_['xddg_ind'] for _ in data]
        data = [_['ma5'] for _ in data if _['xd_dg'] and _['xd_dg']['status'] in ('ok', 'merged', 'extended', 'divergence')]
    elif mtype == 'xd_dg':
        data = list(col.find({'xddg_ind': {'$ne': {}},
                              'dt': {'$lte': current_dt},
                              },
                             {'_id': False, 'xddg_ind': True}
                             ))
        data = [_['xddg_ind'] for _ in data]
        data = [_['xd_dg'] for _ in data if _['xd_dg'] and _['xd_dg']['status'] in ('ok', 'last')]
    elif mtype == 'xd_dg_extended':
        data = list(col.find({'xddg_ind': {'$ne': {}},
                              'dt': {'$lte': current_dt},
                              },
                             {'_id': False, 'xddg_ind': True}
                             ))
        data = [_['xddg_ind'] for _ in data]

        res = []
        for item in data:
            if item['xd_dg']['status'] in ('ok', 'last', 'extended', 'merged', 'divergence'):
                x = item['xd_dg']
                x['after_has_zs'] = item['has_zs']['after']
                x['before_has_zs'] = item['has_zs']['before']
                print(x)
                res.append(x)

        data = res

    elif mtype == 'kline_dg':
        data = list(col.find({'xddg_ind': {'$ne': {}},
                              'dt': {'$lte': current_dt},
                              },
                             {'_id': False, 'xddg_ind': True}
                             ))
        data = [_['xddg_ind'] for _ in data]
        data = [_['xd_dg'] for _ in data
                if _['xd_dg'] and _['xd_dg']['status'] in ('ok', 'merged', 'extended', 'divergence')]

    elif mtype == 'zs_line':
        res = list(col.find({'zs_line': {'$ne': {}},
                             'dt': {'$lte': current_dt},
                             },
                            {'_id': False, 'zs_line': True,
                             'dt': True,
                             'low': True,
                             'high': True,
                             }
                            ))
        data = []
        for item in res:
            _zsl = {'dt': item['dt'],
                    'low': item['low'],
                    'high': item['high'],
                    }
            _zsl.update(item['zs_line'])
            data.append(_zsl)

        print(data)
    elif mtype == 'xdzs':
        res = list(col.find({'xdzs': {'$ne': []},
                             'dt': {'$lte': current_dt},
                             },
                            {'_id': False, 'xdzs': True,
                             }
                            ))
        data = []

        pprint(data[:5])

        for item in res:
            xdzs_list = item['xdzs']
            for xdzs in xdzs_list:
                print(xdzs)
                if xdzs['status'] != 'ok':
                    continue
                xdzs['zstext'] = '/'.join([k for k, v in xdzs['zstype'].items() if v])
                data.append(xdzs)
    elif mtype == 'bspoint':
        col = CHAN_DB["bs_point_{sym}_{tf}".format(sym=sym, tf=tf)]
        res = list(col.find({}, {'_id': False}))
        data = res

    ret = {'status': 'ok',
           'data': data,
           }

    return jsonify(ret)


@NaturalChan.route("/api/bzzs_mark", methods=['GET'])
def bzzs_mark():
    """
    线段的标记的点
    """
    mtype = request.args.get('mtype', 'czxd_dg')
    sym = request.args.get('symbol', 'BTC')
    tf = request.args.get('tf', '1')

    tf = RESOU_DICT[tf]

    col = CHAN_DB[ESSENCE_XD_COL.format(sym=sym, tf=tf)]

    data = None

    if mtype == 'bzxd_zzk':
        data = list(col.find({'xddg_ind': {'$ne': {}}, },
                             {'_id': False, 'xddg_ind': True}
                             ))
        data = [_['xddg_ind'] for _ in data]
        pprint(data[:3])
        data = [_['bzxd_zzk'] for _ in data if _['xd_dg'] and _['xd_dg']['status'] in ('ok', 'last')]
    elif mtype == 'czxd_dg':
        data = list(col.find({'czxd_dg': {'$ne': {}}, },
                             {'_id': False, 'czxd_dg': True, 'dt': True,
                              'czxd_status': True,
                              }
                             ))

        dgs = [_['czxd_dg'] for _ in data]
        status = [_['czxd_status'] for _ in data]

        res = []
        for dg, st in zip(dgs, status):
            if st == 'ok':
                res.append(dg)
        # data = [_ for _ in data if _['value'] > 0 and _['status'] == 'ok']

        data = res
        print(data[:10])
    elif mtype == 'bzzs':
        res = list(col.find({'bzzs': {'$ne': {}}, },
                            {'_id': False, 'bzzs': True,
                             }
                            ))
        data = []
        for item in res:
            xdzs = item['bzzs']
            data.append(xdzs)
    elif mtype == '3_buysell':
        data = list(col.find({'3_buysell': {'$ne': {}}},
                             {'_id': False, '3_buysell': True, 'dt': True,
                              'high': True, 'low': True}
                             ))
        print('oolllllll')
        print(data)
    elif mtype == 'indp_cz':
        data = list(col.find({'czxd_dg': {'$ne': {}}, },
                             {'_id': False, 'czxd_dg': True, 'dt': True}
                             ))
        data = [_['czxd_dg'] for _ in data]
        data = [_ for _ in data if _['value'] > 0 and _['status'] == 'ok' and _['independent']]

        print(data[:10])

    ret = {'status': 'ok',
           'data': data,
           }

    return jsonify(ret)


@NaturalChan.route("/api/get_upper_fx", methods=['GET'])
def get_upper_fx():
    """
    upper fx
    """
    symbol = request.args.get('symbol', 'btc')
    resolution = request.args.get('resolution', '1')
    fx_jibie = request.args.get('fx_jibie', 'father')

    data, tf = None, None

    if fx_jibie == "father":
        if resolution in ('15', '30'):
            tf = RESOU_DICT['240']
        elif resolution == '240':
            tf = RESOU_DICT['1D']
        if resolution == '1D':
            tf = RESOU_DICT['1W']
    elif fx_jibie == "grandpa":
        # 股票就是这个
        if symbol in ('BTC', 'BHCoin'):
            if resolution in ('1', '5'):
                tf = RESOU_DICT['1D']
            elif resolution in ('15', '30'):
                tf = RESOU_DICT['1D']
            elif resolution == '240':
                tf = RESOU_DICT['1W']
        elif symbol in ('SH',):
            if resolution in ('1', '5'):
                tf = RESOU_DICT['1D']
            elif resolution in ('15', '30'):
                tf = RESOU_DICT['1W']

    col_tf = HIST_DB[f'{symbol}_{tf}']

    res = col_tf.find({},
                      sort=[('ts', ASCENDING)]
                      )
    # pprint(list(res))
    res = pd.DataFrame(list(res))

    _hist = res[-400:]

    data = []

    for row, next_row in zip(_hist[:-1].to_dict(orient='records'),
                             _hist[1:].to_dict(orient='records')):
        item = {'start_dt': row['datetime'],
                'end_dt': next_row['datetime'],
                'high': float(row['high']),
                'low': float(row['low']),
                }

        # # 股票里面的一天的开始和结束等
        # if symbol in ('SH',) and resolution in ('1', '5'):
        #     item['start_dt'] = item['start_dt'] + ' 09:31:00'
        #     item['end_dt'] = item['end_dt'] + ' 09:31:00'
        # elif symbol in ('SH',) and resolution in ('15', '30'):
        #     item['start_dt'] = item['start_dt'] + ' 09:30:00'
        #     item['end_dt'] = item['end_dt'] + ' 09:30:00'

        data.append(item)

    return jsonify({'status': 'ok', 'data': data})


app.register_blueprint(NaturalChan, url_prefix='')

if __name__ == '__main__':
    from flask_cors import *

    # app = Flask(__name__)
    CORS(app, supports_credentials=True)
    app.run(host='127.0.0.1', port=8421, debug=True)
