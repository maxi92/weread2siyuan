import json
import os
import sys
import requests
from collections import defaultdict

USERVID = 0

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