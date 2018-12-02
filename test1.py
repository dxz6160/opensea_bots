import requests
import pymysql
import time
from lxml import etree
import re

conn = pymysql.connect(host='localhost', user='root', passwd='123456', db='db', port=3306, charset='utf8')
cursor = conn.cursor()

count = 1

headers = {
    'Cookie': 'll="108301"; ap_v=0,6.0; bid=gx8Pgt26ozY; report=ref=%2F&from=mv_a_pst; _pk_ref.100001.4cf6=%5B%22%22%2C%22%22%2C1543054968%2C%22https%3A%2F%2Fwww.so.com%2Fs%3Fie%3Dutf-8%26src%3Dhao_360so_a1004%26shb%3D1%26hsid%3D2fa4fa3d240d9f83%26q%3Ddouban%22%5D; _pk_id.100001.4cf6=6b22a05fcf758b56.1543054968.1.1543054968.1543054968.; _pk_ses.100001.4cf6=*; __yadk_uid=w3m6QUUrJstuAVkCMjo7ptd2JKYYVSmx',
    'Host': 'movie.douban.com',
    'Referer': 'https://movie.douban.com',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.140 Safari/537.36 Edge/17.17134'
}

def get_url():
    sql = 'SELECT movie_link FROM `movies_copy1_copy3`'
    try:
        cursor.execute(sql)
        result = cursor.fetchall()
        for url in result[0:25]:
            get_info(url[0])
            time.sleep(1)
    except:
        print('error')

def get_info(url):
    global count
    try:
        html = requests.get(url, headers=headers)
        if html.status_code == 404:
            print('网页不存在')
            cursor.execute("UPDATE movies_copy1_copy3 SET name= '%s' WHERE id= %s" % ('网页不存在', count))
        else:
            selector = etree.HTML(html.text)
            name = selector.xpath('//*[@id="content"]/h1/span[1]/text()')[0]
            name = name.replace('\'', '‘')
            if 'directedBy' in html.text:
                directors = selector.xpath('//*[@id="info"]/span[1]/span[2]/a/text()')
                director = ''
                for director_1 in directors:
                    director = director + director_1 + ' '
                director = director.replace('\'', '‘')
            else:
                director = '导演不存在'
            if 'class=\'pl\'>编剧' in html.text and director != '导演不存在':
                screenwrites = selector.xpath('//*[@id="info"]/span[2]/span[2]')[0]
                screenwrite = screenwrites.xpath('string(.)')
                screenwrite = screenwrite.replace('\'', '‘')
            elif 'class=\'pl\'>编剧' in html.text and director == '导演不存在':
                screenwrites = selector.xpath('//*[@id="info"]/span[1]/span[2]')[0]
                screenwrite = screenwrites.xpath('string(.)')
                screenwrite = screenwrite.replace('\'', '‘')
            else:
                screenwrite = '编剧不存在'
            if 'class=\'pl\'>主演' in html.text and screenwrite != '编剧不存在' and director != '导演不存在':
                actors = selector.xpath('//*[@id="info"]/span[3]/span[2]')[0]
                actor = actors.xpath('string(.)')
                actor = actor.replace('\'', '‘')
            elif ('class=\'pl\'>主演' in html.text and screenwrite == '编剧不存在' and director != '导演不存在') or (
                    'class=\'pl\'>主演' in html.text and screenwrite != '编剧不存在' and director == '导演不存在'):
                actors = selector.xpath('//*[@id="info"]/span[2]/span[2]')[0]
                actor = actors.xpath('string(.)')
                actor = actor.replace('\'', '‘')
            elif 'class=\'pl\'>主演' in html.text and screenwrite == '编剧不存在' and director == '导演不存在':
                actors = selector.xpath('//*[@id="info"]/span[1]/span[2]')[0]
                actor = actors.xpath('string(.)')
                actor = actor.replace('\'', '‘')
            else:
                actor = '主演不存在'
            types = re.findall('<span property="v:genre">(.*?)</span>', html.text, re.S)
            type_new = ''
            for type in types:
                type_new = type_new + type + '/'
            if '制片国家' in html.text:
                country = re.findall('制片国家/地区:</span>(.*?)<br/>', html.text, re.S)[0]
            else:
                country = '没有制片国家'
            if 'class="pl">语言:' in html.text:
                language = re.findall('语言:</span>(.*?)<br/>', html.text, re.S)[0]
                language = language.replace('\'', '‘')
            else:
                language = '没有语言'
            if ('上映日期:' or '首播:') in html.text:
                release_time = re.findall('<span property="v:initialReleaseDate.*?>(.*?)</span>', html.text, re.S)
                thetime = ''
                for release in release_time:
                    thetime = thetime + release + '/'
                thetime = thetime.replace('\'', '‘')
            else:
                thetime = '没有上映日期'
            if '片长:' in html.text:
                if 'runtime' in html.text:
                    time = re.findall('片长:</span>.*?>(.*?)</span>', html.text, re.S)[0]
                    time = time.replace('\'', '‘')
                else:
                    time = re.findall('片长:</span>(.*?)<br/>', html.text, re.S)[0]
                    time = time.replace('\'', '‘')
            else:
                time = '片长不存在'
            if 'IMDb链接:' in html.text:
                IMDb = re.findall('MDb链接:</spa.*?href="(.*?)" target', html.text, re.S)[0]
            else:
                IMDb = '没有IMDb链接'
            if '暂无评分' in html.text:
                score = '暂无评分'
            elif '豆瓣评分' in html.text:
                score = re.findall('<strong class="ll rating_num" property="v:average">(.*?)</strong>', html.text, re.S)[0]
            else:
                score = '没有评分'
            if 'summary' in html.text:
                info_2 = selector.xpath('//span[@property="v:summary"]/text()')
                str = ''
                for info in info_2:
                    info1 = info.strip(r'\n                                \u3000\u3000')
                    info2 = info1.strip()
                    str = str + info2
                str = str.replace('\'', '‘')
                str = str.replace('\\', '')
            else:
                str = ''
            print(count)
            print(name)
            cursor.execute(
                "UPDATE movies_copy1_copy3 SET name = '%s',director = '%s',screenwriter = '%s',actor = '%s',style = '%s',production = '%s',language = '%s',thetime = '%s',time = '%s',IMDb = '%s',socre = '%s',intro = '%s' WHERE id= %d" % (
                name, director, screenwrite, actor, type_new, country, language, thetime, time, IMDb, score, str,
                count))
        print('写入成功',count,'条')
        count += 1
        conn.commit()
    except:
        print('出错')
        print(count, '无法写入')
        count += 1



if __name__ == '__main__':
    # url = 'https://movie.douban.com/subject/1291830/'
    # get_info(url)
    get_url()
    conn.commit()
    conn.close()


