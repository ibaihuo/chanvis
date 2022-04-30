#!/usr/bin/env bash

cmd_dir=../../../mgtools
data_dir=../../data

sym=000001.XSHG_1d

# # 导出股票示例数据(上证指数)
# ${cmd_dir}/mongodump -d stock -c stk_${sym} -o ${data_dir}
# ${cmd_dir}/mongodump -d stock -c replay_config -o ${data_dir}
# ${cmd_dir}/mongodump -d stock -c stock_names -o ${data_dir}

# # 导出缠论的分析结果(上证指数)
# ${cmd_dir}/mongodump -d nlchan -c essence_xd_${sym} -o ${data_dir}


# 导入数据
${cmd_dir}/mongorestore --nsInclude stock.stk_${sym} --drop ${data_dir}
${cmd_dir}/mongorestore --nsInclude stock.replay_config --drop ${data_dir}
${cmd_dir}/mongorestore --nsInclude stock.stock_names --drop ${data_dir}

# 导入缠论的分析结果(上证指数)
${cmd_dir}/mongorestore --nsInclude nlchan.essence_xd_${sym} --drop ${data_dir}
