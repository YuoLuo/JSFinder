#!/usr/bin/env python"
# coding: utf-8
# By Threezh1
# https://threezh1.github.io/

import requests, argparse, sys, re
from requests.packages import urllib3
from urllib.parse import urlparse
from bs4 import BeautifulSoup
import concurrent.futures
import logging
from tqdm import tqdm
import time
import json
from datetime import datetime
import os

def parse_args():
    parser = argparse.ArgumentParser(epilog='\tExample: \r\npython ' + sys.argv[0] + " -u http://www.baidu.com")
    parser.add_argument("-u", "--url", help="The website")
    parser.add_argument("-c", "--cookie", help="The website cookie")
    parser.add_argument("-f", "--file", help="The file contains url or js")
    parser.add_argument("-ou", "--outputurl", help="Output file name. ")
    parser.add_argument("-os", "--outputsubdomain", help="Output file name. ")
    parser.add_argument("-j", "--js", help="Find in js file", action="store_true")
    parser.add_argument("-d", "--deep",help="Deep find", action="store_true")
    parser.add_argument("-o", "--output", help="Output HTML report file name")
    return parser.parse_args()

# Regular expression comes from https://github.com/GerbenJavado/LinkFinder
def extract_URL(JS):
	pattern_raw = r"""
	  (?:"|')                               # Start newline delimiter
	  (
	    ((?:[a-zA-Z]{1,10}://|//)           # Match a scheme [a-Z]*1-10 or //
	    [^"'/]{1,}\.                        # Match a domainname (any character + dot)
	    [a-zA-Z]{2,}[^"']{0,})              # The domainextension and/or path
	    |
	    ((?:/|\.\./|\./)                    # Start with /,../,./
	    [^"'><,;| *()(%%$^/\\\[\]]          # Next character can't be...
	    [^"'><,;|()]{1,})                   # Rest of the characters can't be
	    |
	    ([a-zA-Z0-9_\-/]{1,}/               # Relative endpoint with /
	    [a-zA-Z0-9_\-/]{1,}                 # Resource name
	    \.(?:[a-zA-Z]{1,4}|action)          # Rest + extension (length 1-4 or action)
	    (?:[\?|/][^"|']{0,}|))              # ? mark with parameters
	    |
	    ([a-zA-Z0-9_\-]{1,}                 # filename
	    \.(?:php|asp|aspx|jsp|json|
	         action|html|js|txt|xml)             # . + extension
	    (?:\?[^"|']{0,}|))                  # ? mark with parameters
	  )
	  (?:"|')                               # End newline delimiter
	"""
	pattern = re.compile(pattern_raw, re.VERBOSE)
	result = re.finditer(pattern, str(JS))
	if result == None:
		return None
	js_url = []
	return [match.group().strip('"').strip("'") for match in result
		if match.group() not in js_url]

# Get the page source
def Extract_html(URL, max_retries=3, timeout=10):
	header = {
		"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.108 Safari/537.36",
		"Cookie": args.cookie
	}
	
	for attempt in range(max_retries):
		try:
			raw = requests.get(URL, headers=header, timeout=timeout, verify=False)
			raw.raise_for_status()  # 检查响应状态
			return raw.content.decode("utf-8", "ignore")
		except requests.exceptions.RequestException as e:
			logging.warning(f"Attempt {attempt + 1}/{max_retries} failed for {URL}: {str(e)}")
			if attempt == max_retries - 1:
				logging.error(f"Failed to access {URL} after {max_retries} attempts")
				return None
			time.sleep(2)  # 重试前等待

# Handling relative URLs
def process_url(URL, re_URL):
	black_url = ["javascript:"]	# Add some keyword for filter url.
	URL_raw = urlparse(URL)
	ab_URL = URL_raw.netloc
	host_URL = URL_raw.scheme
	if re_URL[0:2] == "//":
		result = host_URL  + ":" + re_URL
	elif re_URL[0:4] == "http":
		result = re_URL
	elif re_URL[0:2] != "//" and re_URL not in black_url:
		if re_URL[0:1] == "/":
			result = host_URL + "://" + ab_URL + re_URL
		else:
			if re_URL[0:1] == ".":
				if re_URL[0:2] == "..":
					result = host_URL + "://" + ab_URL + re_URL[2:]
				else:
					result = host_URL + "://" + ab_URL + re_URL[1:]
			else:
				result = host_URL + "://" + ab_URL + "/" + re_URL
	else:
		result = URL
	return result

def find_last(string,str):
	positions = []
	last_position=-1
	while True:
		position = string.find(str,last_position+1)
		if position == -1:break
		last_position = position
		positions.append(position)
	return positions

def find_by_url(url, js = False):
	if js == False:
		try:
			logging.info(f"Scanning URL: {url}")
		except:
			logging.error("Please specify a URL like https://www.baidu.com")
			return None
		
		html_raw = Extract_html(url)
		if html_raw == None:
			logging.error(f"Failed to access {url}")
			return None
		
		html = BeautifulSoup(html_raw, "html.parser")
		html_scripts = html.find_all("script")
		script_array = {}
		script_temp = ""
		
		# 添加进度条显示
		logging.info(f"Found {len(html_scripts)} script tags")
		for html_script in tqdm(html_scripts, desc="Processing scripts"):
			script_src = html_script.get("src")
			if script_src == None:
				script_temp += html_script.get_text() + "\n"
			else:
				purl = process_url(url, script_src)
				script_array[purl] = Extract_html(purl)
				
		script_array[url] = script_temp
		allurls = []
		
		# 处理提取的URL
		for script in script_array:
			temp_urls = extract_URL(script_array[script])
			if temp_urls and len(temp_urls) > 0:
				for temp_url in temp_urls:
					allurls.append(process_url(script, temp_url))
					
		# 过滤和去重
		result = []
		url_raw = urlparse(url)
		domain = url_raw.netloc
		positions = find_last(domain, ".")
		miandomain = domain
		if len(positions) > 1:
			miandomain = domain[positions[-2] + 1:]
			
		for singerurl in allurls:
			suburl = urlparse(singerurl)
			subdomain = suburl.netloc
			if miandomain in subdomain or subdomain.strip() == "":
				if singerurl.strip() not in result:
					result.append(singerurl)
					
		return result
	return sorted(set(extract_URL(Extract_html(url)))) or None


def find_subdomain(urls, mainurl):
	url_raw = urlparse(mainurl)
	domain = url_raw.netloc
	miandomain = domain
	positions = find_last(domain, ".")
	if len(positions) > 1:miandomain = domain[positions[-2] + 1:]
	subdomains = []
	for url in urls:
		suburl = urlparse(url)
		subdomain = suburl.netloc
		#print(subdomain)
		if subdomain.strip() == "": continue
		if miandomain in subdomain:
			if subdomain not in subdomains:
				subdomains.append(subdomain)
	return subdomains

def find_by_url_deep(url):
	html_raw = Extract_html(url)
	if html_raw == None:
		logging.error(f"Fail to access {url}")
		return None
		
	html = BeautifulSoup(html_raw, "html.parser")
	html_as = html.find_all("a")
	links = []
	
	for html_a in html_as:
		src = html_a.get("href")
		if src == "" or src == None: continue
		link = process_url(url, src)
		if link not in links:
			links.append(link)
			
	if links == []: return None
	logging.info(f"Found {len(links)} links to process")
	
	urls = []
	# 使用线程池处理链接
	with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
		future_to_url = {executor.submit(find_by_url, link): link for link in links}
		
		# 使用tqdm显示进度
		for future in tqdm(concurrent.futures.as_completed(future_to_url), total=len(links), desc="Processing URLs"):
			link = future_to_url[future]
			try:
				temp_urls = future.result()
				if temp_urls:
					logging.info(f"Found {len(temp_urls)} URLs in {link}")
					urls.extend([url for url in temp_urls if url not in urls])
			except Exception as e:
				logging.error(f"Error processing {link}: {str(e)}")
				
	return urls

	
def find_by_file(file_path, js=False):
	with open(file_path, "r") as fobject:
		links = fobject.read().split("\n")
	if links == []: return None
	print("ALL Find " + str(len(links)) + " links")
	urls = []
	i = len(links)
	for link in links:
		if js == False:
			temp_urls = find_by_url(link)
		else:
			temp_urls = find_by_url(link, js=True)
		if temp_urls == None: continue
		print(str(i) + " Find " + str(len(temp_urls)) + " URL in " + link)
		for temp_url in temp_urls:
			if temp_url not in urls:
				urls.append(temp_url)
		i -= 1
	return urls

def setup_logging(log_level=logging.INFO):
    """配置日志"""
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('jsfinder.log'),
            logging.StreamHandler()
        ]
    )

def generate_html_report(urls, subdomains, scan_info):
    """生成HTML报告"""
    # 确保static目录存在
    os.makedirs('static', exist_ok=True)
    
    # 如果style.css不存在，创建它
    css_path = os.path.join('static', 'style.css')
    if not os.path.exists(css_path):
        with open(css_path, 'w') as f:
            f.write('''body{font-family:sans-serif;margin:40px auto;max-width:1200px;padding:0 20px;background:#fff}
h1{color:#2c3e50;border-bottom:2px solid #eee;padding-bottom:10px}
.info{background:#f8f9fa;padding:15px;border-radius:4px;margin:20px 0}
.results{margin:20px 0}
pre{background:#f8f9fa;padding:15px;border-radius:4px;overflow-x:auto;border:1px solid #eee}''')

    # 使用相对路径引用样式表的HTML模板
    html_content = f'''<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>JSFinder Results</title>
<link rel="stylesheet" href="static/style.css">
</head>
<body>
<div class="container">
    <h1>JSFinder Scan Results</h1>
    <div class="info">
        <p><b>Target:</b> {scan_info['target']}</p>
        <p><b>Scan Time:</b> {scan_info['timestamp']}</p>
        <p><b>Duration:</b> {scan_info['duration']:.2f} seconds</p>
    </div>
    <div class="results">
        <h2>Found URLs <span class="count">{len(urls)}</span></h2>
        <pre>{chr(10).join(urls)}</pre>
    </div>
    <div class="results">
        <h2>Found Subdomains <span class="count">{len(subdomains)}</span></h2>
        <pre>{chr(10).join(subdomains)}</pre>
    </div>
</div>
</body>
</html>'''

    return html_content

def load_blacklist():
    """加载黑名单配置"""
    try:
        from config import URL_BLACKLIST
        logging.info("Loaded URL blacklist from config.py")
        return URL_BLACKLIST
    except ImportError:
        logging.info("No blacklist config found, continuing without filtering")
        return None

def should_filter_url(url, blacklist):
    """检查URL是否应该被过滤"""
    if not blacklist:
        return False
        
    parsed_url = urlparse(url)
    
    # 检查域名黑名单
    if any(domain in parsed_url.netloc for domain in blacklist.get('domains', [])):
        return True
        
    # 检查文件扩展名
    if any(url.lower().endswith(ext) for ext in blacklist.get('extensions', [])):
        return True
        
    # 检查URL关键词
    if any(keyword in url.lower() for keyword in blacklist.get('keywords', [])):
        return True
        
    return False

def giveresult(urls, domain, start_time):
    if urls == None:
        logging.warning("No results found")
        return None
    
    # 加载黑名单配置
    blacklist = load_blacklist()
    
    # 如果有黑名单配置，进行过滤
    if blacklist:
        filtered_urls = [url for url in urls if not should_filter_url(url, blacklist)]
        logging.info(f"Filtered {len(urls) - len(filtered_urls)} URLs using blacklist")
        urls = filtered_urls
    
    logging.info(f"Found {len(urls)} URLs")
    content_url = ""
    content_subdomain = ""
    
    print("\n=== Found URLs ===")
    for url in urls:
        content_url += url + "\n"
        print(f"  {url}")
        
    subdomains = find_subdomain(urls, domain)
    print(f"\n=== Found {len(subdomains)} Subdomains ===")
    
    for subdomain in subdomains:
        content_subdomain += subdomain + "\n"
        print(f"  {subdomain}")
    
    # 只在指定-o参数时生成HTML报告
    if args.output:
        # 生成报告
        scan_info = {
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'target': domain,
            'duration': time.time() - start_time
        }
        
        html_report = generate_html_report(urls, subdomains, scan_info)
        
        # 使用指定的文件名保存HTML报告
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(html_report)
        logging.info(f"HTML report saved to {args.output}")
    
    # 保存原始结果
    if args.outputurl:
        with open(args.outputurl, "a", encoding='utf-8') as f:
            f.write(content_url)
        logging.info(f"URLs saved to {args.outputurl}")
        
    if args.outputsubdomain:
        with open(args.outputsubdomain, "a", encoding='utf-8') as f:
            f.write(content_subdomain)
        logging.info(f"Subdomains saved to {args.outputsubdomain}")

if __name__ == "__main__":
	urllib3.disable_warnings()
	args = parse_args()
	
	# 设置日志
	setup_logging()
	
	start_time = time.time()  # 记录开始时间
	
	try:
		if args.file == None:
			if args.deep is not True:
				urls = find_by_url(args.url)
				giveresult(urls, args.url, start_time)  # 传入start_time
			else:
				urls = find_by_url_deep(args.url)
				giveresult(urls, args.url, start_time)  # 传入start_time
		else:
			if args.js is not True:
				urls = find_by_file(args.file)
				giveresult(urls, urls[0] if urls else None, start_time)  # 传入start_time
			else:
				urls = find_by_file(args.file, js=True)
				giveresult(urls, urls[0] if urls else None, start_time)  # 传入start_time
	except Exception as e:
		logging.error(f"An error occurred: {str(e)}")
		sys.exit(1)
