import os
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import random
import time
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.chrome.service import Service
import undetected_chromedriver as uc
from selenium.webdriver.chrome.options import Options

# ====== 新增 MetaMask 配置 ======
EXTENSION_PATH = os.path.expanduser('/home/fuckOpensea-main/resources/chrome/extension/nkbihfbeogaeaoehlefnkodbefgpgknn/12.16.0_0')
METAMASK_PASSWORD = "your_wallet_password"  # 使用环境变量更安全
WALLET_ADDRESS = "0xYourWalletAddress"
RECOVERY_PHRASE = "word1 word2 ... word12"  # 绝对不要硬编码在代码中！

# User-Agent列表（需定期更新）
USER_AGENT_LIST = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_5) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.5 Safari/605.1.15",
    # 添加更多UA...
]

# ChromeDriver路径（如果系统PATH已配置可留空）
CHROME_DRIVER_PATH = "/usr/local/bin/chromedriver"


class OpenSeaBrowserWithMetaMask:
    def __init__(self, max_retries=3):
        self.max_retries = max_retries
        self.driver = None

    # def _configure_browser(self):
    #
    #
    # # if USER_AGENT_LIST:
    # #         user_agent = random.choice(USER_AGENT_LIST)
    # #         options.add_argument(f'user-agent={user_agent}')

    def _init_driver(self):
        options = uc.ChromeOptions()

        # 加载 MetaMask 扩展
        if os.path.exists(EXTENSION_PATH):
            options.add_argument(f"--load-extension={EXTENSION_PATH}")
        else:
            raise FileNotFoundError("MetaMask 扩展目录不存在")
        options.add_argument("--disable-gpu")
        options.add_argument('--no-sandbox')  # 解决DevToolsActivePort问题
        options.add_argument('--disable-dev-shm-usage')  # 解决资源限制问题
        # options.add_argument('--headless')  # 无头模式，不显示浏览器窗口
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--window-size=1920,1080")
        options.add_argument('--private')
        if USER_AGENT_LIST:
                user_agent = random.choice(USER_AGENT_LIST)
                options.add_argument(f'user-agent={user_agent}')

        """初始化浏览器实例"""
        service = Service(executable_path=CHROME_DRIVER_PATH)
        driver = uc.Chrome(
            service=service,
            options=options,
            use_subprocess=True,
        )

        # 注入JavaScript修改navigator属性
        driver.execute_script(
            "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
        )
        return driver

    def _human_like_delay(self):
        """模拟人类操作延迟"""
        time.sleep(random.uniform(1.5, 5.0))  # 页面加载后随机等待
        if random.random() > 0.7:  # 30%概率添加额外延迟
            time.sleep(random.uniform(2, 8))

    def get_page(self, url, retry_count=0):
        """访问目标页面并处理异常"""
        try:
            if not self.driver:
                self.driver = self._init_driver()

            self.driver.get(url)
            self._human_like_delay()
            # time.sleep(1000)

            # 检查是否被拦截（示例检测逻辑）
            if "access denied" in self.driver.title.lower():
                raise WebDriverException("CloudFlare拦截检测")

            return self.driver.page_source

        except Exception as e:
            print(f"请求失败: {str(e)}")
            if retry_count < self.max_retries:
                print(f"尝试重试 ({retry_count + 1}/{self.max_retries})")
                self.driver.quit()
                self.driver = None
                return self.get_page(url, retry_count + 1)
            else:
                raise RuntimeError("超过最大重试次数")

    def close(self):
        """关闭浏览器实例"""
        if self.driver:
            self.driver.quit()

    def _switch_to_meta_mask_initialization(self):
        """处理首次安装后的初始化流程"""
        # 等待 MetaMask 弹窗出现
        time.sleep(3)
        self.driver.switch_to.window(self.driver.window_handles[-1])
        # if not self.driver:
        #     self.driver = self._init_driver()
        #
        # self.driver.get("chrome-extension://nkbihfbeogaeaoehlefnkodbefgpgknn/home.html")
        # time.sleep(1000)

        # extensions = self.driver.capabilities['chrome']['extensions']
        # print(extensions)
        # if not extensions:
        #     raise RuntimeError("没有检测到任何扩展加载")
        # for ext_id in extensions:
        #     try:
        #         self.driver.get(f'chrome-extension://{ext_id}/home.html')
        #         time.sleep(2)
        #         if "MetaMask" in self.driver.title:
        #             break
        #     except:
        #         continue
        time.sleep(5)
        print('1')
        # time.sleep(1000)
#
        try:
            # 点击 "Get Started"
            WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="app-content"]/div/div[2]/div/div/div/ul/li[1]/div/label/span/span"'))
            ).click()
            print('2')
            time.sleep(1000)

            # 选择导入钱包
            WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//button[text()='Import wallet']"))
            ).click()

            # 同意条款
            self.driver.find_element(By.XPATH, "//input[@type='checkbox']").click()
            self.driver.find_element(By.XPATH, "//button[text()='Import']").click()

            # 输入助记词
            words = RECOVERY_PHRASE.split()
            for i in range(12):
                field = self.driver.find_element(
                    By.XPATH, f"//input[@id='import-srp__srp-word-{i}']"
                )
                field.send_keys(words[i])

            # 设置密码
            password_field = self.driver.find_element(By.ID, "password")
            confirm_field = self.driver.find_element(By.ID, "confirm-password")
            password_field.send_keys(METAMASK_PASSWORD)
            confirm_field.send_keys(METAMASK_PASSWORD)

            # 完成导入
            self.driver.find_element(By.XPATH, "//button[text()='Import']").click()

            # 等待初始化完成
            WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.XPATH, "//div[@class='home__main-view']"))
            )

        except TimeoutException:
            print("MetaMask 初始化超时")

        # 切换回主窗口
        self.driver.switch_to.window(self.driver.window_handles[0])

    def _unlock_meta_mask(self):
        """解锁已存在的 MetaMask 钱包"""
        self.driver.switch_to.window(self.driver.window_handles[-1])

        try:
            password_field = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "password"))
            )
            password_field.send_keys(METAMASK_PASSWORD)

            self.driver.find_element(By.XPATH, "//button[text()='Unlock']").click()

            WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.XPATH, "//div[@class='home__main-view']"))
            )

        except TimeoutException:
            print("MetaMask 解锁失败")
        finally:
            self.driver.switch_to.window(self.driver.window_handles[0])

    def _handle_meta_mask_notification(self):
        """处理 DApp 连接请求"""
        if len(self.driver.window_handles) > 1:
            self.driver.switch_to.window(self.driver.window_handles[-1])
            try:
                # 点击确认连接
                WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[text()='Next']"))
                ).click()

                WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[text()='Connect']"))
                ).click()

            except Exception as e:
                print(f"处理连接请求失败: {str(e)}")
            finally:
                self.driver.switch_to.window(self.driver.window_handles[0])

    def connect_wallet_on_opensea(self):
        """在 OpenSea 执行钱包连接操作"""
        try:
            # 点击钱包连接按钮
            connect_btn = WebDriverWait(self.driver, 20).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Wallet')]"))
            )
            connect_btn.click()

            # 选择 MetaMask
            WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'MetaMask')]"))
            ).click()

            # 处理弹窗
            self._handle_meta_mask_notification()

            # 验证连接成功
            WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.XPATH, f"//div[contains(text(), '{WALLET_ADDRESS[-4:]}')]"))
            )
            print("钱包连接成功")

        except TimeoutException:
            print("钱包连接超时")


# ====== 使用示例 ======
if __name__ == "__main__":
    browser = OpenSeaBrowserWithMetaMask(max_retries=2)

    try:
        # 访问 OpenSea
        browser.get_page("https://opensea.io")

        # 解锁 MetaMask
        # browser._unlock_meta_mask()  # 注意：实际应使用更安全的方式管理密码
        browser._switch_to_meta_mask_initialization()

        # 执行钱包连接
        browser.connect_wallet_on_opensea()

        # 后续操作...

    except Exception as e:
        print(f"执行失败: {str(e)}")
    finally:
        browser.close()