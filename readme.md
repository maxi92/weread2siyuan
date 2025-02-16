# WeRead2SiYuan 项目 README 📚💻

## 项目简介
WeRead2SiYuan 是一个用于将微信读书的笔记和标注同步到思源笔记的应用程序。它可以帮助用户方便地管理和保存阅读过程中产生的笔记，确保所有内容都能在思源笔记中进行统一管理。🚀

## 功能特性
- **自动登录**：通过二维码扫描或已保存的Cookie实现微信读书的自动登录。🔒
- **多模式同步**：
  - 全量同步：每次同步时删除旧笔记并创建最新笔记。
  - 增量同步（默认）：仅对未标记“读完”的书籍进行更新，已标记“读完”的书籍不再重复同步。
  - 指定同步：可以选择特定书籍进行同步。
- **格式转换**：支持将微信读书中的笔记和想法转换为Markdown格式，并生成美观的表格展示。📝
- **图片上传**：自动上传书籍封面至思源笔记，并在笔记中插入对应的图片链接。🖼️
- **日志记录**：详细的日志记录功能，帮助开发者调试和用户了解同步过程。📜

### 最终生成的笔记截图参考
![Image text](https://github.com/maxi92/weread2siyuan/blob/master/readme/1.PNG)
![Image text](https://github.com/maxi92/weread2siyuan/blob/master/readme/2.PNG)
![Image text](https://github.com/maxi92/weread2siyuan/blob/master/readme/3.PNG)

## 使用技术栈
- **编程语言**：Python 🐍
- **GUI框架**：PyQt5 🖥️
- **Web引擎**：PyQtWebEngine 🌐
- **HTTP请求库**：Requests ⚡
- **HTML解析器**：BeautifulSoup4 🛠️
- **日志记录**：Logging 📝

## 安装与使用

### 源码运行：
1. **安装依赖**：
   ```bash
   pip install -r requirements.txt
   ```
2. **运行应用**：
   ```bash
   python main.py
   ```
3. **首次配置**：
   - 扫描二维码登录微信读书。
   - 输入思源笔记API Token（可在思源笔记设置中获取）。

### exe运行
 **请在release中下载exe文件，并运行即可。**

## 目录结构
```
weread2siyuan/
├── src/
│   ├── wereader.py      # 微信读书相关接口实现
│   ├── siyuan.py        # 思源笔记相关接口实现
│   └── main.py          # 主程序入口
├── temp/                # 临时文件夹，存储cookie等信息
└── README.md            # 项目说明文档
```

## 注意事项
- 确保思源笔记服务端口为 `http://127.0.0.1:6806`。
- 同步过程中请勿在思源笔记中对同步的笔记进行重要修改，以免被覆盖。
- 目前版本暂不支持公众号的同步，后续会继续优化

## 贡献指南
欢迎任何有兴趣的朋友参与贡献！如果您有任何问题或建议，请随时提交Issue或Pull Request。🤝

## 鸣谢
本项目微信读书的登录功能、书摘和想法的解析部分代码参考了<https://github.com/Higurashi-kagome/pythontools>项目，在此特别感谢该项目。

---

希望这个README能帮助您更好地理解和使用WeRead2SiYuan项目！如果有任何疑问，欢迎联系开发者。😊