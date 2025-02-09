import requests
from bs4 import BeautifulSoup

# 预先设置好的token
token = "your-token"

"""
根据文档标题搜索文档。

参数:
    - title: str, 要搜索的文档标题

返回:
    - dict, 包含文档信息的字典，如果未找到则返回空字典
"""
def search_docs_by_title(title):
    url = "http://127.0.0.1:6806/api/filetree/searchDocs"
    
    # 设置请求头
    headers = {
        'Authorization': token,
        'Content-Type': 'application/json'
    }
    
    # 设置请求体
    body = {"k": title}
    
    try:
        # 发送POST请求
        response = requests.post(url, json=body, headers=headers)
        response.raise_for_status()  # 检查请求是否成功
        
        # 解析响应内容
        resp_json = response.json()
        
        if resp_json["code"] == 0 and isinstance(resp_json["data"], list) and len(resp_json["data"]) > 0:
            # 筛选符合条件的数据
            filtered_data = [
                item for item in resp_json["data"]
                if item.get("path") and item.get("hPath", "").split('/')[-1] == title
            ]
            
            if filtered_data:
                # 取第一个符合条件的数据
                selected_item = filtered_data[0]
                result = {
                    "box": selected_item.get("box", ""),
                    "hPath": selected_item.get("hPath", ""),
                    "path": selected_item.get("path", "")
                }
                return result
            else:
                return {}  # 如果没有符合条件的数据，返回空字典
        else:
            return {}  # 如果data为空数组或响应码不为0，返回空字典
    
    except requests.exceptions.RequestException as e:
        print(f"请求失败: {e}")
        return {}
    
"""
获取名为“测试笔记本”的笔记本的ID。

参数:
    - 无

返回:
    - str, 笔记本ID，如果未找到则返回空字符串
"""
def get_notebook_id_by_name():
    
    url = "http://127.0.0.1:6806/api/notebook/lsNotebooks"
    
    # 设置请求头
    headers = {
        'Authorization': token,
        'Content-Type': 'application/json'
    }
    
    try:
        # 发送POST请求
        response = requests.post(url, json={}, headers=headers)
        response.raise_for_status()  # 检查请求是否成功
        
        # 解析响应内容
        resp_json = response.json()
        
        if resp_json["code"] == 0 and "notebooks" in resp_json["data"]:
            notebooks = resp_json["data"]["notebooks"]
            
            # 筛选出name为“读书笔记”的元素
            for notebook in notebooks:
                if notebook.get("name") == "测试笔记本":
                    return notebook.get("id", "")
            
            # 如果没有找到符合条件的元素，返回空字符串
            return ""
        else:
            return ""  # 如果data为空或响应码不为0，返回空字符串
    
    except requests.exceptions.RequestException as e:
        print(f"请求失败: {e}")
        return ""
    
"""
创建一个名为“测试笔记本”的笔记本。

参数:
    - 无

返回:
    - str, 新创建的笔记本ID，如果创建失败则返回空字符串
"""
def create_notebook():
   
    url = "http://127.0.0.1:6806/api/notebook/createNotebook"
    
    # 设置请求头
    headers = {
        'Authorization': token,
        'Content-Type': 'application/json'
    }
    
    # 设置请求体
    body = {
        "name": "测试笔记本"
    }
    
    try:
        # 发送POST请求
        response = requests.post(url, json=body, headers=headers)
        response.raise_for_status()  # 检查请求是否成功
        
        # 解析响应内容
        resp_json = response.json()
        
        if resp_json["code"] == 0 and "notebook" in resp_json["data"]:
            notebook = resp_json["data"]["notebook"]
            return notebook.get("id", "")
        else:
            return ""  # 如果data为空或响应码不为0，返回空字符串
    
    except requests.exceptions.RequestException as e:
        print(f"请求失败: {e}")
        return ""
    
"""
在指定笔记本中创建一个Markdown文档。

参数:
    - notebook_id: str, 笔记本ID
    - book_name: str, 文档名称
    - md_content: str, Markdown格式的文档内容

返回:
    - dict, 包含文档信息的字典，如果创建失败则返回空字符串
"""
def create_doc_with_md(notebook_id, book_name, md_content):
    url = "http://127.0.0.1:6806/api/filetree/createDocWithMd"
    
    # 设置请求头
    headers = {
        'Authorization': token,
        'Content-Type': 'application/json'
    }
    
    # 设置请求体
    body = {
        "notebook": notebook_id,
        "path": book_name,
        "markdown": md_content
    }
    
    try:
        # 发送POST请求
        response = requests.post(url, json=body, headers=headers)
        response.raise_for_status()  # 检查请求是否成功
        
        # 解析响应内容
        resp_json = response.json()
        
        if resp_json["code"] == 0 and "data" in resp_json:
            return resp_json["data"]
        else:
            return ""  # 如果data为空或响应码不为0，返回空字符串
    
    except requests.exceptions.RequestException as e:
        print(f"请求失败: {e}")
        return ""
    
"""
根据 style 格式化文本。

参数:
    - text: str, 要格式化的文本
    - style: int, 格式化样式（0: 斜体, 1: 正常, 2: 加粗）

返回:
    - str, 格式化后的文本
"""
def format_text(text, style):

    if style == 0:
        return f"*{text}*"
    elif style == 2:
        return f"**{text}**"
    else:
        return text

"""
根据章节信息和书摘内容生成 markdown 格式字符串。

参数:
    - sorted_chapters: list, 每个元素为 (chapterUid, position, title)
        其中 position 用于确定标题级别（1 对应 "#", 2 对应 "##" 等）
    - sorted_contents: dict, key 为 chapterUid，value 为书摘列表，
        每个书摘结构为 [text_position, style, markText]
    - is_all_chapter: int, 如果 <= 0，则只输出有书摘内容的章节；如果 > 0，则输出所有章节
    
返回:
    - str, 拼接好的 markdown 格式字符串
"""
def generate_markdown(sorted_chapters, sorted_contents, is_all_chapter=1):
    
    markdown_lines = []
    
    # 遍历所有章节
    for chapter in sorted_chapters:
        chapterUid, pos, title = chapter
        
        # 如果设置只输出有内容的章节，且当前章节没有书摘，则跳过
        if is_all_chapter <= 0 and not sorted_contents.get(chapterUid):
            continue
        
        # 根据章节级别生成对应的 markdown 标题（例如 1 级用 "#", 2 级用 "##"）
        markdown_lines.append("#" * pos + " " + title)
        markdown_lines.append("")  # 添加空行
        
        # 获取当前章节的所有书摘内容
        chapter_contents = sorted_contents.get(chapterUid, [])
        if chapter_contents:
            # 添加表格头及分隔行
            markdown_lines.append("| 序号 | 书摘内容 |")
            markdown_lines.append("| ---- | -------- |")
            
            # 遍历当前章节的书摘内容
            for idx, text_item in enumerate(chapter_contents, start=1):
                _, style, text = text_item
                # 对书摘文本进行格式化，并在开头添加两个中文全角空格
                formatted_text = "　　" + format_text(text, style)
                # 序号部分使用加粗 Markdown 格式
                markdown_lines.append(f"| <strong>{idx}</strong> | {'　　' + format_text(text, style)} |")

            
            markdown_lines.append("")
        else:
            # 如果章节没有书摘内容，可以添加提示文本
            markdown_lines.append("暂无书摘内容")
            markdown_lines.append("")
    
    return "\n".join(markdown_lines)

def remove_doc_by_id(doc_id):

    """
    调用API删除指定ID的文档。

    功能：
    - 通过发送POST请求到指定的API端点，删除具有给定ID的文档。
    - 根据响应内容判断操作是否成功。

    入参：
    - doc_id (str): 文档的唯一标识符（ID）。
    """

    url = "http://127.0.0.1:6806/api/filetree/removeDocByID"
    
    # 设置请求头
    headers = {
        'Authorization': token,
        'Content-Type': 'application/json'
    }
    
    # 设置请求体
    body = {
        "id": doc_id
    }
    
    try:
        # 发送POST请求
        response = requests.post(url, json=body, headers=headers)
        response.raise_for_status()  # 检查请求是否成功
        
        # 解析响应内容
        resp_json = response.json()
        
        if resp_json["code"] == 0:
            return True  # 删除成功
        else:
            return False  # 删除失败
        
    except requests.exceptions.RequestException as e:
        print(f"请求失败: {e}")
        return False  # 请求异常，返回False
    
def remove_doc(notebook_id, path):
    """
    调用API删除指定notebook和路径的文档。

    入参：
    - notebook_id (str): 笔记本的唯一标识符（ID）。
    - path (str): 文档的路径。

    出参：
    - bool: 如果删除成功返回True，否则返回False。
    """
    url = "http://127.0.0.1:6806/api/filetree/removeDoc"
    
    # 设置请求头
    headers = {
        'Authorization': token,
        'Content-Type': 'application/json'
    }
    
    # 设置请求体
    body = {
        "notebook": notebook_id,
        "path": path
    }
    
    try:
        # 发送POST请求
        response = requests.post(url, json=body, headers=headers)
        response.raise_for_status()  # 检查请求是否成功
        
        # 解析响应内容
        resp_json = response.json()
        
        if resp_json["code"] == 0:
            return True  # 删除成功
        else:
            return False  # 删除失败
        
    except requests.exceptions.RequestException as e:
        print(f"请求失败: {e}")
        return False  # 请求异常，返回False
    
def get_doc_content(doc_id):
    """
    调用API获取指定ID的文档内容。

    入参：
    - doc_id (str): 文档的唯一标识符（ID）。

    出参：
    - str: 如果content不为空则返回content字符串，否则返回空字符串。
    """
    url = "http://127.0.0.1:6806/api/filetree/getDoc"
    
    # 设置请求头
    headers = {
        'Authorization': token,
        'Content-Type': 'application/json'
    }
    
    # 设置请求体
    body = {
        "id": doc_id
    }
    
    try:
        # 发送POST请求
        response = requests.post(url, json=body, headers=headers)
        response.raise_for_status()  # 检查请求是否成功
        
        # 解析响应内容
        resp_json = response.json()
        
        if resp_json["code"] == 0 and "data" in resp_json and resp_json["data"].get("content"):
            return resp_json["data"]["content"]  # 返回content字符串
        else:
            return ""  # content为空或响应不符合预期，返回空字符串
        
    except requests.exceptions.RequestException as e:
        print(f"请求失败: {e}")
        return ""  # 请求异常，返回空字符串

def find_divs_with_tables(html: str) -> list:
    """
    查找包含 <table> 的根 <div> 节点，并返回其 data-node-id 属性值列表。

    :param html: 原始 HTML 字符串
    :return: 包含 <table> 的 div 的 data-node-id 列表
    """
    soup = BeautifulSoup(html, "html.parser")
    return [div["data-node-id"] for div in soup.find_all("div", attrs={"data-node-id": True}) if div.find("table")]

def set_block_attributes_for_ids(id_array, width):
    """
    为给定的ID数组中的每个ID调用API设置块属性。

    入参：
    - id_array (list): 包含多个块ID的列表。
    - width (int): 宽度值，用于设置colgroup属性。

    出参：
    - list: 包含每个请求的结果（成功或失败）的列表。
    """
    url = "http://127.0.0.1:6806/api/attr/setBlockAttrs"
    
    # 设置请求头
    headers = {
        'Authorization': token,
        'Content-Type': 'application/json'
    }

    results = []

    for block_id in id_array:
        # 设置请求体
        payload = {
            "id": block_id,
            "attrs": {
                "colgroup": f"|width: {width}px;"
            }
        }

        try:
            # 发送POST请求
            response = requests.post(url, json=payload, headers=headers)
            response.raise_for_status()  # 检查请求是否成功
            
            # 解析响应内容
            resp_json = response.json()

            if resp_json["code"] == 0:
                results.append({"id": block_id, "success": True})
            else:
                results.append({"id": block_id, "success": False, "msg": resp_json.get("msg", "未知错误")})

        except requests.exceptions.RequestException as e:
            # 请求异常时记录错误信息并继续下一个ID
            print(f"请求失败 (ID: {block_id}): {e}")
            results.append({"id": block_id, "success": False, "msg": str(e)})

    return results

if __name__=='__main__':
    # 示例调用
    """ 
    title = "测试文档123";

    result = search_docs_by_title(title);
    print(result);
 """
    """     
    notebook_id = get_notebook_id_by_name()
    print(notebook_id)
    """
    """    
    notebook_id = create_notebook()
    print(notebook_id)
 """

    """     
    notebook_id = "20240728220314-dle1lqk"
    book_name = "测试文档/我的笔记"
    md_content = "# 标题\n这是一个Markdown文档示例。"

    doc_id = create_doc_with_md(notebook_id, book_name, md_content)
    print(doc_id) 
    """

    # 下面是示例数据
    sorted_chapters = [
        ("chap1", 1, "第一章 引言"),
        ("chap2", 2, "第二章 深入探讨"),
        ("chap3", 1, "第三章 结论")
    ]
    
    sorted_contents = {
        "chap1": [
            [1, 0, "这是斜体的书摘"],
            [2, 1, "这是正常的书摘"]
        ],
        "chap2": [
            [1, 2, "这是加粗的书摘"],
            [2, 1, "另一个正常书摘"]
        ],
        "chap3": []  # 此章节没有书摘内容
    }
    
    # 设置是否输出所有章节的标志：
    # 如果 is_all_chapter <= 0，则只输出有书摘的章节；如果 > 0，则输出所有章节
    is_all_chapter = 1  # 或设置为 0 看看效果
    
    # 生成 markdown 格式的内容
    markdown_output = generate_markdown(sorted_chapters, sorted_contents, is_all_chapter)
    
    # 输出到控制台，也可以将 markdown_output 保存到文件中
    print(markdown_output)