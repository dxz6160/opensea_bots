import os
import zmail
import time
import traceback
import pandas as pd
from selenium.webdriver.common.by import By
from dotenv import find_dotenv, load_dotenv
load_dotenv(find_dotenv('.env'))
env_dist = os.environ
class Utils():
    
    def prn_obj(obj): 
        print ('\n'.join(['%s:%s' % item for item in obj.__dict__.items()]))

    def mailSender(subject, context, screenShot):

        username = env_dist['MAIL_USERNAME'].split(",") # 'luzewei199@gmail.com', 
        password = env_dist['MAIL_PASSWORD'].split(",") # 'vnagkjycxjjyswaa'

        content_html = '''<html><p>{}</p><img src='data:image/png;base64,{}'/></html>'''.format('</p><p>'.join([str(x) for x in context]),screenShot)

        mail_info = {
            'subject': subject,  
            'content_html': content_html,
            'from': 'fuckOpensea<305670525@qq.com>'
        }
        size = len(username)
        while size:
            size -= 1
            time.sleep(1)
            _username = username.pop()
            _password = password.pop()
            print(_username)
            print(_password)
            try:
                mail_server = zmail.server(
                    _username,
                    _password
                )
                mail_server.send_mail(env_dist['MAIL_TO'].split(","), mail_info)
                print("邮件发送成功")
                break

            except Exception as e:
                traceback.print_exc()
                print("邮箱发送失败")

    def tableCatcher(driver, table):
        # 获取行数，由于部分表格表头是用th而不是用td，可能会出现计算错误。因此这里先除去表头
        table_tr = table.find_elements(By.XPATH, 'li')
        row = len(table_tr)
        # 获取列数
        cell = 0 if row == 0 else len(
            table_tr[0].find_elements(By.XPATH, './*'))
        #
        # print((row, cell))
        # print(table_tr[0].find_elements(By.XPATH, './*')[0].get_attribute("textContent"))
        tableRes = [[x.get_attribute("textContent") for x in table_tr[0].find_elements(
            By.XPATH, './*')] + ['href']]
        # print(tableRes)
        if row > 1:
            for i in range(1, row):
                # print(i)
                # print([x.get_attribute("href") for x in table_tr[i].find_elements(By.XPATH, './div[1]//a')])
                tableRes.append([x.get_attribute("textContent").strip() for x in table_tr[i].find_elements(By.XPATH, './*')] + [
                                table_tr[i].find_element(By.XPATH, './div[1]//a').get_attribute("href")])

        res = pd.DataFrame(tableRes[1:], columns=tableRes[0])

        return res

    def test():
        collectionName = "Bored Ape Yacht Club"
        tableRes = [
            ['Offer', 'Unit Price', 'USD Unit Price', 'Floor Difference',
                'From', 'Expiration', 'Made', 'Status', '', 'href'],
            ['Bored Ape Yacht Club', '0.003 WETH', '$5.11', '100% below', 'you', '3 days', '7 hours ago', 'Valid',
                'Cancel', 'https://opensea.io/assets/ethereum/0xbc4ca0eda7647a8ab7c2061c2e118a18a936f13d/8922'],
            ['Bored Ape Yacht Club '.strip(), '0.003 WETH', '$5.11', '100% below', 'you', 'about 17 hours',
             '7 hours ago', 'Valid', 'Cancel', 'https://opensea.io/collection/boredapeyachtclub'],
            ['Bored Ape Yacht Club '.strip(), '0.002 WETH', '$5.11', '100% below', 'you', 'about 17 hours',
             '7 hours ago', 'Valid', 'Cancel', 'https://opensea.io/collection/boredapeyachtclub'],
            ['Bored Ape Yacht Club '.strip(), '0.001 WETH', '$5.11', '100% below', 'you', 'about 17 hours',
             '7 hours ago', 'Valid', 'Cancel', 'https://opensea.io/collection/boredapeyachtclub'],
            ['Bored Ape Yacht Club '.strip(), '0.005 WETH', '$5.11', '100% below', 'you', 'about 17 hours',
             '7 hours ago', 'Valid', 'Cancel', 'https://opensea.io/collection/boredapeyachtclub'],
            ['Bored Ape Yacht Club '.strip(), '0.006 WETH', '$5.11', '100% below', 'you', 'about 17 hours',
             '7 hours ago', 'Valid', 'Cancel', 'https://opensea.io/collection/boredapeyachtclub'],
        ]

        res = pd.DataFrame(tableRes[1:], columns=tableRes[0])
        print(res)
        collectionOfferSort = res[res["href"].str.contains('collection') & (
            res["Offer"] == collectionName)].sort_values(by='Unit Price', ascending=False).iloc[0, 1].split(" ")[0]

        print(collectionOfferSort)
