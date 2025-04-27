import numpy as np
import pandas as pd
import datetime
from string import Template
from pathlib import PurePosixPath, Path

def load_item_from_csv(path):
    tmp = pd.read_csv(path)
    res = tmp
    return res
res = load_item_from_csv('''/Users/wz/Downloads/项目列表-工作表1 (3).csv''')
# type(res)
temp = res.loc[2:]

templateFilePath = '''/Users/wz/Code/python/fuckOpensea/src/_missionTemplate/missionTemplate.tpl'''
baseOutPath = '''/Users/wz/Code/python/fuckOpensea/src/mission'''

for index, row in temp.iterrows():
    print(row[0],row[1],row[2],row[3],row[4],row[5],row[6])
    filename = row[1] + '.py'
    print(filename)
    level = "level_" + row[0]
    owner = "owner_" + row[6]
    
    print(PurePosixPath(baseOutPath).joinpath(level, owner, filename))
    tplFile = open(templateFilePath)
    Path(PurePosixPath(baseOutPath).joinpath(level, owner)).mkdir(parents=True, exist_ok=True)
    gFile = open(PurePosixPath(baseOutPath).joinpath(level, owner, filename), "w")

    lines = []
    tpl = Template(tplFile.read())

    lines.append(tpl.substitute(
        COLLECTION_NAME=row[1],
        COLLECTION_NAME_=row[2],
        MY_BEST_RATIO=row[3],
        MY_BEST_WEIGHT=row[4]))

    gFile.writelines(lines)
    tplFile.close()
    gFile.close()
    print('%s文件创建完成' % filename)