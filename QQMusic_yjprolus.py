import csv, time, datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from lxml import etree  # 用于数据处理
import pandas as pd

# 主要爬取思路是通过xpath找到对应标签找到数据在对数据进行整理转化存入指定数据类型
chromedriver = webdriver.Chrome("D:\Program\chromedriver100.exe")
chromedriver.get("https://y.qq.com/")  # 打开QQ音乐首页进行爬取
# chromedriver.get("https://y.qq.com/n/ryqq/singer/001BLpXF2DyJe2") 也可以直接进入歌手界面进行对应标签的爬取

chromedriver.find_element(By.XPATH, "//*[@id='app']/div/div[1]/div/ul[2]/li[2]/a").click()  # 点击“歌手“
time.sleep(1)  # 歇个1-3秒防止页面未收到点击请求，后同

chromedriver.execute_script("window.scrollBy(0,500)")  # 调用JavaScript下拉加载详请并点击链接，后同
time.sleep(1)
chromedriver.switch_to.window(chromedriver.window_handles[-1])  # 切换至当前页面，执行下一步模拟点击操作，后同

print("-----选择歌手林俊杰进行爬取-----")
# 选择第一行第三个歌手林俊杰为本次爬取对象
chromedriver.find_element(By.XPATH, "//*[@id='app']/div/div[3]/div[2]/ul/li[3]/div/h3/a").click()
time.sleep(1)

chromedriver.execute_script("window.scrollBy(0,500)")
time.sleep(1)
chromedriver.switch_to.window(chromedriver.window_handles[-1])
main_handle = chromedriver.current_window_handle  # 获取当前页面句柄

print("-----歌手选择完毕，开始爬取前五首歌曲相关信息-----")
info = []
# 获取前五首歌曲相关信息
for order in range(1, 6):
    print("开始爬取第{}首歌曲".format(order))
    chromedriver.find_element(By.XPATH,
                              "//*[@id='app']/div/div[2]/div[2]/div[2]/ul[2]/li[{}]/div/div[2]/span/a".format(
                                  order)).click()  # 点击歌曲

    time.sleep(3)
    chromedriver.switch_to.window(chromedriver.window_handles[-1])
    chromedriver.execute_script("window.scrollBy(0,300)")
    time.sleep(1)

    # 歌名，前端F12调试找到对应元素为h1，并做好定位
    name = chromedriver.find_element(By.XPATH,
                                     "//*[@id='app']/div/div[2]/div[1]/div/div[1]/h1").text
    # 点击展开按钮便于爬取所有歌词
    chromedriver.find_element(By.XPATH, "//*[@id='app']/div/div[2]/div[2]/div[1]/div[1]/div[2]/a").click()
    lyrics = chromedriver.find_element(By.XPATH, "//*[@id='lrc_content']").text  # 歌词
    genre = chromedriver.find_element(By.XPATH, "//*[@id='app']/div/div[2]/div[1]/div/ul/li[3]").text.split("：")[
        1]  # 流派
    release_time = chromedriver.find_element(By.XPATH, "//*[@id='app']/div/div[2]/div[1]/div/ul/li[5]").text.split("：")[
        1]  # 发行时间
    comment_num = chromedriver.find_element(By.XPATH,
                                            "//*[@id='app']/div/div[2]/div[1]/div/div[3]/a[4]/span").text  # 评论个数

    basic_info = {'歌词': lyrics, '流派': genre, '发行日期': release_time, '评论个数': comment_num}  # 歌曲基本信息
    comment = []  # 评论列表
    # 下拉页面使其加载足够多的评论
    for i in range(35):
        chromedriver.execute_script("window.scrollBy(0,700+{}*220)".format(i))
        time.sleep(1)
    page_text = chromedriver.page_source
    tree = etree.HTML(page_text)
    c_list = tree.xpath("//*[@id='comment_box']/div[5]/ul/li")
    print("第{}首歌加载了{}条评论".format(order,len(c_list)))

    for i in range(500):
        li = c_list[i]
        comment_time = str(li.xpath("./div[1]/div[1]/text()")[0])
        if len(str(comment_time).split(" ")) == 1:
            current_time = datetime.datetime.now()
            comment_time = "{0}月{1}日 ".format(current_time.month, current_time.day) + str(
                li.xpath("./div[1]/div[1]/text()")[0])
        if len(li.xpath("./div[1]/div[2]/a[1]/text()")) != 0:
            like_num = eval(str(li.xpath("./div[1]/div[2]/a[1]/text()")[0]))
        else:
            like_num = 0

        comment_text = "".join(li.xpath("./div[1]/p/span//text()"))
        comment.append({'歌名': name, '评论时间': comment_time, '点赞数': like_num, '评论内容': comment_text})
    info.append([basic_info, comment])

    chromedriver.back()
    time.sleep(1)
    print("第{}首歌爬取完毕".format(order))
    chromedriver.switch_to.window(main_handle)  # 切换到上一个页面

print("-----即将关闭Chrome浏览器-----")
chromedriver.quit()  # 关闭Chrome浏览器

print("-----开始将爬取到的数据写入csv文件-----")
# 先用list将爬取到的数据存储起来并写入文件，保证数据能全部成功加载，将数据写入csv文件
csv_music = open("QQMusic.csv", 'w', encoding='utf-8-sig', newline='')
writer = csv.DictWriter(csv_music, ['歌词', '流派', '发行日期', '评论个数', '歌名', '评论时间', '点赞数', '评论内容'])
writer.writeheader()

for i in range(5):
    writer.writerow(info[i][0])
    writer.writerows(info[i][1])
csv_music.close()  # 完成csv文件写入
print("-----完成csv文件的写入-----")

# 统计每首歌曲的的评论的平均点赞数和标准差
print("-----开始进行相关数据的统计-----")
for i in range(5):
    like_num_list = []
    for j in info[i][1]:
        like_num_list.append(j['点赞数'])
    series = pd.Series(like_num_list)
    print("《" + info[i][1][0]['歌名'] + "》")
    print("平均点赞数:", series.mean())
    print("标准差：", series.var())

    # DataFrame分析评论数量与点赞数量的相关性
    comment_and_like = []
    for i in range(500):
        comment_and_like.append([i + 1, series[0:i + 1].sum()])
    df = pd.DataFrame(comment_and_like, columns=['评论数量', '点赞总数'])
    print("相关性：")
    print(df.corr())

print('学号_姓名_Lab2-2 QQ音乐爬虫运行成功')
