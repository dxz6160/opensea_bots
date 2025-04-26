import re
import sys
from subprocess import PIPE, Popen, call

print('\033[0;37;43m==>>>> FUCK <<<<==\033[0m')
PID = sys.argv[1]
print('PID: ', PID)
CMD1 = 'ps ajx {}'.format(PID)
print('CMD1: ', CMD1)

# 返回的是 Popen 实例对象
proc = Popen(
    CMD1,  # cmd特定的查询空间的命令
    stdin=None,  # 标准输入 键盘
    stdout=PIPE,  # -1 标准输出（演示器、终端) 保存到管道中以便进行操作
    stderr=PIPE,  # 标准错误，保存到管道
    shell=True)
outinfo, errinfo = proc.communicate()
# print(outinfo.decode('gbk'))  # 外部程序(windows系统)决定编码格式
# print(errinfo.decode('gbk'))

outinfoDetails = outinfo.decode('gbk').split("\n")
# print(outinfoDetails)
if len(outinfoDetails) == 3:
    MISSION = outinfoDetails[1].split("offerBotV2.py ")[-1].split(":")[0]
    print('MISSION: ', MISSION)
    PGID = re.split(r'[ ]+', outinfoDetails[1])[3]
    print('PGID: ', PGID)
    CMD2 = 'kill -SIGTERM -- -{}'.format(PGID)
    print('CMD2: ',CMD2)
    call(CMD2.split(" "))
    print('\033[0;37;42m==>>>> SUCC <<<<==\033[0m')
else:
    print('\033[0;37;41m==>>>> FAIL <<<<==\033[0m')
    