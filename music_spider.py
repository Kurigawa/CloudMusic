from my_spider import Response
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from urllib.parse import urlparse
from selenium.webdriver import ActionChains
import pymongo
import json

def toplist():
# 查看榜单
    # 云音乐飙升榜  id=19723756
    # 云音乐新歌榜 id=3779629
    # 云音乐原创歌曲榜 id=2884035
    # 云音乐热歌榜 id=3778678
    print('请输入你想要查看的榜单：')
    l = input('1云音乐飙升榜\n2云音乐新歌榜\n3云音乐原创歌曲榜\n4云音乐热歌榜\n')
    name = '榜单'
    if l == '1':
        ID = 19723756
        name = '云音乐飙升榜'
    elif l == '2':
        ID = 3779629
        name = '云音乐新歌榜'
    elif l == '3':
        ID = 2884035
        name = '云音乐原创歌曲榜'
    elif l == '4':
        ID = 3778678
        name = '云音乐热歌榜'
    else:
        print('输入错误,程序退出')
        exit(1)
    url = 'https://music.163.com/discover/toplist?id=' + str(ID)
    Res = Response(url)
    res = Res.bs4_analytic()
    res1 = res.select('#song-list-pre-data ')[0].text
    # bs4解析,选择id为song-list-pre-data的标签,将列表中的第一个元素转换成文本
    L = []
    for i in json.loads(res1):
    # json解析获取的文本
        # print(i)
        data = {}
        # 构造字典,存放歌曲信息
        data['歌曲名'] = i['name']
        data['歌手'] = i['artists'][0]['name']
        m = int(i['duration'] / 1000 / 60)
        s = int(i['duration'] / 1000 % 60)
        data['时长'] = str(m) + ':' + str(s)
        if i['alias'] == []:
            i['alias'] = ['']
        # print(data)
        data['其他信息'] = i['alias'][0]
        L.append((data))
        print(data)
    print(L)
    Res.file_save_csv(f'{name}', L)
    client = pymongo.MongoClient('mongodb://localhost:27017')
    db = client.cloudmusic
    collection = db.song_info
    result = collection.insert(L)
    # 插入数据库
    exit(0)
def download():
# 利用浏览器搜索歌曲并下载
    word = input("请输入你要搜索的关键词：")
    browser = webdriver.Chrome()
    browser.get('https://music.163.com/')
    input1 = browser.find_element_by_class_name('j-flag')
    input1.clear()
    input1.send_keys(word)
    input1.send_keys(Keys.ENTER)
    # 搜索关键词
    browser.switch_to.frame('contentFrame')
    # 用frame的name定位
    song_list = []
    for i in range(5):
    # 下载页数,默认为5
        wait = WebDriverWait(browser, 60).until(EC.presence_of_element_located((By.CLASS_NAME, "srchsongst")))
        # 等待加载
        link = browser.find_elements_by_css_selector('div.text > a')
        # CSS定位
        lst = []
        for em in link:
            if 'song' in em.get_attribute('href'):
            # 获取href属性
                song = {}
                lst = urlparse(em.get_attribute('href'))  # 元组
                # 拆分链接
                print(lst[4])
                song['id'] = lst[4]
                # 取得歌曲id
                song['name'] = em.find_element_by_css_selector('b').text
                print(song['name'])
                # 获取歌曲名
                song_list.append(song)
                # 获取歌曲列表
            else:
                continue
        browser.execute_script('window,scrollTo(0,document.body.scrollHeight)')
        # 按钮会被底部播放栏挡住，所以移动至页面最底部
        botton = browser.find_element_by_class_name('znxt')
        ActionChains(browser).move_to_element(botton).click(botton).perform()
        # 模拟鼠标点击
    for song in song_list:
        url = 'https://music.163.com/song/media/outer/url?' + str(song['id']) + '.mp3'
        # print(url)
        response = Response(url)
        res = response.requests_req()
        # requests解析
        with open(f"{song['name']}.mp3", 'wb') as f:
            f.write(res.content)
            # 写入文件

if __name__ == "__main__":
    print('请选择功能：')
    f = input('1：查看榜单\n2：下载歌曲\n3：退出程序\n')
    while True:
        if f == '1':
            toplist()
        elif f == '2':
            download()
        elif f == '3':
            exit(0)
        else:
            print('输入错误，请重新输入。')
            f = input('1：查看榜单\n2：下载歌曲\n3：退出程序\n')
