# 黑名单配置
URL_BLACKLIST = {
    # 域名黑名单
    'domains': [
        'google-analytics.com',
        'doubleclick.net',
        'googleapis.com',
        'gstatic.com',
    ],
    
    # 文件扩展名黑名单
    'extensions': [
        '.png', '.jpg', '.jpeg', '.gif', '.css',
        '.mp4', '.mp3', '.mov', '.avi', '.wmv',
        '.flv', '.ico', '.woff', '.woff2', '.ttf',
    ],
    
    # URL关键词黑名单
    'keywords': [
        'javascript:',
        'mailto:',
        'tel:',
        'data:',
        'about:',
        'file:',
    ]
}
