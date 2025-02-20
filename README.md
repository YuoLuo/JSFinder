# JSFinder modifications

JSFinder is a tool for quickly extracting URLs and subdomains from JS files on a website.

JSFinder是一款用作快速在网站的js文件中提取URL，子域名的工具。

> 本项目基于[JSFinder](https://github.com/Threezh1/JSFinder)开发,URL提取正则来自[LinkFinder](https://github.com/GerbenJavado/LinkFinder)

## 🚀 新增功能 (New Features)

- **并发处理 (Concurrent Processing)**
  - 使用线程池提高扫描速度
  - Using thread pool to improve scanning speed

- **进度显示 (Progress Display)**
  - 实时显示扫描进度
  - Real-time scanning progress display

- **HTML报告 (HTML Report)**
  - 生成美观的HTML格式报告
  - Generate beautiful HTML format reports
  ```
  python JSFinder.py -u http://www.example.com -o report.html
  ```

- **URL过滤 (URL Filtering)**
  - 支持通过config.py配置URL黑名单
  - Support URL blacklist configuration via config.py
  ```python
  # config.py example
  URL_BLACKLIST = {
      'domains': ['google-analytics.com', 'doubleclick.net'],
      'extensions': ['.png', '.jpg', '.gif'],
      'keywords': ['javascript:', 'mailto:']
  }
  ```

- **改进的错误处理 (Improved Error Handling)**
  - 智能重试机制
  - 详细的日志记录
  - Smart retry mechanism
  - Detailed logging

## 用法 (Usage)

### 基本用法 (Basic Usage)

```bash
# 简单扫描
python JSFinder.py -u http://example.com

# 深度扫描并生成HTML报告
python JSFinder.py -u http://example.com -d -o report.html

# 使用Cookie扫描
python JSFinder.py -u http://example.com -c "sessionid=xxx"

# 从文件扫描
python JSFinder.py -f urls.txt
```

### 参数说明 (Parameters)

| 参数 | 说明 | Description |
|------|------|-------------|
| -u, --url | 指定目标网站 | Target website |
| -c, --cookie | 指定Cookie | Cookie for requests |
| -f, --file | 指定包含URL或JS的文件 | File containing URLs or JS |
| -ou, --outputurl | URL输出文件名 | Output file for URLs |
| -os, --outputsubdomain | 子域名输出文件名 | Output file for subdomains |
| -j, --js | 在JS文件中查找 | Find in JS files |
| -d, --deep | 深度查找 | Deep crawling |
| -o, --output | 输出HTML报告文件名 | Output HTML report filename |

### 注意事项 (Notes)

- URL需要包含http://或https://
- 指定JS文件爬取时，返回的URL为相对URL
- 批量URL扫描时，相对URL会基于第一个URL的域名转换为绝对URL

## 依赖安装 (Dependencies)

```bash
pip install -r requirements.txt
```

## 作者 (Authors)

- **原作者 (Original Author)**: [Threezh1](https://threezh1.github.io/)
- **增强版作者 (modifications Version Author)**: [yuluo](https://github.com/YuoLuo)

## 许可证 (License)

本项目采用 MIT 许可证。详见 [LICENSE](LICENSE) 文件。

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

Copyright (c) 2025 yuluo

## 免责声明 (Disclaimer)

本工具仅用于安全研究和授权测试，使用本工具进行攻击的行为与作者无关。

This tool is for security research and authorized testing only. The authors are not responsible for any malicious use of this tool.
