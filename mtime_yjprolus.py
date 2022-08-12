# coding=utf-8
from gevent import monkey

monkey.patch_all()
import gevent, requests, bs4, csv
from gevent.queue import Queue

# 通过前端F12调试得到api接口，用requests的get方法获取数据并保存到JSON，便于后续解析和存取，再对数据进行解析合并
result = requests.get('http://front-gateway.mtime.com/library/index/app/topList.api?')
json_result = result.json()
print("-----用requests的get方法获取数据并保存到JSON-----")
tv_list = json_result['data']['tvTopList']['topListInfos'][0]['items']
url_list = []

# 遍历前一百个电视剧并保留到url_list中，便于后续获取对应影视的详细数据
for item in tv_list:
    item = 'http://front-gateway.mtime.com/library/movie/detail.api?&movieId={}&locationId=290'.format(item['itemId'])
    url_list.append(item)

# 根据提示对提供的headers进行解析并转换为字典存储
header_dict = {}
origin_headers = '''Accept:application/json, text/plain, */*
Accept-Encoding:gzip, deflate
Accept-Language:zh-CN,zh;q=0.9
Connection:keep-alive
Content-Type:application/json
Cookie:Hm_lvt_07aa95427da600fc217b1133c1e84e5b=1649125631; Hm_lpvt_07aa95427da600fc217b1133c1e84e5b=1649138436
Host:front-gateway.mtime.com
Origin:http://list.mtime.com
Referer:http://list.mtime.com/listIndex/
User-Agent:Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.25 Safari/537.36 Core/1.70.3877.400 QQBrowser/10.8.4506.400
X-Mtime-Wap-CheckValue:mtime'''

lines = origin_headers.split("\n")
for l in lines:
    key_value = l.split(":", 1)
    header_dict[key_value[0]] = key_value[1]

# header_dict = dict([l.split(": ", 1) for l in origin_headers.split("")]) 此方法有一定问题，故弃用

# 用Queue()创建队列
print("-----用Queue()创建队列，用put_nowait()储存数据-----")
work_queue = Queue()
# 遍历url列表，并将每个url放入队列，用put_nowait()储存数据
for url in url_list:
    work_queue.put_nowait(url)


# 定义爬虫函数，后面gevnet.spawm()函数需要用到
def crawler():
    # 当队列不是空时，执行
    while not work_queue.empty():
        # 用get_nowait()提取队列中的url
        url = work_queue.get_nowait()
        # 发送get请求抓取网址数据并保存为JSON格式便于后续数据处理
        result = requests.get(url, headers=header_dict).json()['data']['basic']
        # result = result.json()['data']['basic']
        actors = []
        directors = []
        for actor in result['actors']:
            if actor['name']:
                actors.append(actor['name'])
        for director in result['directors']:
            if director['name']:
                directors.append(director['name'])
        title = result['name']
        story = result['story']
        # 将四个关键数据title,directors,actors,story写入csv文件
        writerTop.writerow([title, directors, actors, story])


# csv文件写入
csv_top100 = open('time100.csv', 'w', newline='', encoding='gb18030')
writerTop = csv.writer(csv_top100)
writerTop.writerow(['剧名', '导演', '主演', '简介'])

# 创建一个空任务列表
todo_list = []

# 使用gevent实现多协程爬虫：创建4个爬虫，注意数量不能太多
for x in range(4):
    task = gevent.spawn(crawler)  # 使用gevnet.spawm()函数执行crawler()的任务
    todo_list.append(task)

gevent.joinall(todo_list)  # 调用gevent库里的joinall方法，启动执行所有的任务。
print("-----多协程爬虫任务全部执行完毕-----")
csv_top100.close()  # 关闭文件
print("-----csv文件写入完毕-----")
print('学号_姓名_Lab2-1 Mtime爬虫运行成功')
