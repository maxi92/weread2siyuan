import sys
import os
import pyperclip
from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QUrl
from PyQt5.QtCore import Qt
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEngineProfile
from wereader import *
from siyuan import *

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

"""获取标注(md)"""
def get_mark(bookId):
    res = ''
    res = get_bookmarklist(bookId,is_all_chapter = 0)
    #没有标注时给出提示
    if res.strip() == '':
        print('无标注')
    return res

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
    """     bookId_dict = get_bookshelf(userVid=USERVID,list_as_shelf = False)
    print('**********************************************************')
    print_books_as_tree(userVid=USERVID)
    bookId = '3300026067';
    res = get_mark(bookId);
    if res != None:
        print(res); 
    """

    sorted_chapters,sorted_contents = getChaptersAndContents('3300026067')
    res = generate_markdown(sorted_chapters,sorted_contents,is_all_chapter=0);
    print(res)

    # 查找是否存在笔记本，若不存在则创建
    notebook_id = get_notebook_id_by_name()
    if not notebook_id:
        notebook_id = create_notebook()
        if not notebook_id:
            print("无法创建笔记本")
            sys.exit(0)

    # 指定标题
    title = "测试文档123"

    # 查找是否存在指定标题的笔记
    doc_info = search_docs_by_title(title)
    if doc_info:
        path = doc_info.get("path")
        box = doc_info.get("box")
        if path and box == notebook_id:
            # 删除该笔记
            remove_success = remove_doc(notebook_id, path)
            if remove_success:
                print(f"成功删除笔记: {title}")
            else:
                print(f"删除笔记失败: {title}")
        else:
            print(f"未找到笔记ID: {title}")
    else:
        print(f"未找到笔记: {title}")

    # 创建一个名称为指定标题的笔记
    book_name = title
    md_content = "# 标题\n这是一个Markdown文档示例1。"
    doc_id = create_doc_with_md(notebook_id, book_name, res)
    if doc_id:
        print(f"成功创建笔记: {title}, ID: {doc_id}")
    else:
        print(f"创建笔记失败: {title}")

        """
    根据doc_id获取文档内容，查找包含表格的div，并设置块属性。

    参数:
    - doc_id (str): 文档的唯一标识符（ID）。
    """
    # 获取文档内容
    doc_content = get_doc_content(doc_id)
    if not doc_content:
        print(f"无法获取文档内容，doc_id: {doc_id}")
        sys.exit(0)

    # 查找包含表格的div
    div_ids = find_divs_with_tables(doc_content)
    if not div_ids:
        print(f"未找到包含表格的div，doc_id: {doc_id}")
        sys.exit(0)

    # 设置块属性
    results = set_block_attributes_for_ids(div_ids, 1400)
    for result in results:
        if result["success"]:
            print(f"成功设置块属性，ID: {result['id']}")
        else:
            print(f"设置块属性失败，ID: {result['id']}, 错误信息: {result['msg']}")

    

    
                