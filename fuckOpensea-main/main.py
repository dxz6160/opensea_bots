import sys
import datetime
import os
import time
import schedule
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
import pandas as pd
from dotenv import find_dotenv, load_dotenv

load_dotenv(find_dotenv('.env'))
env_dist = os.environ

name1=sys.argv[1]
name2=sys.argv[2].replace('/', ' ')
ratio=sys.argv[3]
weight=sys.argv[4]
parms = {
    'COLLECTION_NAME' : '{}:{}'.format(name1,name2),  # 集合名称:集合名称
    'MY_BEST_RATIO' : ratio, # 计算比例
    'MY_BEST_WEIGHT' : weight, # 偏移量
}

'初始化浏览器'
class OfferBot:
    def __init__(self):
        self.initBot()

    def initBot(self):
        # 初始化 ✅
        self.fucker = FuckOpensea(env_dist)
        try:
            # 激活钱包(助记词) ✅
            self.fucker.verify_metamask(env_dist.get("MNEMONIC_WORD"))
            # 连接钱包 ✅
            self.fucker.connect_metamask_opensea()
        except Exception as e:
            self.fucker.teardown_method()
            sys.exit()

    def makeOffeForLoop(self):
        # 输出窗口
        try:
            # 查询offer
            self.fucker.my_offer_opensea()
            # 提交offer
            self.fucker.set_new_offer()
        except Exception as e:  # P-0:未知错误，中断运行
            self.killMyself()
        finally:
            self.fucker.clear_windows()

    def killMyself(self):
        print("未知错误，中断运行❌:P-0")
        self.fucker.teardown_method()
        sys.exit()


    # 任务计划
    def scheduleMakeOffer(self):
        self.makeOffeForLoop()
        print("开始循环")
        schedule.every(int(env_dist['TIME_GAP'])).minutes.do(self.makeOffeForLoop)
        while True:
            schedule.run_pending()
            time.sleep(1)


"""
$$$FUCK OF OPENSEA$$$
"""


class FuckOpensea:
    """
    初始化self变量
    """

    def __init__(self, env_dist):
        self.log_cache = []
        self.balance = -1
        self.myBestOffer = -1
        self.expireTime = datetime.datetime.now() + datetime.timedelta(hours=-1)
        self.env_dist = env_dist
        self.collectionName = parms['COLLECTION_NAME']
        self.collectionUrl = "https://opensea.io/collection/{0}".format(self.collectionName.split(":")[0])
        self.setup_method(self.env_dist)

    def _get(self, url):
        self.driver.get(url)

    def setup_method(self, env_dist):
        # 插件配置
        profileDir = self.env_dist.get("PROFILE_FILE")
        # driver配置
        options = Options()
        options.page_load_strategy = 'eager'
        # 无头模式
        # options.add_argument('--headless')
        # 无痕模式，清缓存
        # options.add_argument('--private')
        options.profile=profileDir
        options.set_preference('profile', profileDir)
        options.set_preference("permissions.default.image", 2)  # 禁用图片
        # Don't show thumbnails on not loaded images
        options.set_preference("browser.display.show_image_placeholders", False)
        # Don't show document colors.
        options.set_preference("browser.display.use_document_colors", False)
        # Don't load document fonts.
        options.set_preference("browser.display.use_document_fonts", 0)
        # Use system colors.
        options.set_preference("browser.display.use_system_colors", True)

        # 初始化driver
        self.driver = webdriver.Firefox(service=Service(self.env_dist.get("FIREFOX_DRIVER")),options=options)
        # 初始化等待器
        self.wait = WebDriverWait(self.driver, int(30), float(0.5))
        time.sleep(2)
        print("初始化浏览器✅")


    #关闭浏览器
    def teardown_method(self):
        self.driver.quit()

    #清理窗口
    def clear_windows(self):
        if self.driver != None:
            curWindow = self.driver.current_window_handle
            for window in self.driver.window_handles:
                if curWindow != window:
                    try:
                        self.driver.switch_to.window(window)
                        self.driver.close()
                    except Exception as e:
                        pass
            self.driver.switch_to.window(curWindow)

    #登陆metamask，输入钱包助记词
    def verify_metamask(self, menmoicWord):
        self.driver.get(
            'moz-extension://2f7d8212-142f-46a3-ad84-494532d6c46b/home.html#onboarding/welcome')
        time.sleep(1000)
        self.wait.until(EC.visibility_of_element_located(
            (By.XPATH, '//*[@id="onboarding__terms-checkbox"]')))
        # 勾选同意
        self.driver.find_element(
            By.XPATH, '//*[@id="onboarding__terms-checkbox"]').click()
        # 点击确定
        self.driver.find_element(
            By.XPATH, '/html/body/div[1]/div/div[2]/div/div/div/ul/li[3]/button').click()
        # 拒绝信息采集
        self.driver.find_element(
            By.XPATH, '/html/body/div[1]/div/div[2]/div/div/div/div[2]/button[1]').click()
        print('拒绝信息采集')
        # 助记词输入
        menmoicWord = menmoicWord.split(" ")
        for x in range(0, len(menmoicWord)):
            # print(x,menmoicWord[x])
            self.wait.until(EC.visibility_of_element_located(
                (By.XPATH, '''//*[@id="import-srp__srp-word-{0}"]'''.format(x)))).send_keys(menmoicWord[x])

        # 等待按钮变亮
        self.wait.until(EC.visibility_of_element_located(
            (By.XPATH, '/html/body/div[1]/div/div[2]/div/div/div/div[4]/div/button')))
        # 勾选Confirm Secret Recovery Phrase
        self.driver.find_element(
            By.XPATH, '/html/body/div[1]/div/div[2]/div/div/div/div[4]/div/button').click()
        print('Confirm Secret Recovery Phrase')

        # 密码输入
        self.driver.find_element(
            By.XPATH, '/html/body/div[1]/div/div[2]/div/div/div/div[2]/form/div[1]/label/input').send_keys(
            self.env_dist.get('METAMASK_PASSWORD'))
        self.driver.find_element(
            By.XPATH, '/html/body/div[1]/div/div[2]/div/div/div/div[2]/form/div[2]/label/input').send_keys(
            self.env_dist.get('METAMASK_PASSWORD'))
        print('密码输入')
        # time.sleep(1000)

        self.driver.find_element(
            By.XPATH, '/html/body/div[1]/div/div[2]/div/div/div/div[2]/form/div[3]/label/span[1]/input').click()
        # 点击确定
        self.driver.find_element(
            By.XPATH, '/html/body/div[1]/div/div[2]/div/div/div/div[2]/form/button').click()
        # 确认完成
        self.wait.until(EC.visibility_of_element_located(
            (By.XPATH, '/html/body/div[1]/div/div[2]/div/div/div/div[3]/button'))).click()
        self.wait.until(EC.visibility_of_element_located(
            (By.XPATH, '/html/body/div[1]/div/div[2]/div/div/div/div[2]/button'))).click()
        self.wait.until(EC.visibility_of_element_located(
            (By.XPATH, '/html/body/div[1]/div/div[2]/div/div/div/div[2]/button'))).click()
        print("激活钱包✅")
        time.sleep(1000)

    #连接metamask到opensea，开始fuck
    def connect_metamask_opensea(self):
        oldDriverHandle = self.driver.current_window_handle
        # 切换到opensea登陆窗口
        self.driver.switch_to.new_window()
        self._get('https://opensea.io/login?referrer=%2Faccount')
        # 判断是否已连接
        connectButton = self.wait.until(EC.visibility_of_element_located((By.XPATH, "//*[text()='MetaMask']")),message="connect_opensea_metamask Timeout")
        handlesSize = len(self.driver.window_handles)
        connectButton.click()
        time.sleep(1)
        self.wait.until(lambda x: len(self.driver.window_handles) == (handlesSize + 1), message="connect_opensea_metamask Timeout")
        self.driver.switch_to.window(self.driver.window_handles[-1])
        self.wait.until(EC.visibility_of_element_located((By.XPATH, './/*[@id="app-content"]/div/div[2]/div/div[3]/div[2]/button[2]'))).click()
        self.wait.until(EC.visibility_of_element_located((By.XPATH, '//*[@id="app-content"]/div/div[2]/div/div[2]/div[2]/div[2]/footer/button[2]'))).click()
        # 切换回初始窗口
        self.driver.switch_to.window(oldDriverHandle)
        time.sleep(2)
        print("连接opensea钱包✅")

    def tableCatcher(driver, table):
        # 获取行数，由于部分表格表头是用th而不是用td，可能会出现计算错误。因此这里先除去表头
        table_tr = table.find_elements(By.XPATH, 'li')
        row = len(table_tr)
        tableRes = [[x.get_attribute("textContent") for x in table_tr[0].find_elements(By.XPATH, './*')] + ['href']]
        if row > 1:
            for i in range(1, row):
                tableRes.append([x.get_attribute("textContent").strip() for x in table_tr[i].find_elements(By.XPATH, './*')] + [table_tr[i].find_element(By.XPATH, './div[1]//a').get_attribute("href")])
        res = pd.DataFrame(tableRes[1:], columns=tableRes[0])
        return res

    #获取我的报价列表
    def my_offer_opensea(self):
        Name = self.collectionName.replace(': ', '/').split(':')[1].replace("/", ": ")
        try:
            if datetime.datetime.now() > self.expireTime:
                self._get("https://opensea.io/account?tab=bids_made")
                # 抓取offer List
                bestOffer = 0
                expireTime = 0
                self.driver.implicitly_wait(2)
                # 等待第一个li出现，代表加载完成
                self.wait.until(EC.visibility_of_element_located((By.XPATH, '//*[@id="Body offer-search-1"]/div/div/div/div/ul/li[2]')))

                # 移动到table底部
                for i in range(6):  # 下滑6次
                    # 下滑
                    js = '''document.evaluate('//*[@id="Body offer-search-1"]/div/div/div/div/ul', document).iterateNext().scrollIntoView(false)'''
                    self.driver.execute_script(js)
                    time.sleep(1)
                self.wait.until(lambda x: any(stopString in self.driver.find_element(By.XPATH, '//*[@id="Body offer-search-1"]/div/div/div/div/ul').get_attribute("textContent") for stopString in [Name, "days", "hours"]))
                # 获得table
                offerTable = self.driver.find_element(By.XPATH, '//*[@id="Body offer-search-1"]/div/div/div/div/ul')
                res = self.tableCatcher(offerTable)
                try:
                    sortedTable = res[res["href"].str.contains('collection') & (res["Offer"] == Name)].sort_values(by='Unit Price', ascending=False)
                    bestOffer = sortedTable.iloc[0, 1].split(" ")[0]
                    expireTime_ = sortedTable.iloc[0, 5].strip(" ")
                    if "seconds" in expireTime_:
                        expireTime = 5
                    elif "a minute" == expireTime_:
                        expireTime = 30
                    elif "minutes" in expireTime_:
                        expireTime = float(expireTime_.split(" ")[-2]) * 60
                    else:
                        expireTime = 3601
                except Exception as e:
                    print('未挂底价，默认为0')
                self.expireTime = datetime.datetime.now() + datetime.timedelta(seconds=+int(expireTime))
                self.myBestOffer = bestOffer
                print(("获取我的最佳报价✅:{0} 过期时间:{1} s".format(self.myBestOffer, (self.expireTime - datetime.datetime.now()).seconds)))
            else:
                print("最佳报价未过期✅:{0} 过期时间:{1} s".format(self.myBestOffer, (self.expireTime - datetime.datetime.now()).seconds))
        except Exception as e:
            print("报价错误:", e)

    #报价策略
    def offer_orcale(self):
        newBalance = float(self.newBalance[:6])
        print('余额',newBalance)
        bestCollectionOffer = float(format(float(self.bestOffer), '.4f'))
        print('市场最高价',bestCollectionOffer)
        myBestOffer = float(format(float(self.myBestOffer), '.4f'))
        print('我的出价',myBestOffer)
        myBestOfferExpireTime = float((self.expireTime - datetime.datetime.now()).seconds)
        myHighestOffer = float(format(float(self.floorPrice) * float(parms["MY_BEST_RATIO"]) - float(parms["MY_BEST_WEIGHT"]), '.4f'))
        print('我的最高接受价格',myHighestOffer)
        markUp = float(format(float(self.env_dist.get("COLLECTION_MARKUP")), '.4f'))
        self.myHighestOffer = myHighestOffer

        if bestCollectionOffer == myBestOffer:  # 如果市场最高价是我
            res = 0
        else:  # 市场最高价不是我
            if bestCollectionOffer < myHighestOffer:  # 市场最高价小于我的最高定价
                # 出价为市场最高价+加价幅度
                res = bestCollectionOffer + markUp
                print('加价0.0001')
            else:  # 市场最高价高于我的最高定价
                if myBestOffer < myHighestOffer:  # 我的当前价小于我的最高价
                    res = myHighestOffer
                    print('拉满')
                elif myBestOffer > myHighestOffer:  # 我的当前价大于我的最高价
                    res = myHighestOffer
                    print("超过预期,回到接受最高价")
                else:  # 等于
                    if myBestOfferExpireTime <= 120:  # 过期时间单位为分钟 且 临近过期
                        res = myHighestOffer  # 续单
                        print('最高接受价续单')
                    else:
                        print("理论最高价挂单中")
                        res = 0
        if res > newBalance:  # 拦截余额不足
            print("余额不足")
            res = newBalance

        res = format(res, '.4f')
        self.orcalePrice = res
        print("最新报价✅:{} ".format(res))

    #挂单
    def set_new_offer(self, expireTime=16):
        # 记录handles
        self.driver.switch_to.new_window()
        # 进入页面
        self._get(self.collectionUrl)
        time.sleep(5)
        oldDriverHandle = self.driver.current_window_handle
        handlesSize = len(self.driver.window_handles)
        # 点击make collection offer
        self.wait.until(EC.visibility_of_element_located((By.XPATH, "//*[text()='Make collection offer']"))).click()
        time.sleep(10)

        # 如果需要点review-confirmation
        if self.driver.find_elements(By.CSS_SELECTOR, "#review-confirmation") != []:
            self.driver.find_elements(By.CSS_SELECTOR, "#review-confirmation")[0].click()

        content = self.wait.until(EC.visibility_of_element_located((By.XPATH, "//section/div[2]"))).get_attribute("textContent")
        div_num = 2
        if 'Choose an attribute' in content:
            div_num = 3

        floorPrice = self.wait.until(EC.visibility_of_element_located((By.XPATH, "//section/div[2]/div[{}]/ul/div[2]/div[2]/span".format(div_num)))).get_attribute("textContent")
        self.floorPrice = floorPrice.split(" ")[0]

        # 获得Collection best Offer
        bestOffer = self.wait.until(EC.visibility_of_element_located((By.XPATH, "//section/div[2]/div[{}]/ul/div[3]/div[2]/span".format(div_num)))).get_attribute("textContent")
        self.bestOffer = bestOffer.split(" ")[0]

        # 获得账户余额
        checkBalance = self.wait.until(EC.visibility_of_element_located((By.XPATH, "//section/div[2]/div[{}]/ul/div[1]/div[3]/span".format(div_num)))).get_attribute("textContent").split(" ")[0]
        self.newBalance = checkBalance

        # 计算新报价
        self.offer_orcale()
        self.balance = self.newBalance
        if float(self.orcalePrice) == 0:
            print('不用挂单')
        else:
            print('------------开始挂单----------------')
            # 设置offer价格
            print('设置offer价格')
            self.wait.until(EC.visibility_of_element_located((By.NAME, "pricePerUnit"))).click()
            self.driver.find_element(By.NAME, "pricePerUnit").send_keys(str(self.orcalePrice))

            # 设置过期时间(1day/2day/custom)
            self.wait.until(EC.visibility_of_element_located((By.XPATH, '//section/div[2]/div[{}]/div[1]/div[1]'.format(div_num + 1)))).click()
            li = self.wait.until(EC.visibility_of_all_elements_located((By.XPATH, '//section/div[2]/div[{}]/div[1]/div[2]/div[1]/div[1]/div[1]/ul/li'.format(div_num + 1))))
            for l in li:
                if 'Custom' in l.get_attribute("innerHTML"):
                    l.click()

            # 点击时间栏按钮
            self.wait.until(EC.visibility_of_element_located((By.XPATH, '//section/div[2]/div[{}]/div[2]/button'.format(div_num + 1)))).click()
            time.sleep(1)
            # 获取默认过期时间
            startTimePre = self.driver.find_element(By.XPATH, '//section/div[2]/div[{}]/div[2]/div[1]/input'.format(div_num + 1))
            timeObject = datetime.datetime.strptime(startTimePre.get_attribute("value").replace("T", " "), '%Y-%m-%d %H:%M')
            # 计算最小过期时间
            timeObjectDelta = timeObject + datetime.timedelta(minutes=+(expireTime - 30))
            # 拿到过期时间Input窗口
            startTime = self.driver.find_element(By.ID, 'start-time')
            # 移动到时间Input窗口 点击
            print('设置时间')
            ActionChains(self.driver).move_to_element(startTime).click().perform()
            time.sleep(1)
            # 填充过期时间
            # 确保没有跨天
            if timeObjectDelta.strftime('%Y%m%d') == timeObject.strftime('%Y%m%d'):
                startTime.send_keys(timeObjectDelta.strftime('%H:%M'))
            time.sleep(1)
            self.wait.until(EC.visibility_of_element_located((By.NAME, "pricePerUnit"))).click()
            time.sleep(1)

            # 点击Make Offer
            makeOfferButton = self.wait.until(EC.element_to_be_clickable((By.XPATH, '//form/footer/button')))
            makeOfferButton.click()

            # 等待MetaMask弹出
            try:
                self.wait.until(lambda x: len(self.driver.window_handles) == (handlesSize + 1), message="connect_opensea_metamask Timeout")
                # 切换到小狐狸窗口
                self.driver.switch_to.window(self.driver.window_handles[-1])
                # 点击下滑按钮
                self.wait.until(EC.visibility_of_element_located((By.XPATH, '//*[@id="app-content"]/div/div[2]/div/div[3]/div[1]'))).click()
                # 点击签名按钮
                self.wait.until(EC.visibility_of_element_located((By.XPATH, '//*[@id="app-content"]/div/div[2]/div/div[4]/button[2]'))).click()
                self.driver.switch_to.window(oldDriverHandle)
                # 更新offer和过期时间
                self.myBestOffer = self.orcalePrice
                self.expireTime = datetime.datetime.now() + datetime.timedelta(minutes=+16)
                print('------------------挂单成功-------------')

            except Exception as e:
                print("出价错误:", e)

if __name__ == '__main__':
    bot = OfferBot()
    bot.scheduleMakeOffer()

