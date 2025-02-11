import os
import requests
import tempfile
from urllib.parse import urlparse
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

def generate_markdown(sorted_chapters, sorted_contents, is_all_chapter=1):
    """
    根据章节信息和书摘内容生成包含完整章节结构的 markdown 格式字符串。
    
    参数:
        - sorted_chapters: list, 每个元素为 (chapterUid, level, title)，按照深度优先顺序排列
        - sorted_contents: dict, key 为 chapterUid，value 为书摘列表，每个书摘为 [text_position, style, markText]
        - is_all_chapter: int, 如果 <= 0，则只输出有书摘内容的章节；如果 > 0，则输出所有章节
    返回:
        - str, 拼接好的 markdown 格式字符串
    """
    markdown_lines = []
    printed_ids = set()  # 记录已输出的章节ID

    #把level+1，这样最后最高级标题为H2，更合适一点
    sorted_chapters = [(chapterUid, level + 1, title) for chapterUid, level, title in sorted_chapters]

    # 遍历所有章节（已按深度优先排序）
    for i, chapter in enumerate(sorted_chapters):
        chapterUid, level, title = chapter

        # 如果只输出有内容的章节，且当前章节没有书摘，则跳过
        if is_all_chapter <= 0 and not sorted_contents.get(chapterUid):
            continue

        # 如果章节级别大于1，检查是否需要回溯输出未输出的祖先章节
        if level > 2:
            current_level = level - 1
            ancestors = []
            # 向上扫描，寻找所有祖先（即最近的、级别分别为 level-1, level-2, ... , 1 的章节）
            for j in range(i - 1, -1, -1):
                anc_uid, anc_level, anc_title = sorted_chapters[j]
                if anc_level == current_level:
                    ancestors.append((anc_uid, anc_level, anc_title))
                    current_level -= 1
                    if current_level == 0:
                        break
            ancestors.reverse()  # 保证从根到直接父章节的顺序
            for anc_uid, anc_level, anc_title in ancestors:
                if anc_uid not in printed_ids:
                    markdown_lines.append("#" * anc_level + " " + anc_title)
                    markdown_lines.append("")
                    printed_ids.add(anc_uid)

        # 输出当前章节标题（如果还未输出）
        if chapterUid not in printed_ids:
            markdown_lines.append("#" * level + " " + title)
            markdown_lines.append("")
            printed_ids.add(chapterUid)

        # 获取当前章节的书摘内容
        chapter_contents = sorted_contents.get(chapterUid, [])
        if chapter_contents:
            markdown_lines.append("| 序号 | 书摘内容 |")
            markdown_lines.append("| ---- | -------- |")
            for idx, text_item in enumerate(chapter_contents, start=1):
                _, style, text = text_item
                # 在书摘内容前添加两个中文全角空格，并使用 format_text 格式化
                formatted_text = "　　" + format_text(text, style)
                # 将换行符替换为 <br> 后同时在新行开头插入两个中文全角空格
                formatted_text = formatted_text.replace("\n", "<br>　　")
                markdown_lines.append(f"| <strong>{idx}</strong> | {formatted_text} |")
            
            markdown_lines.append("")
        else:
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

def upload_image_from_url_fixed(image_url):
    """
    从给定的图片网址下载图片，并上传到指定的API接口，确保files作为一个数组传递。
    
    参数:
    image_url (str): 图片的网址字符串。
    
    返回:
    str: 成功上传后的图片路径（如果上传成功），否则返回None。
    """
    # 下载图片并保存到临时文件夹
    response = requests.get(image_url)
    if response.status_code != 200:
        print(f"Failed to download image from {image_url}")
        return None
    
    # 创建临时文件
    with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg", dir=tempfile.gettempdir()) as tmp_file:
        tmp_file.write(response.content)
        temp_file_path = tmp_file.name
    
    try:
        # 准备上传文件的form-data，确保files是一个数组
        files = [
            ('assetsDirPath', (None, '/assets/')),  # text类型
            ('files[]', (os.path.basename(urlparse(image_url).path), open(temp_file_path, 'rb'))),  # File类型，注意这里使用files[]
        ]
        
        headers = {
            'Authorization': f'token {token}'
        }

        print(files)
        
        # 发送POST请求
        upload_response = requests.post('http://127.0.0.1:6806/api/asset/upload', headers=headers, files=files)
        upload_response_json = upload_response.json()
        print(upload_response_json)
        
        # 检查响应是否成功
        if upload_response_json.get('code') == 0:
            succ_map = upload_response_json.get('data', {}).get('succMap', {})
            if succ_map:
                # 返回第一个成功上传的文件路径
                return next(iter(succ_map.values()))
        else:
            print(f"Upload failed: {upload_response_json.get('msg')}")
            return None
    finally:
        # 删除临时文件
        os.remove(temp_file_path)



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
    """
    
    image_url = 'https://cdn.weread.qq.com/weread/cover/33/cpPlatform_6KREKi1aMoV88q4acZ9cVw/t7_cpPlatform_6KREKi1aMoV88q4acZ9cVw.jpg'
    uploaded_path = upload_image_from_url_fixed(image_url)
    print(uploaded_path)