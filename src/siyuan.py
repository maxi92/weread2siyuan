import os
import requests
import tempfile
from urllib.parse import urlparse
from bs4 import BeautifulSoup
from collections import defaultdict
import logging

# 配置日志记录器
logging.basicConfig(
    level=logging.DEBUG,  # 设置最低日志级别
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='app.log',   # 将日志写入文件而不是终端
    filemode='a'          # 追加模式
)

logger = logging.getLogger(__name__)

# 预先设置好的token
token = None  # 这个值会在main.py中被覆盖
token_file = os.getcwd() + "\\temp\\config.txt"
current_notebook_name = None

# 读取token文件
def read_token_file():
    if os.path.exists(token_file) and os.path.isfile(token_file):
        with open(token_file, 'r', encoding='utf-8') as f:
            for line in f:
                if line.startswith('token='):
                    token = line.strip().split('token=')[1]
                    if token:
                        return token
    return None

# 写入token文件
def write_token_file(token):
    with open(token_file, 'w', encoding='utf-8') as f:
        f.write(f'token={token}')

def initialize_token():
    # 初始化token
    local_token = read_token_file()
    if not local_token:
        while True:
            local_token = input("请输入思源笔记token，可通过思源笔记的设置-关于-API token处获取：")
            if not local_token:
                print("思源笔记token为空！")
            else:
                write_token_file(local_token)
                break

    # 将local_token赋值给siyuan.py中的token变量
    global token
    token = local_token

def initialize_notebook_name():
    """
    初始化配置文件中的笔记本名称。
    如果 config.txt 中已有 "notebook_name=" 的键，则覆盖其值；否则新增该键。
    
    返回:
        None，配置直接写入 config.txt，同时全局变量 current_notebook_name 被更新。
    """
    import os
    from collections import defaultdict

    conf_file = os.path.join(os.getcwd(), "temp", "config.txt")
    default_name = "读书笔记"
    notebook_name = default_name

    # 如果配置文件存在，读取其中的 notebook_name
    if os.path.exists(conf_file) and os.path.isfile(conf_file):
        with open(conf_file, 'r', encoding='utf-8') as f:
            for line in f:
                if line.startswith('notebook_name='):
                    notebook_name = line.strip().split('notebook_name=')[1].strip()
                    if not notebook_name:
                        notebook_name = default_name
                    break

    # 提示用户输入笔记本名称
    user_input = input(f"请输入存储读书笔记的笔记本名称（直接回车则为“{notebook_name}”）：").strip()
    if user_input:
        notebook_name = user_input
        # 读取现有配置内容
        lines = []
        if os.path.exists(conf_file) and os.path.isfile(conf_file):
            with open(conf_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            # 遍历所有行，查找 notebook_name 键并更新
            found = False
            for i, line in enumerate(lines):
                if line.startswith('notebook_name='):
                    lines[i] = f'notebook_name={notebook_name}\n'
                    found = True
                    break
            if not found:
                lines.append(f'notebook_name={notebook_name}\n')
        else:
            lines = [f'notebook_name={notebook_name}\n']
        # 写回配置文件，覆盖原有内容
        with open(conf_file, 'w', encoding='utf-8') as f:
            f.writelines(lines)

    # 更新全局变量
    global current_notebook_name
    current_notebook_name = notebook_name



def get_sync_mode_and_book_id():
    """
    获取用户选择的同步模式和书籍ID。

    该方法会在终端打印同步模式选项，并等待用户输入。
    根据用户的输入，它会设置sync_mode和selected_book_id的值，并在最后返回这两个值。
    如果用户选择的是模式3，它还会要求用户输入书籍ID，并确保输入不为空。

    返回:
        - sync_mode (int): 用户选择的同步模式，1表示全量同步，2表示增量同步，3表示指定同步某一本书。
        - selected_book_id (str): 如果用户选择了模式3，则为用户输入的书籍ID，否则为None。
    """
    sync_mode = None
    selected_book_id = None

    while sync_mode is None:
        print("同步模式：")
        print("按1：全量同步（对于所有书籍，每一次同步都会将前一次的笔记删除，以最新的内容创建新的笔记，故请注意不要在笔记中添加重要的内容）")
        print("按2或直接回车：增量同步（对于未标记“读完”的书籍，每一次同步都会将前一次的笔记删除，以最新的内容创建新的笔记，故请注意不要在笔记中添加重要的内容；对于已经标记“读完”的书籍，若已经同步到思源笔记过，则后续不会再同步，可以放心在里面添加内容）")
        print("按3：指定同步某一本书（选择该选项后，请输入书籍id，本应用会将该书前一次的笔记删除，以最新的内容创建新的笔记）")
        print("请选择同步模式：", end="")
        user_input = input().strip()

        if user_input == '1':
            sync_mode = 1
        elif user_input in ('2', ''):
            sync_mode = 2
        elif user_input == '3':
            sync_mode = 3
        else:
            print("同步模式选择有误，请重新输入！")

    if sync_mode == 3:
        while selected_book_id is None:
            print("请输入书籍id:", end="")
            book_id_input = input().strip()
            if book_id_input:
                selected_book_id = book_id_input
            else:
                print("书籍id输入有误，请重新输入！")

    return sync_mode, selected_book_id

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
        logger.debug(f"请求失败: {e}")
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
                if notebook.get("name") == current_notebook_name:
                    return notebook.get("id", "")
            
            # 如果没有找到符合条件的元素，返回空字符串
            return ""
        else:
            return ""  # 如果data为空或响应码不为0，返回空字符串
    
    except requests.exceptions.RequestException as e:
        logger.debug(f"请求失败: {e}")
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
        "name": current_notebook_name
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
        logger.debug(f"请求失败: {e}")
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
        logger.debug(f"请求失败: {e}")
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

   """  if style == 0:
        return f"*{text}*"
    elif style == 2:
        return f"**{text}**"
    else:
        return text """
   
   return text;

def generate_markdown(sorted_chapters, sorted_contents, sorted_thoughts, is_all_chapter=1):
    """
    根据章节信息、书摘内容和想法生成包含完整章节结构的 markdown 格式字符串。
    
    参数:
        - sorted_chapters: list, 每个元素为 (chapterUid, level, title)，按照深度优先顺序排列
        - sorted_contents: dict, key 为 chapterUid，value 为书摘列表，每个书摘为 [text_position, style, markText]
        - sorted_thoughts: list, 按章节包含原文和想法的排序信息，每个元素为 (chapterUid, [(position, abstract, content)])
        - is_all_chapter: int, 如果 <= 0，则只输出有书摘内容的章节；如果 > 0，则输出所有章节
        
    返回:
        - str, 拼接好的 markdown 格式字符串
    """
    # 合并 sorted_contents 和 sorted_thoughts
    merged_thoughts = defaultdict(list)

    for chapterUid, content_items in sorted_contents.items():
        for text_position, style, markText in content_items:
            merged_thoughts[chapterUid].append((text_position, markText, "", style))  # markText为书摘内容，style为样式

    for chapterUid, thought_items in sorted_thoughts:
        for position, abstract, content in thought_items:
            # 如果已存在相同的 markText，则去重，保留 sorted_thoughts
            existing_items = merged_thoughts.get(chapterUid, [])
            for idx, (text_position, existing_markText, _, _) in enumerate(existing_items):
                if existing_markText == abstract:
                    merged_thoughts[chapterUid][idx] = (position, abstract, content, existing_items[idx][3])  # 替换为 sorted_thoughts 内容
                    break
            else:
                merged_thoughts[chapterUid].append((position, abstract, content, ""))  # 如果没有相同的 markText，就新增

    # 对每个章节的内容按 position 排序
    for chapterUid in merged_thoughts:
        merged_thoughts[chapterUid] = sorted(merged_thoughts[chapterUid], key=lambda x: x[0])

    markdown_lines = []
    printed_ids = set()  # 记录已输出的章节ID

    # 把level+1，这样最后最高级标题为H2，更合适一点
    sorted_chapters = [(chapterUid, level + 1, title) for chapterUid, level, title in sorted_chapters]

    # 遍历所有章节（已按深度优先排序）
    for i, chapter in enumerate(sorted_chapters):
        chapterUid, level, title = chapter

        # 如果只输出有内容的章节，且当前章节没有书摘，则跳过
        if is_all_chapter <= 0 and chapterUid not in merged_thoughts:
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

        # 获取当前章节的合并内容
        chapter_contents = merged_thoughts.get(chapterUid, [])

        if chapter_contents:
            markdown_lines.append("| 序号 | 书摘内容 | 想法 |")
            markdown_lines.append("| ---- | -------- | ---- |")

            # 遍历每个合并后的条目
            for idx, (position, abstract, content, style) in enumerate(chapter_contents, start=1):
                # 在书摘内容前添加两个中文全角空格，并使用 format_text 格式化
                formatted_text = "　　" + format_text(abstract, style) if abstract else ""
                # 将换行符替换为 <br> 后同时在新行开头插入两个中文全角空格
                formatted_text = formatted_text.replace("\r\n", "<br>　　").replace("\n", "<br>　　")
                # 在想法内容前添加两个中文全角空格，并使用 <em> 标签格式化
                thought_text = f"　　<em>{content}</em>" if content else ""
                # 将换行符替换为 <br> 后同时在新行开头插入两个中文全角空格
                thought_text = thought_text.replace("\r\n", "<br>　　").replace("\n", "<br>　　")

                markdown_lines.append(f"| <strong>{idx}</strong> | {formatted_text} | {thought_text} |")
            
            markdown_lines.append("")
        else:
            markdown_lines.append("暂无书摘或想法内容")
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
        logger.debug(f"请求失败: {e}")
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
        logger.debug(f"请求失败: {e}")
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
        logger.debug(f"请求失败: {e}")
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
            logger.debug(f"请求失败 (ID: {block_id}): {e}")
            results.append({"id": block_id, "success": False, "msg": str(e)})

    return results

def upload_image_from_url(image_url):
    """
    从给定的图片网址下载图片，并上传到指定的API接口。
    
    参数:
    image_url (str): 图片的网址字符串。
    
    返回:
    str: 成功上传后的图片路径（如果上传成功），否则返回None。
    """
    # 下载图片并保存到临时文件夹
    response = requests.get(image_url)
    if response.status_code != 200:
        logger.debug(f"Failed to download image from {image_url}")
        return None
    
    # 创建临时文件
    with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg", dir=tempfile.gettempdir()) as tmp_file:
        tmp_file.write(response.content)
        temp_file_path = tmp_file.name
    
    try:
        # 使用上下文管理器确保文件句柄被正确关闭
        with open(temp_file_path, 'rb') as file_handle:
            # 准备上传文件的form-data，确保file[]是一个数组
            files = [
                ('assetsDirPath', (None, '/assets/')),  # text类型
                ('file[]', (os.path.basename(urlparse(image_url).path), file_handle)),  # File类型，注意这里使用file[]
            ]
            
            headers = {
                'Authorization': f'token {token}'
            }
            
            # 发送POST请求
            upload_response = requests.post('http://127.0.0.1:6806/api/asset/upload', headers=headers, files=files)
            upload_response_json = upload_response.json()
            
            # 检查响应是否成功
            if upload_response_json.get('code') == 0:
                succ_map = upload_response_json.get('data', {}).get('succMap', {})
                if succ_map:
                    # 返回第一个成功上传的文件路径
                    return next(iter(succ_map.values()))
            else:
                logger.debug(f"Upload failed: {upload_response_json.get('msg')}")
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
    uploaded_path = upload_image_from_url(image_url)
    print(uploaded_path)
