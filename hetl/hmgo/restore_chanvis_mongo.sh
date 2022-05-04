#!/usr/bin/env bash

# 修改mgtools的路径
# 如果没有，请去mongo官网下载对应的版本
cmd_dir=../../../mgtools
data_dir=../../data

# 上证指数（日线）
sym=000001.XSHG_1d

# ########################### 导出 ###########################
# # 导出股票示例数据(上证指数)
# ${cmd_dir}/mongodump -d stock -c stk_${sym} -o ${data_dir}
# ${cmd_dir}/mongodump -d config -c replay_config -o ${data_dir}
# ${cmd_dir}/mongodump -d stock -c stock_names -o ${data_dir}

# # 导出缠论的分析结果(上证指数)
# ${cmd_dir}/mongodump -d nlchan -c essence_xd_${sym} -o ${data_dir}



########################## 导入 ###########################
# 导入数据
${cmd_dir}/mongorestore --nsInclude stock.stk_${sym} --drop ${data_dir}
${cmd_dir}/mongorestore --nsInclude config.replay_config --drop ${data_dir}
${cmd_dir}/mongorestore --nsInclude stock.stock_names --drop ${data_dir}

# 导入缠论的分析结果(上证指数)
${cmd_dir}/mongorestore --nsInclude nlchan.essence_xd_${sym} --drop ${data_dir}
