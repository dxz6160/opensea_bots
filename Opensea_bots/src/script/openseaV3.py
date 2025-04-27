# Licensed to the Software Freedom Conservancy (SFC) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The SFC licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.

import time
import json
import os
import pandas as pd
import requests
import datetime
import traceback
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.support import expected_conditions
from selenium.common.exceptions import TimeoutException, WebDriverException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

from utils import Utils


class P1Error(BaseException):
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return self.msg


class P2Error(BaseException):
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return self.msg


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
        self.failNum = 0
        self.bidNum = 0
        self.env_dist = env_dist
        self.collectionName = env_dist.get("COLLECTION_NAME")
        self.collectionUrl = "https://opensea.io/collection/{0}".format(
            self.collectionName.split(":")[0])
        self.collectionApi = "https://api.opensea.io/api/v1/collection/{0}".format(
            self.collectionName.split(":")[0])
        self.setup_method(self.env_dist)

    def _get(self, url):
        self.driver.get(url)

    def setup_method(self, env_dist):
        # 插件配置
        profileDir = self.env_dist.get("PROFILE_FILE")
        profile = webdriver.FirefoxProfile(profileDir)
        profile.set_preference("permissions.default.image", 2)  # 禁用图片
        # Don't show thumbnails on not loaded images
        profile.set_preference(
            "browser.display.show_image_placeholders", False)
        # Don't show document colors.
        profile.set_preference("browser.display.use_document_colors", False)
        # Don't load document fonts.
        profile.set_preference("browser.display.use_document_fonts", 0)
        # Use system colors.
        profile.set_preference("browser.display.use_system_colors", True)
        # driver配置
        options = webdriver.FirefoxOptions()
        # 无头模式
        options.add_argument('--headless')
        # 无痕模式，清缓存
        options.add_argument('--private')
        # 初始化driver
        self.driver = webdriver.Firefox(
            firefox_profile=profile,
            executable_path=self.env_dist.get("FIREFOX_DRIVER"),
            options=options
        )
        self.driver.set_window_size(1920, 1080)

        # 初始化等待器
        self.wait = WebDriverWait(
            self.driver, int(self.env_dist.get("WAIT_TIME")), float(self.env_dist.get("CHECK_INTERVAL")))
        self.longWait = WebDriverWait(
            self.driver, int(30), float(self.env_dist.get("CHECK_INTERVAL")))
        self.longlongWait = WebDriverWait(
            self.driver, int(60), float(3))
        time.sleep(2)
        print("初始化浏览器✅")

    """
    关闭浏览器
    """

    def teardown_method(self):
        self.driver.quit()

    """
    清理窗口
    """

    def clear_windows(self):
        if self.driver != None:
            # 快照
            windows = self.driver.window_handles
            # 关闭全部窗口，除了第一个
            for window in windows[1:]:
                try:
                    self.driver.switch_to.window(window)
                    self.driver.close()
                except Exception as e:
                    pass
            # 切换到第一个窗口
            self.driver.switch_to.window(windows[0])

    """
    登陆metamask，输入钱包助记词
    """

    def verify_metamask(self, menmoicWord):
        self.driver.get(
            'moz-extension://38d67efb-5720-4c2e-8025-c5208d4202a0/home.html#initialize/create-password/import-with-seed-phrase')
        # 助记词输入
        menmoicWord = menmoicWord.split(" ")
        for x in range(0, len(menmoicWord)):
            # print(x,menmoicWord[x])
            self.wait.until(EC.visibility_of_element_located(
                (By.XPATH, '''//*[@id="import-srp__srp-word-{0}"]'''.format(x)))).send_keys(menmoicWord[x])

        # 密码输入
        self.driver.find_element(
            By.XPATH, '//*[@id="password"]').send_keys(self.env_dist.get('METAMASK_PASSWORD'))
        self.driver.find_element(
            By.XPATH, '//*[@id="confirm-password"]').send_keys(self.env_dist.get('METAMASK_PASSWORD'))

        # 勾选同意
        self.driver.find_element(
            By.XPATH, '//*[@id="create-new-vault__terms-checkbox"]').click()
        # 点击确定
        self.driver.find_element(
            By.XPATH, '//*[@id="app-content"]/div/div[2]/div/div/div[2]/form/button').click()
        # 确认完成
        self.wait.until(EC.visibility_of_element_located(
            (By.XPATH, '//*[@id="app-content"]/div/div[2]/div/div/button'))).click()
        print("激活钱包✅")

    """
    连接metamask到opensea，开始fuck
    """

    def connect_metamask_opensea(self):
        oldDriverHandle = self.driver.current_window_handle
        # 切换到opensea登陆窗口
        self.driver.switch_to.new_window()
        self._get('https://opensea.io/login?referrer=%2Faccount')
        # 判断是否已连接
        connectButton = self.wait.until(EC.visibility_of_element_located(
            (By.XPATH, "//*[text()='MetaMask']")), message="connect_opensea_metamask Timeout")
        #
        handlesSize = len(self.driver.window_handles)
        connectButton.click()
        self.wait.until(lambda x: len(self.driver.window_handles) == (
            handlesSize + 1), message="connect_opensea_metamask Timeout")
        self.driver.switch_to.window(self.driver.window_handles[-1])
        self.wait.until(EC.visibility_of_element_located(
            (By.XPATH, './/*[@id="app-content"]/div/div[2]/div/div[3]/div[2]/button[2]'))).click()
        self.wait.until(EC.visibility_of_element_located(
            (By.XPATH, '//*[@id="app-content"]/div/div[2]/div/div[2]/div[2]/div[2]/footer/button[2]'))).click()

        # 切换回初始窗口
        self.driver.switch_to.window(oldDriverHandle)
        time.sleep(2)
        print("连接opensea钱包✅")

    """
    获取我的报价列表
    """

    def my_offer_opensea(self):
        try:
            if datetime.datetime.now() > self.expireTime:
                self._get("https://opensea.io/account?tab=bids_made")
                # 抓取offer List
                bestOffer = 0
                expireTime = 0
                self.driver.implicitly_wait(2)
                # 等待第一个li出现，代表加载完成
                self.wait.until(EC.visibility_of_element_located((By.XPATH, '//*[@id="Body offer-search-1"]/div/div/div/div/ul/li[2]')))
                # 移动到table底部（需要30秒左右）
                js = '''document.evaluate('//*[@id="Body offer-search-1"]/div/div/div/div/ul', document).iterateNext().scrollIntoView(false)'''
                self.driver.execute_script(js)
                # 找到第一个item为止 或者找到“days” "hours"
                self.longlongWait.until(
                    lambda x : any(stopString in self.driver.find_element(By.XPATH, '//*[@id="Body offer-search-1"]/div/div/div/div/ul').get_attribute("textContent") for stopString in [self.collectionName.split(":")[1], "days", "hours"])
                    )
                # 获得table
                offerTable = self.driver.find_element(
                    By.XPATH, '//*[@id="Body offer-search-1"]/div/div/div/div/ul')
                res = Utils.tableCatcher(self.driver, offerTable)
                # print(res) # 原始表
                sortedTable = res[res["href"].str.contains('collection') & (res["Offer"] == self.collectionName.split(
                    ":")[1])].sort_values(by='Unit Price', ascending=False)
                # print(sortedTable) # 筛选+排序表
                bestOffer = sortedTable.iloc[0, 1].split(" ")[0]
                expireTime_ = sortedTable.iloc[0, 5].strip(" ")
                if "seconds" in expireTime_:
                    expireTime = 20
                elif "less than a minute" == expireTime_:
                    expireTime = 50
                elif "minutes" in expireTime_:
                    expireTime = float(expireTime_.split(" ")[-2]) * 60
                else:
                    expireTime = 3601
                self.expireTime = datetime.datetime.now() + datetime.timedelta(seconds=+(expireTime))
                self.myBestOffer = bestOffer

                self.log_cache.append("获取我的最佳报价✅:{0} 过期时间:{1} s".format(
                    self.myBestOffer, (self.expireTime - datetime.datetime.now()).seconds))
            else:
                self.log_cache.append("最佳报价未过期✅:{0} 过期时间:{1} s".format(
                    self.myBestOffer, (self.expireTime - datetime.datetime.now()).seconds))

        except IndexError as e:
            self.log_cache.append("无Offer")
            self.myBestOffer = 0.005
            self.expireTime = datetime.datetime.now() + datetime.timedelta(seconds=+(3601))
            self.log_cache.append(self.driver.find_element(By.XPATH, '//*[@id="Body offer-search-1"]/div/div/div/div/ul').get_attribute("textContent"))
            self.log_cache.append("获取offer信息:11——增加——>{}".format(self.driver.find_elements(By.XPATH, '//*[@id="Body offer-search-1"]/div/div/div/div/ul/li').__len__()))


        except TimeoutException as e:
            print("未挂底价OR超时:", e)
            self.log_cache.append("未挂底价OR超时❌:P-1")
            self.log_cache.append("获取offer信息:11——增加——>{}".format(self.driver.find_elements(By.XPATH, '//*[@id="Body offer-search-1"]/div/div/div/div/ul/li').__len__()))
            self.log_cache.append(self.driver.find_element(By.XPATH, '//*[@id="Body offer-search-1"]/div/div/div/div/ul').get_attribute("textContent"))
            raise P1Error("报价错误")

        except Exception as e:
            print("报价错误:", e)
            self.log_cache.append("获取报价失败❌:P-1")
            self.log_cache.append("获取offer信息:11——增加——>{}".format(self.driver.find_elements(By.XPATH, '//*[@id="Body offer-search-1"]/div/div/div/div/ul/li').__len__()))
            raise P1Error("报价错误")

    """
    报价策略
    """

    def offer_orcale(self):
        newBalance = float(format(float(self.newBalance), '.4f'))
        bestCollectionOffer = float(format(float(self.bestOffer), '.4f'))
        myBestOffer = float(format(float(self.myBestOffer), '.4f'))
        myBestOfferExpireTime = float(
            (self.expireTime - datetime.datetime.now()).seconds)

        timeGap = float(self.env_dist.get("TIME_GAP"))
        myHighestOffer = float(format(float(self.floorPrice) * float(self.env_dist.get(
            "MY_BEST_RATIO")) - float(self.env_dist.get("MY_BEST_WEIGHT")), '.4f'))
        markUp = float(
            format(float(self.env_dist.get("COLLECTION_MARKUP")), '.4f'))
        self.myHighestOffer = myHighestOffer
        self.log_cache.append("预期最高价格✅:{}".format(self.myHighestOffer))

        if bestCollectionOffer == myBestOffer:  # 如果市场最高价是我
            if myBestOfferExpireTime <= 120:  # 临近过期
                # res = bestCollectionOffer - 2 * markUp  # 尝试降价续单
                self.log_cache.append("最高价是我，且临近过期，放弃报价❌")
                res = 0
            else:
                self.log_cache.append("最高价是我❌")
                res = 0
        else:  # 市场最高价不是我
            if bestCollectionOffer <= myHighestOffer:  # 市场最高价小于我的最高定价
                # 出价为市场最高价+加价幅度
                res = bestCollectionOffer + markUp
            else:  # 市场最高价高于我的最高定价
                if myBestOffer < myHighestOffer:  # 我的当前价小于我的最高价
                    res = myHighestOffer
                elif myBestOffer > myHighestOffer:  # 我的当前价大于我的最高价
                    self.log_cache.append("超过预期❌")
                    res = 0
                else:  # 等于
                    if myBestOfferExpireTime <= 120:  # 过期时间单位为分钟 且 临近过期
                        res = myHighestOffer  # 续单
                    else:
                        self.log_cache.append("理论最高价❌")
                        res = 0
        if res > newBalance: # 余额不足
            if myBestOfferExpireTime <= 120 or myBestOffer > newBalance:  # 临近过期 或者 最好offer超过余额
                self.log_cache.append("余额不足❌:更新offer")
                res = newBalance
            else:
                self.log_cache.append("余额不足❌:保持offer")
                res = 0

        if (float(self.balance) != -1) and (float(self.balance) != float(newBalance)):  # 余额更新，刷新过期时间
            res = 0
            self.log_cache.append("余额更新❌")
            self.expireTime = datetime.datetime.now() + datetime.timedelta(hours=-1)

        res = format(res, '.4f')
        self.orcalePrice = res
        self.log_cache.append("最新报价✅:{} ".format(res))

    """
    挂单
    """

    def set_new_offer(self, expireTime=16):
        # 记录handles
        self.driver.switch_to.new_window()
        self._get(self.collectionUrl)
        oldDriverHandle = self.driver.current_window_handle
        handlesSize = len(self.driver.window_handles)
        # 进入页面

        # 获得页面地板价
        self.wait.until(EC.visibility_of_all_elements_located(
            (By.CSS_SELECTOR, ".Price--eth-icon")))
        collectionList = self.wait.until(
            EC.visibility_of_all_elements_located((By.CSS_SELECTOR, ".Asset--anchor")))
        priceList = []
        for collection in collectionList:
            try:
                if 'Price--eth-icon' in collection.find_elements(By.CSS_SELECTOR, '.Price--main')[0].find_element(By.CSS_SELECTOR, ' div > div > span').get_attribute('class'):
                    price = collection.find_elements(
                        By.CSS_SELECTOR, '.Price--amount')[0].get_attribute('textContent')
                    priceList.append(float(price))
            except:
                pass
        priceList.sort()
        self.floorPrice = priceList[0]
        self.log_cache.append("获取市场地板价✅:{}".format(self.floorPrice))

        # 点击make collection offer
        self.wait.until(EC.visibility_of_element_located(
            (By.XPATH, "//*[text()='Make collection offer']"))).click()
        time.sleep(1)

        # 如果需要点review-confirmation
        if self.driver.find_elements(By.CSS_SELECTOR, "#review-confirmation") != []:
            self.driver.find_elements(
                By.CSS_SELECTOR, "#review-confirmation")[0].click()

        # 获得Collection best Offer
        bestOffer = self.wait.until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, ".Price--isInline"))).get_attribute("textContent")
        self.bestOffer = bestOffer.split(" ")[0]
        self.log_cache.append("获取市场offer最高价✅:{}".format(self.bestOffer))

        # 等待余额检查
        self.wait.until(
            lambda x: self.driver.find_element(By.XPATH, "//section/div[2]/div[1]/div[2]/p").get_attribute("textContent") != 'Checking balance...')

        # 获得账户余额
        checkBalance = self.wait.until(
            EC.visibility_of_element_located((By.XPATH, "//section/div[2]/div[1]/div[2]/p"))).get_attribute("textContent").split(" ")[1]
        self.newBalance = checkBalance
        self.log_cache.append("获取余额✅:{}".format(self.newBalance))

        # 计算新报价
        return_msg = ""
        self.offer_orcale()
        self.balance = self.newBalance
        if float(self.orcalePrice) == 0:
            self.newOfferPrice = self.orcalePrice
            return_msg = "succ"
        else:
            # 设置offer价格
            self.wait.until(EC.visibility_of_element_located(
                (By.NAME, "pricePerUnit"))).click()
            self.driver.find_element(
                By.NAME, "pricePerUnit").send_keys(str(self.orcalePrice))

            # 设置过期时间(1day/2day/custom)
            self.wait.until(EC.visibility_of_element_located(
                (By.XPATH, '//section/div[2]/div[2]/div/div[2]/div[1]/div'))).click()
            li = self.wait.until(EC.visibility_of_all_elements_located(
                (By.XPATH, '//section/div[2]/div[2]/div/div[2]/div[1]/div[2]/div[1]/div[1]/div[1]/ul/li')))
            for l in li:
                if 'Custom' in l.get_attribute("innerHTML"):
                    l.click()

            # 点击时间栏按钮
            self.wait.until(EC.visibility_of_element_located(
                (By.XPATH, '//section/div[2]/div[2]/div/div[2]/div[2]/button'))).click()
            time.sleep(1)
            # 获取默认过期时间
            startTimePre = self.driver.find_element(
                By.XPATH, '//section/div[2]/div[2]/div/div[2]/div[2]/div[1]/input')
            timeObject = datetime.datetime.strptime(
                startTimePre.get_attribute("value").replace("T", " "), '%Y-%m-%d %H:%M')
            # 计算最小过期时间
            timeObjectDelta = timeObject + \
                datetime.timedelta(minutes=+(expireTime - 30))
            # 拿到过期时间Input窗口
            startTime = self.driver.find_element(By.ID, 'start-time')
            # 移动到时间Input窗口 点击
            ActionChains(self.driver).move_to_element(
                startTime).click().perform()
            time.sleep(1)
            # 填充过期时间
            # 确保没有跨天
            if timeObjectDelta.strftime('%Y%m%d') == timeObject.strftime('%Y%m%d'):
                startTime.send_keys(timeObjectDelta.strftime('%H:%M'))
            time.sleep(1)
            try:
                self.wait.until(EC.visibility_of_element_located(
                    (By.NAME, "pricePerUnit"))).click()
            except:
                pass
            time.sleep(1)

            # 点击Make Offer
            makeOfferButton = self.wait.until(EC.element_to_be_clickable(
                (By.XPATH, '//form/footer/button')))
            makeOfferButton.click()

            # 等待MetaMask弹出
            try:

                self.longWait.until(lambda x: len(self.driver.window_handles) == (
                    handlesSize + 1), message="connect_opensea_metamask Timeout")

                # 切换到小狐狸窗口
                self.driver.switch_to.window(self.driver.window_handles[-1])

                # 点击下滑按钮
                self.wait.until(EC.visibility_of_element_located(
                    (By.XPATH, '//*[@id="app-content"]/div/div[2]/div/div[3]/div[1]'))).click()

                # 点击签名按钮
                self.wait.until(EC.visibility_of_element_located(
                    (By.XPATH, '//*[@id="app-content"]/div/div[2]/div/div[4]/button[2]'))).click()
                self.driver.switch_to.window(oldDriverHandle)

                # 更新offer和过期时间
                self.myBestOffer = self.orcalePrice
                self.expireTime = datetime.datetime.now() + datetime.timedelta(minutes=+16)
                return_msg = "succ"

            except Exception as e:
                print("出价错误:", e)
                self.log_cache.append("小狐狸弹出超时❌:P-1")
                raise P1Error("出价错误")

        self.status = return_msg
