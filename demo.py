import requests
import time
import execjs
from lxml import etree
from fake_useragent import UserAgent

headers = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'referer': 'https://music.163.com/',
    'user-agent': UserAgent().random,
}


def parse_comment_id(song_id):
    resp = requests.get('https://music.163.com/song?id=%s' % song_id, headers=headers)
    resp.encoding = 'utf-8'
    doc = etree.HTML(resp.text)
    tid = doc.xpath('//div[@id="comment-box"]/@data-tid')[0]
    return tid


def parse_comments(tid, page_num):
    data = {
        "rid": tid,
        "threadId": tid,
        "pageNo": str(page_num),
        "pageSize": "20",
        "cursor": int(time.time()*1000),
        "offset": (page_num - 1) * 20,
        "orderType":"1",
        "csrf_token":""
    }

    with open('encrypt_comment.js', 'r', encoding='utf-8') as f:
        content = f.read()

    ctx = execjs.compile(content)
    wb_data = ctx.call('encrypt_params', str(data))
    data = {
        'params': wb_data.get('encText'),
        'encSecKey': wb_data.get('encSecKey'),
    }
    search_api = 'https://music.163.com/weapi/comment/resource/comments/get?'
    params = {
        'csrf_token': ''
    }
    resp = requests.post(search_api, params=params, headers=headers, data=data)

    if resp.status_code == 200:
        items = resp.json().get('data').get('comments')
        for item in items:
            comment = item.get('content')
            print(comment)
    else:
        print(resp.status_code)


def start(song_id):
    tid = parse_comment_id(song_id)
    for i in range(1, 100):
        print('正在抓取第%s页评论...' % i)
        parse_comments(tid, i)
        time.sleep(2)


if __name__ == '__main__':
    start('1488737309')