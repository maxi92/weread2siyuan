import sys
import os
import pyperclip
from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QUrl
from PyQt5.QtCore import Qt
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEngineProfile
from wereader import *

# 微信读书用户id
USERVID = 0
# 文件路径
file=''
cookie_file = os.getcwd() + "\\temp\\cookie.txt"

class MainWindow(QMainWindow):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.DomainCookies = {}

        self.setWindowTitle('微信读书助手') # 设置窗口标题
        self.resize(900, 600) # 设置窗口大小
        self.setWindowFlags(Qt.WindowMinimizeButtonHint) # 禁止最大化按钮
        self.setFixedSize(self.width(), self.height()) # 禁止调整窗口大小

        url = 'https://weread.qq.com/#login' # 目标地址
        self.browser = QWebEngineView() # 实例化浏览器对象

        self.profile = QWebEngineProfile.defaultProfile()
        self.profile.cookieStore().deleteAllCookies() # 初次运行软件时删除所有cookies
        self.profile.cookieStore().cookieAdded.connect(self.onCookieAdd) # cookies增加时触发self.onCookieAdd()函数

        self.browser.loadFinished.connect(self.onLoadFinished) # 网页加载完毕时触发self.onLoadFinished()函数

        self.browser.load(QUrl(url)) # 加载网页
        self.setCentralWidget(self.browser) # 设置中心窗口


    # 网页加载完毕事件
    def onLoadFinished(self):
        print("onLoadFinished")
        global USERVID
        global headers
        global headers_p

        # 获取cookies
        cookies = ['{}={};'.format(key, value) for key,value in self.DomainCookies.items()]
        cookies = ' '.join(cookies)
        # 添加Cookie到header
        headers.update(Cookie=cookies)
        headers_p.update(Cookie=cookies)
        # 判断是否成功登录微信读书
        if login_success(headers):
            print("login success")
            #判断temp文件夹是否存在，不存在则创建
            temp_dir = os.getcwd() + "\\temp"
            if not os.path.exists(temp_dir):
                os.makedirs(temp_dir)
            #登录成功后写入cookie
            with open(cookie_file, 'w',encoding='utf-8') as f:
                f.write(cookies)
            print('登录微信读书成功!')
            # 获取用户user_vid
            if 'wr_vid' in self.DomainCookies.keys():
                USERVID = self.DomainCookies['wr_vid']
                print('用户id:{}'.format(USERVID))
                # 关闭整个qt窗口
                self.close()

        else:
            print("login failed")
            self.profile.cookieStore().deleteAllCookies()
            print('请扫描二维码登录微信读书...')

    # 添加cookies事件
    def onCookieAdd(self, cookie):
        # 打印cookie的name和value
        print("新增cookie")
        print(cookie.name().data().decode('utf-8'), cookie.value().data().decode('utf-8'))
        if 'weread.qq.com' in cookie.domain():
            name = cookie.name().data().decode('utf-8')
            value = cookie.value().data().decode('utf-8')
            if name not in self.DomainCookies:
                self.DomainCookies.update({name: value})

    # 窗口关闭事件
    def closeEvent(self, event):
        """
        重写closeEvent方法，实现窗体关闭时执行一些代码
        :param event: close()触发的事件
        :return: None
        """

        self.setWindowTitle('退出中……')  # 设置窗口标题
        self.profile.cookieStore().deleteAllCookies()

if __name__=='__main__':
    print(cookie_file)
    #cookie文件存在时尝试从文件中读取cookie登录
    if os.path.exists(cookie_file) and os.path.isfile(cookie_file):
        #读取
        with open(cookie_file,'r',encoding='utf-8') as f:
            cookie_in_file = f.readlines()
        #尝试登陆
        headers_from_file = headers
        headers_from_file.update(Cookie=cookie_in_file[0])
        if login_success(headers_from_file):
            print('登录微信读书成功!')
            #登录成后更新headers
            headers = headers_from_file
            headers_p.update(Cookie=cookie_in_file[0])
            #获取用户user_vid
            for item in cookie_in_file[0].split(';'):
                if item.strip()[:6] == 'wr_vid':
                    USERVID = int(item.strip()[7:])
        else:
            app = QApplication(sys.argv) # 创建应用
            window = MainWindow() # 创建主窗口
            window.show() # 显示窗口
            app.exec_() # 运行应用，并监听事件
    #文件不存在时再启用登录界面
    else:
        app = QApplication(sys.argv) # 创建应用
        window = MainWindow() # 创建主窗口
        window.show() # 显示窗口
        app.exec_() # 运行应用，并监听事件
    
    
    #将书架按{'bookId1':"title1"...}的形式储存在字典中
    bookId_dict = get_bookshelf(userVid=USERVID,list_as_shelf = False)
    print('**********************************************************')
    print_books_as_tree(userVid=USERVID)
"""     while True:
        print_books_as_tree(userVid=USERVID)
        #提示输入书本id，正确输入后进入主函数
        bookId = input('请输入书本ID：\n').strip()
        if bookId in bookId_dict.keys():
            y = main(bookId)
            if y == 0:
                break
            elif y == 1:
                continue """
                