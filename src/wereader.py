import json
import os
import sys
import requests
from collections import defaultdict
from urllib3.exceptions import InsecureRequestWarning  # 直接从 urllib3 导入
import logging

# 配置日志记录器
logging.basicConfig(
    level=logging.DEBUG,  # 设置最低日志级别
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='app.log',   # 将日志写入文件而不是终端
    filemode='a'          # 追加模式
)

logger = logging.getLogger(__name__)

# 禁用 InsecureRequestWarning 警告
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

USERVID = 0
level1 = '## '#(微信读书)一级标题
level2 = '### '#二级标题
level3 = '#### '#三级标题
style1 = {'pre': "",   'suf': ""}#(微信读书)红色下划线
style2 = {'pre': "**",   'suf': "**"}#橙色背景色
style3 = {'pre': "",   'suf': ""}#蓝色波浪线

headers_p = {
    'Connection': 'keep-alive',
    'Accept': 'application/json, text/plain, */*',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.103 Safari/537.36',
    'Content-Type': 'application/json;charset=UTF-8',
    'Origin': 'https://weread.qq.com',
    'Sec-Fetch-Site': 'same-origin',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Dest': 'empty',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
}

# 设置header
headers = {
    'Host': 'i.weread.qq.com',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.103 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8'
}

def login_success(headers):
    """判断是否登录成功"""
    url = "https://i.weread.qq.com/user/notebooks"
    r = requests.get(url,headers=headers,verify=False)
    if r.ok:
        return True
    else:
        return False
    
"""
(不排序)获取书架中的书：
直接列出——{'bookId1':"title1"...}
按分类列出——{"计算机":{'bookId1':"bookName"...}...}
"""
def get_bookshelf(userVid=USERVID,list_as_shelf = True):
    url = "https://i.weread.qq.com/shelf/sync?userVid=" + str(userVid) + "&synckey=0&lectureSynckey=0" 
    data = request_data(url)
    """获取书架上所有书"""
    if list_as_shelf == True:   #分类列出
        #遍历所有书并储存到字典
        books = {}
        for book in data['books']:
            books[book['bookId']] = book['title']
        
        #遍历书架分类创建整个书架
        shelf = defaultdict(dict)
        #遍历书架分类
        for archive in data['archive']:
            #遍历书架分类内的书本id并赋值
            for bookId in archive['bookIds']:
                shelf[archive['name']][bookId] = books[bookId]
                del books[bookId]
        #附加未分类书本
        for bookId,bookName in books.items():
            shelf['未分类书本'][bookId] = bookName
        return shelf
    else:   #直接列出
        #遍历所有书并储存到字典
        books = {}
        for book in data['books']:
            books[book['bookId']] = book['title']
        return books
    
"""按分类输出，文档树样式"""
def print_books_as_tree(userVid=USERVID):
    shelf = get_sorted_bookshelf(userVid)
    #获得{readUpdatetime1:'计算机',...}
    sorted_group = {}
    for group_name in shelf.keys():
        sorted_group[shelf[group_name][0][0]] = group_name
    #排序,得到[(readUpdatetime1,'计算机'),...]
    sorted_group = sorted(sorted_group.items())
    sorted_group.reverse()
    print('\n你的书架')
    #遍历分类
    for group in sorted_group:
        group_name = group[1]
        print('    ┣━━ ' + group_name)
        #遍历分类下的书
        for book in shelf[group_name]:
            book_id = book[1]
            book_name = book[2]
            print('    ┃    ┣━━  ' + book_id + ' '*(9 - len(book_id)) + ' ' + book_name)
        print('    ┃          ')
        print('    ┃          ')
    return ''

"""
(排序)获取书架中的书:
直接列出——[(readUpdateTime,['bookId',"bookName"]),...]
按分类列出——{'计算机':[[readUpdatetime,'bookId','title'],...]}
"""
def get_sorted_bookshelf(userVid=USERVID,list_as_shelf = True):
    url = "https://i.weread.qq.com/shelf/sync?userVid=" + str(userVid) + "&synckey=0&lectureSynckey=0"
    data = request_data(url)
    """获取书架上的所有书"""
    if list_as_shelf == True:   #分类列出
        #{'bookId':[readUpdatetime,'bookId',title]}
        books = {}
        for book in data['books']:
            bookId = book['bookId']
            books[bookId] = [book['readUpdateTime'],bookId,book['title']]
        #遍历书本分类：{'计算机':[[readUpdatetime,'bookId',title],...]}
        shelf = defaultdict(list)
        for archive in data['archive']:
            #遍历某类别内的书本id并追加[readUpdatetime,'bookId',title]
            for bookId in archive['bookIds']:
                shelf[archive['name']].append(books[bookId])
                del books[bookId]
        #附加未分类书本
        if books:
            for bookId in books.keys():
                shelf['未分类书本'].append(books[bookId])
        #排序
        for category in shelf.keys():
            shelf[category] = sorted(shelf[category],key=lambda x: x[0])
            shelf[category].reverse()
        return shelf
    else:   #直接列出
        #遍历所有书并储存到字典,得到{{readUpdateTime:['bookId',"bookName"]}}
        books = {}
        for book in data['books']:
            books[book['readUpdateTime']] = [book['bookId'],book['title']]
        #排序得到[(readUpdateTime,['bookId',"bookName"])]
        sorted_books = sorted(books.items())
        sorted_books.reverse()
        return sorted_books

"""由url请求数据"""
def request_data(url):
    global headers
    r = requests.get(url,headers=headers,verify=False)
    if r.ok:
        data = r.json()
    else:
        raise Exception(r.text)
    return data

def set_chapter_level(level):
    global level1,level2,level3
    if level == 1:
        return level1
    elif level == 2:
        return level2
    elif level == 3:
        return level3
    
def set_content_style(style,text):
    global style1,style2,style3
    if style == 0:#红色下划线
        return style1['pre'] + text.strip() + style1['suf']
    elif style == 1:#橙色背景色
        return style2['pre'] + text.strip() + style2['suf']
    elif style == 2:#蓝色波浪线
        return style3['pre'] + text.strip() + style3['suf']
    
"""
(按顺序)获取书中的标注(Markdown格式、标题分级、标注前后缀)
"""
def get_bookmarklist(bookId,is_all_chapter=1):
    """获取笔记返回md文本"""
    #请求数据
    url = "https://i.weread.qq.com/book/bookmarklist?bookId=" + bookId
    data = request_data(url)
    """处理数据，生成笔记"""
    res = ''
    res = get_md_str_from_data(data,is_all_chapter = is_all_chapter)
    if res == '':#如果在书本中未找到标注
        print('书中无标注/获取出错')
        return ''
    return res

"""
获取章节信息和划线内容
"""
def getChaptersAndContents(bookId,is_all_chapter=1):
    """获取笔记返回md文本"""
    #请求数据
    url = "https://i.weread.qq.com/book/bookmarklist?bookId=" + bookId
    data = request_data(url)
    """处理数据，生成笔记"""
    #获取章节和标注
    sorted_chapters = get_sorted_chapters(bookId)
    sorted_contents = get_sorted_contents_from_data(data)
    return sorted_chapters,sorted_contents

"""
(按顺序)返回data数据中的标注(Markdown格式)，标注标题按级别设置，标注内容设置前后缀
"""
def get_md_str_from_data(data,is_all_chapter=1):
    res = '\n'
    bookId = data['book']['bookId']
    #书本为公众号的情况
    if '_' in bookId:
        sorted_contents = get_sorted_contents_from_data(data)
        #遍历章节
        for chapter in sorted_contents:
            #获得章节标题和标注
            for title,marks in chapter.items():
                res += '### ' + title + '\n\n'
                #遍历标注
                for mark in marks:
                    res += mark[1] + '\n\n'
        return res
    #获取章节和标注
    sorted_chapters = get_sorted_chapters(bookId)
    sorted_contents = get_sorted_contents_from_data(data)
    #遍历章节
    for chapter in sorted_chapters:#chapter = (chapterUid,position,title)
        #如果指明不输出所有标题
        if is_all_chapter <= 0 and len(sorted_contents[chapter[0]]) == 0:
            continue
        #获取章节名
        title = chapter[2]
        res += set_chapter_level(chapter[1]) + title + '\n\n'
        #遍历一章内的标注
        for text in sorted_contents[chapter[0]]:#text = [position,style,markText]
            res += set_content_style(text[1],text[2]) + '\n\n'
    return res

"""
获取以章节id为键，以排序好的标注列表为值的字典：
{"chapterUid":[[text_positon1,style1,"text1"],[text_positon2,style2,"text2"]...]}
"""
def get_sorted_contents_from_data(data):
    bookId = data['book']['bookId']
    #书本为公众号的情况{createTime:[[text_position1,'text1'],...]}
    if '_' in bookId:
        sorted_content = []  #
        marks = defaultdict(list)   #{'refMpReviewId':[[position,'text'],...],...}
        chapters = defaultdict(list) #{createTime:['reviewId','title'],...}
        i = 0
        for refMpInfos in data['refMpInfos']:
            chapters[i] = [refMpInfos['reviewId'],refMpInfos['title']]
            i = i + 1
        #排序得到[(createTime1,['revieId1','title1']),...]
        sorted_chapters = sorted(chapters.items())
        #获得{createTime1:[[text_position1,'text1'],...],...}
        for item in data['updated']:
            marks[item['refMpReviewId']].append([int(item['range'].split('-')[0]),item['markText']])
        #排序得到{'refMpReviewId':[[position1,'title1'],...]...}
        sorted_marks = {}
        for key in marks.keys():
            sorted_marks[key] =  sorted(marks[key],key=lambda x: x[0])
        #遍历章节
        for chapter in sorted_chapters:
            sorted_content.append({chapter[1][1]:sorted_marks[chapter[1][0]]})
        return sorted_content
        
    contents = defaultdict(list)
    """遍历所有标注并添加到字典储存起来"""
    for item in data['updated']:#遍历标注
        #获取标注的章节id
        chapterUid = item['chapterUid']
        #获取标注的文本内容
        text = item['markText']
        #获取标注开始位置用于标记位置
        text_position = int(item['range'].split('-')[0])
        text_style = item['style']
        #以章节id为键，以章内标注构成的列表为值,获得{"chapterUid":{text_positon:"text"}}
        contents[chapterUid].append([text_position,text_style,text])
    """将每章内的标注按键值排序，得到sorted_contents = {"chapterUid":[[text_positon2,style2,"text2"],[text_positon1,style1,"text1"]...]}"""
    sorted_contents = defaultdict(list)
    for chapterUid in contents.keys():
        #标注按位置排序，获得：
        #{"chapterUid":[[text_positon1,style1,"text1"],[text_positon2,style2,"text2"]...]}
        sorted_contents[chapterUid] = sorted(contents[chapterUid],key=lambda x: x[0])
    return sorted_contents

"""
(按顺序)获取书中的章节：
[(1, 1, '封面'), (2, 1, '版权信息'), (3, 1, '数字版权声明'), (4, 1, '版权声明'), (5, 1, '献给'), (6, 1, '前言'), (7, 1, '致谢')]
"""
def get_sorted_chapters(bookId):
    if '_' in bookId:
        print('公众号不支持输出目录')
        return ''
    url = "https://i.weread.qq.com/book/chapterInfos?" + "bookIds=" + bookId + "&synckeys=0"
    data = request_data(url)
    chapters = []
    #遍历章节,章节在数据中是按顺序排列的，所以不需要另外排列
    for item in data['data'][0]['updated']:
        #判断item是否包含level属性。
        try:
            chapters.append((item['chapterUid'],item['level'],item['title']))
        except:
            chapters.append((item['chapterUid'],1,item['title']))
    """chapters = [(1, 1, '封面'), (2, 1, '版权信息'), (3, 1, '数字版权声明'), (4, 1, '版权声明'), (5, 1, '献给'), (6, 1, '前言'), (7, 1, '致谢')]"""
    return chapters


"""
获取书本信息(Markdown格式)
"""
def get_bookinfo(bookId):
    if '_' in bookId:
        print('公众号不支持书本信息')
        return ''
    """获取书的详情"""
    url = "https://i.weread.qq.com/book/info?bookId=" + bookId
    data = request_data(url)
    
    # 确定需要保留的键
    keys_to_keep = ['title', 'author', 'intro', 'category', 'publisher', 'totalWords', 'cover','finished']
    
    # 使用字典推导式来生成新的字典，只保留指定的键
    new_book_info = {key: data[key] for key in keys_to_keep if key in data}
    
    # 检查'cover'是否在新字典中，如果存在则进行字符串替换
    # 为了获取封面的高清图片
    if 'cover' in new_book_info:
        new_book_info['cover'] = new_book_info['cover'].replace('s_', 't7_')

    return new_book_info

def generate_markdown_table(new_book_info): 
    """
    根据给定的书籍信息字典生成一个Markdown格式的表格字符串。

    参数:
        new_book_info (dict): 包含书籍信息的字典，至少包含 author、category、publisher、totalWords、intro 键。

    返回:
        str: 一个Markdown格式的字符串，展示作者、分类、出版社、字数、简介等信息。
             简介部分的换行符会被替换为 '<br>　　'，即换行后带有两个中文全角空格，
             以适应Markdown表格中的多行文本显示。
    """
    # 定义要展示的信息及其对应的中文标签
    info_to_display = [
        ('author', '作者'),
        ('category', '分类'),
        ('publisher', '出版社'),
        ('totalWords', '字数'),
        ('intro', '简介')
    ]

    # 获取封面图片路径
    cover_image_path = new_book_info.get('cover_image_path', '')

    # 开始构建Markdown表格字符串
    markdown_str = '| 中文标签 | 内容 |\n| --- | --- |\n'

    # 增加封面图片行，使用动态路径
    markdown_str += f'| <strong>封面</strong> | ![封面]({cover_image_path}) |\n'



    # 遍历展示书籍信息
    for key, label in info_to_display:
        if key in new_book_info:
            if key == 'intro':
                # 为简介字段添加两个中文全角空格，并将换行符替换为 '<br>　　'
                value = "　　" + new_book_info[key].replace("\r\n", "<br>　　").replace("\n", "<br>　　")
            else:
                value = new_book_info[key]
            
            # 使第一列（标签）加粗，第二列（内容）变为斜体
            markdown_str += f'| <strong>{label}</strong> | {value} |\n'

    print('**********************************************************')
    logger.debug(markdown_str)

    return markdown_str

def get_mythought(bookId):
    """
    获取微信读书中的书籍的章节想法和原文内容，将原文和想法分开存储并绑定。

    参数:
        bookId (str): 书籍的唯一标识符，用于从接口获取相关书籍的数据。

    返回:
        tuple: 返回两个元素
            - d_sorted_chapters (list): 包含有想法的章节列表，每个元素为 (chapterUid, level, title)。
            - sorted_thoughts (list): 包含每个章节的原文和想法数据，每个元素为 (chapterUid, [(position, abstract, content)])。
                - 每个章节包含一个列表，列表中是按位置排序的 `(position, abstract, content)` 元组。
    """
    res = ''
    """获取数据"""
    if '_' in bookId:
        url = 'https://i.weread.qq.com/review/list?listtype=6&mine=1&bookId=' + bookId + '&synckey=0&listmode=0'
        data = request_data(url)
        print('公众号暂时不支持获取想法')
        return ''
    else:
        url = "https://i.weread.qq.com/review/list?bookId=" + bookId + "&listType=11&mine=1&synckey=0&listMode=0"
        data = request_data(url)

    # thoughts字典现在存储原文和想法绑定在一起
    thoughts = defaultdict(list)
    MAX = 1000000000
    items = data['reviews']
    for item in items:
        if 'chapterUid' not in item['review']:
            continue  # 跳过没有 chapterUid 的 item
        # 获取想法所在章节id
        chapterUid = item['review']['chapterUid']
        # 获取原文内容
        abstract = item['review']['abstract']
        # 获取想法
        text = item['review']['content']
        # 获取想法开始位置
        try:
            text_position = int(item['review']['range'].split('-')[0])
        except:
            # 处理在章末添加想法的情况 (将位置设置为一个很大的值)
            text_position = MAX + int(item['review']['createTime'])
        
        # 将原文和想法绑定，按位置存储
        thoughts[chapterUid].append((text_position, abstract, text))

    # 章节内原文和想法按位置排序
    thoughts_sorted_range = defaultdict(list)
    for chapterUid in thoughts.keys():
        thoughts_sorted_range[chapterUid] = sorted(thoughts[chapterUid], key=lambda x: x[0])  # 按position排序

    # 章节按id排序
    sorted_thoughts = sorted(thoughts_sorted_range.items())
    
    # 获取包含目录级别的目录数据
    # 获取包含目录级别的全书目录[(chapterUid, level, 'title')]
    sorted_chapters = get_sorted_chapters(bookId)
    # 去除没有想法的目录项
    d_sorted_chapters = [chapter for chapter in sorted_chapters if chapter[0] in thoughts_sorted_range.keys()]
    
    return d_sorted_chapters, sorted_thoughts

def are_sorted_contents_and_thoughts_empty(sorted_contents, sorted_thoughts):
    """
    判断 sorted_contents 和 sorted_thoughts 是否同时为空。
    
    参数:
        - sorted_contents: dict, key 为 chapterUid，value 为书摘列表，每个书摘为 [text_position, style, markText]
        - sorted_thoughts: list, 按章节包含原文和想法的排序信息，每个元素为 (chapterUid, [(position, abstract, content)])
    
    返回:
        - bool: 如果 sorted_contents 和 sorted_thoughts 都为空，返回 True；否则返回 False
    """
    # 判断 sorted_contents 是否为空
    contents_empty = not bool(sorted_contents)
    
    # 判断 sorted_thoughts 是否为空
    thoughts_empty = not bool(sorted_thoughts)
    
    # 如果两个都为空，返回 True；否则返回 False
    return contents_empty and thoughts_empty


