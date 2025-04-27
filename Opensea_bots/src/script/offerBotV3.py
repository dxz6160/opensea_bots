import os
import sys
import time
import datetime
import schedule
import traceback
import random
from utils import Utils
from openseaV3 import FuckOpensea, P1Error, P2Error
from selenium.common.exceptions import TimeoutException, WebDriverException
from urllib3.exceptions import MaxRetryError

from dotenv import find_dotenv, load_dotenv
load_dotenv(find_dotenv('.env'))
env_dist = os.environ

'初始化浏览器'
class OfferBot:
    def __init__(self):
        self.initBot()

    def initBot(self):
        n = float(env_dist['RETRY_WHEN_VERITY_FAIL'])
        while n:
            # 初始化 ✅
            self.fucker = FuckOpensea(env_dist)
            n -= 1
            try:
                # 激活钱包(助记词) ✅
                self.fucker.verify_metamask(env_dist.get("MNEMONIC_WORD"))
                # 连接钱包 ✅
                self.fucker.connect_metamask_opensea()
                break
            except Exception as e:
                traceback.print_exc()
                self.fucker.teardown_method()
                # self.fucker.driver = None
                print("n:{0}:{1}".format(n, e))
                if n == 0:
                    print("无法完成初始化❌")
                    self.snapshotStatus()
                    self.fucker.teardown_method()
                    sys.exit()
        

    def makeOffeForLoop(self):
                
        # 重置log_cache
        self.fucker.log_cache = []
        # 输出开始时间
        print("startTime:", datetime.datetime.now())
        # 输出窗口
        print(self.fucker.driver.window_handles)
        try:
            # 查询offer
            self.fucker.my_offer_opensea()
            # 提交offer
            self.fucker.set_new_offer()

        except P1Error as e:  #P-1:错误，重启浏览器
            print("重启❌:P-1")
            self.fucker.log_cache.append("重启❌:P-1")
            self.snapshotStatus()
            self.fucker.teardown_method()
            self.initBot()

        except TimeoutException as e:  #P-2:超时错误，进行下一轮
            print("超时❌:P-2")
            self.fucker.log_cache.append("超时❌:P-2")
            self.snapshotStatus()
            
        except WebDriverException as e:
            if 'Reached error page' in str(e):
                print("WebDriverException❌:P-2")
                self.fucker.log_cache.append("WebDriverException❌:P-2")
                self.snapshotStatus()
                # 随机睡眠一段时间
                time.sleep(random.randint(60,240))
            else:
                self.killMyself()
                
                
        except MaxRetryError as e:
            if 'Max retries exceeded with url' in str(e):
                print("MaxRetryError❌:P-2")
                self.fucker.log_cache.append("MaxRetryError❌:P-2")
                self.snapshotStatus()
                # 随机睡眠一段时间
                time.sleep(random.randint(60,240))
            else:
                self.killMyself()
        

        except Exception as e: #P-0:未知错误，中断运行
            self.killMyself()

        finally:
            # 记录窗口
            self.fucker.log_cache.append(self.fucker.driver.window_handles)
            # 记录时间
            self.fucker.log_cache.append("endTime:{}".format(str(datetime.datetime.now())))
            # 输出记录
            for x in self.fucker.log_cache:
                print(x)
            # Utils.prn_obj(self.fucker)
            # 清理窗口
            self.fucker.clear_windows()
            #
            print("清理窗口✅")
            print("")


    def killMyself(self):
            print("未知错误，中断运行❌:P-0")
            self.fucker.log_cache.append("未知错误，中断运行❌:P-0")
            self.snapshotStatus()
            self.fucker.teardown_method()
            sys.exit()
    
    # 快照状态
    def snapshotStatus(self):
        # 记录链接
        self.fucker.log_cache.insert(0, self.fucker.collectionUrl)
        # 记录错误
        self.fucker.log_cache.append(traceback.format_exc())
        # self.fucker.log_cache.append(['%s:%s' % item for item in self.fucker.__dict__.items()])
        # 构造邮件标题
        mailSubject = '任务({0}:{1})失败❌:{2}'.format(os.getenv("USER"), str(os.getpid()), self.fucker.collectionName)
        # 截图
        try:
            screenShot = self.fucker.driver.get_full_page_screenshot_as_base64()
        except Exception as e:
            screenShot = "0x"
        # 发送邮件
        Utils.mailSender(mailSubject, self.fucker.log_cache, screenShot)

    
    # 任务计划 
    def scheduleMakeOffer(self):
        self.makeOffeForLoop()
        schedule.every(float(sys.argv[5])).minutes.do(self.makeOffeForLoop)
        while True:
            schedule.run_pending()
            time.sleep(1)
        print("定时任务退出🚔:")



print("startTime:", datetime.datetime.now())
env_dist['COLLECTION_NAME'] = sys.argv[1]
env_dist['MY_BEST_RATIO'] = sys.argv[2]
env_dist['MY_BEST_WEIGHT'] = sys.argv[3]
env_dist['COLLECTION_MARKUP'] = sys.argv[4]
env_dist['TIME_GAP'] = sys.argv[5]

bot = OfferBot()
if bot.fucker.driver == None:
    print("任务失败❌:无法配置钱包")
    exit()
else:
    bot.scheduleMakeOffer()