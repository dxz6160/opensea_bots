"""
url:https://opensea.io/collection/${COLLECTION_NAME}
"""

import sys
import os
sys.path.append('src/script')

from startV3 import start
parms = {
    'COLLECTION_NAME' : '''${COLLECTION_NAME}:${COLLECTION_NAME_}'''.replace(" ", "\ ").replace("'","\\'"),  # 集合名称:集合名称
    'MY_BEST_RATIO' : '${MY_BEST_RATIO}', # 计算比例
    'MY_BEST_WEIGHT' : '${MY_BEST_WEIGHT}', # 偏移量
    'COLLECTION_MARKUP' : '0.0001', # 提价幅度
    'TIME_GAP' : '1', # 间隔多久提交查询
    'STRATEGY_NAME' : os.path.split(sys.argv[0].strip(".py"))[-1] # 策略名 
}
start(parms)
