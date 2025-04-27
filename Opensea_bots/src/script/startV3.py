import subprocess
import datetime
import os

def start(parms):
    
    # 获取脚本位置
    offerBotPath = os.path.abspath("src/script/offerBotV3.py")
    # 组装脚本

    cmdPre = 'nohup python3 -u {0} '.format(offerBotPath)
    cmdArgv = " ".join([
        parms['COLLECTION_NAME'],
        parms['MY_BEST_RATIO'], 
        parms['MY_BEST_WEIGHT'], 
        parms['COLLECTION_MARKUP'],
        parms['TIME_GAP']
        ])

    # log目录
    rootPath = "log"
    # 创建项目目录
    projectPath = rootPath + "/" + parms['COLLECTION_NAME'].replace("\ ", " ").replace("\\\'"," ") + "/" + parms['STRATEGY_NAME']
    if os.path.exists(projectPath):
        pass
    else:
        os.makedirs(projectPath)

    output = ('{0}/{1}'.format(projectPath.replace(" ", "\ "), str(datetime.datetime.now()).replace(" ", "\ ")))
    outputPid = output + "PID"
    cmdOutput = ' > {0}.log & echo $! > {1}.log 2>&1 &'.format(output, outputPid)
    cmdStr = "".join([
        cmdPre,
        cmdArgv, 
        cmdOutput])
    print(cmdStr)
    pp = subprocess.Popen(cmdStr, shell=True)
    print("fpid: ", pp.pid)