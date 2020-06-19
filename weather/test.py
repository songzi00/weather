import requests
from bs4 import BeautifulSoup
import re,time,random
from setting.config import cursor,connect

# 构建useragnet列表
USER_AGENTS = [
    "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; AcooBrowser; .NET CLR 1.1.4322; .NET CLR 2.0.50727)",
    "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.0; Acoo Browser; SLCC1; .NET CLR 2.0.50727; Media Center PC 5.0; .NET CLR 3.0.04506)",
    "Mozilla/4.0 (compatible; MSIE 7.0; AOL 9.5; AOLBuild 4337.35; Windows NT 5.1; .NET CLR 1.1.4322; .NET CLR 2.0.50727)",
    "Mozilla/5.0 (Windows; U; MSIE 9.0; Windows NT 9.0; en-US)",
    "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Win64; x64; Trident/5.0; .NET CLR 3.5.30729; .NET CLR 3.0.30729; .NET CLR 2.0.50727; Media Center PC 6.0)",
    "Mozilla/5.0 (compatible; MSIE 8.0; Windows NT 6.0; Trident/4.0; WOW64; Trident/4.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; .NET CLR 1.0.3705; .NET CLR 1.1.4322)",
    "Mozilla/4.0 (compatible; MSIE 7.0b; Windows NT 5.2; .NET CLR 1.1.4322; .NET CLR 2.0.50727; InfoPath.2; .NET CLR 3.0.04506.30)",
    "Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN) AppleWebKit/523.15 (KHTML, like Gecko, Safari/419.3) Arora/0.3 (Change: 287 c9dfb30)",
    "Mozilla/5.0 (X11; U; Linux; en-US) AppleWebKit/527+ (KHTML, like Gecko, Safari/419.3) Arora/0.6",
    "Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.8.1.2pre) Gecko/20070215 K-Ninja/2.1.1",
    "Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN; rv:1.9) Gecko/20080705 Firefox/3.0 Kapiko/3.0",
    "Mozilla/5.0 (X11; Linux i686; U;) Gecko/20070322 Kazehakase/0.4.5",
    "Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.8) Gecko Fedora/1.9.0.8-1.fc10 Kazehakase/0.5.6",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.56 Safari/535.11",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_3) AppleWebKit/535.20 (KHTML, like Gecko) Chrome/19.0.1036.7 Safari/535.20",
    "Opera/9.80 (Macintosh; Intel Mac OS X 10.6.8; U; fr) Presto/2.9.168 Version/11.52",
]

# 获取8个区的链接
def get_city():
    url = 'http://www.weather.com.cn/textFC/db.shtml'
    headers = {"User-Agent": random.choice(USER_AGENTS)}    #随机获取user-agent
    res = requests.get(url, headers=headers)
    file = res.content.decode('utf-8')
    soup = BeautifulSoup(file, 'lxml')
    city_url = []
    urls = soup.select('.lq_contentboxTab2 > li > span > a')
    for url in urls:
        city_url.append('http://www.weather.com.cn' + url['href'])
    return city_url


# 获取每天的数据
def get_day(url):
    headers = {"User-Agent": random.choice(USER_AGENTS)}  # 随机获取user-agent
    res = requests.get(url, headers=headers)
    file = res.content.decode('utf-8')
    soup = BeautifulSoup(file, 'lxml')

    area = re.findall('textFC/(.*?).shtml',url)[0] #获取当前地区
    days = []

    # 遍历7天的数据
    days_div = soup.find_all('div',class_='conMidtab')
    for day in days_div:
        # 如气温数据不全，则跳过这天的数据爬取
        if day.select('.conMidtab2:nth-child(1) > table > tr:nth-child(3) > td:nth-child(5)')[0].get_text() == '-':
            print('-----此日期气温数据不全，已跳过此日期-----')

        else:
            #获取当天的日期，在数据库查询有无此日期，有便跳过，防止重复存入数据
            l_time = day.select('.conMidtab2:nth-child(1) > table > tr:nth-child(1) > td:nth-child(3)')[0].get_text()  # 获取月、日
            a_time = (re.findall(r'\((.*?)月(.*?)日\)', l_time))[0]  # 提取月与日的数字
            get_time = '2020-' + a_time[0] + '-' + a_time[1]

            sql = 'SELECT * FROM cweather WHERE get_time = %s AND area = %s'
            res = cursor.execute(sql, (
                get_time,
                area
            ))
            if(res):    #如果数据库有此日期，便跳过
                print('-----数据库已有{}地区{}的数据，已跳过此地区日期的数据爬取-----'.format(area,get_time))
            else:
                days.append(day)

    return days,area



def get_date(days,area):
    # 获取每天下面的表格
    province_tp = days.select('table')

    # 依次分析每个表格/省中每个城市的数据
    for pro in province_tp:
        province = pro.select('tr:nth-child(3) > td:nth-child(1) > a')[0].get_text() #获取省份

        l_time = pro.select('tr:nth-child(1) > td:nth-child(3)')[0].get_text()  # 获取月、日
        a_time = (re.findall(r'\((.*?)月(.*?)日\)', l_time))[0]  # 提取月与日的数字
        get_time = '2020-' + a_time[0] + '-' + a_time[1]

        city_list = pro.find_all('tr')[2:]
        count = 1
        try:
            for index, tr in enumerate(city_list):
                '''因为每个表格的第一行第一列为省，市在第二位，故需要特别判断一下'''
                if count == 1:
                    city = tr.find_all('td')[1].get_text()
                    city = city.replace('\n', '')

                    max_tp = tr.find_all('td')[4].get_text()
                    min_tp = tr.find_all('td')[7].get_text()
                else:
                    city = tr.find_all('td')[0].get_text()
                    city = city.replace('\n','')

                    max_tp = tr.find_all('td')[3].get_text()
                    min_tp = tr.find_all('td')[6].get_text()
                count += 1

                sql = 'insert into cweather(area,province,city,get_time,max_tp,min_tp) VALUES (%s,%s,%s,%s,%s,%s)'

                cursor.execute(sql, (
                    area,province,city,get_time,str(max_tp),str(min_tp)
                ))
                connect.commit()

                print('--------------mysql数据插入成功--------------------')
        except Exception as e:
            print(e)


if __name__ == '__main__':

    for url in get_city():
        area = get_day(url)[1]
        days = get_day(url)[0]
        for day in days:
            get_date(day,area)
            time.sleep(0.5)
        print('{}地区已爬取完毕'.format(area))

