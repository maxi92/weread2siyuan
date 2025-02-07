import requests

# 预先设置好的token
token = "your-token"

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

if __name__=='__main__':
    # 示例调用
    title = "测试文档123";

    result = search_docs_by_title(title)
    print(result)