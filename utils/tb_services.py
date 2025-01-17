from html.parser import HTMLParser
import pandas as pd
import numpy as np
import threading
import requests
import random
import time
import html
import json
import wx
import re

from utils import tb_crawlers

HEADERS = {
    'User-Agent': 'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.1; WOW64; Trident/4.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; .NET4.0C; InfoPath.3)'
}

def fetch_thread(kw):
    thread_crawler = tb_crawlers.ThreadDataCrawler()

    request = requests.get("https://tieba.baidu.com/f?kw=" + str(kw), headers=HEADERS).text
    request = html.unescape(request)
    thread_crawler.feed(request)

    return thread_crawler.thread_list

def fetch_thread_info(thread_id):
    request = requests.get("https://tieba.baidu.com/p/" + str(thread_id), headers=HEADERS).text
    # request = html.unescape(request)

    try:
        forum_info_head = request.index("PageData.forum = {")
        forum_info_begin = request.index("{", forum_info_head)
        forum_info_end = request.index(";", forum_info_begin)
        forum_info = request[forum_info_begin:forum_info_end].replace("\'", "\"").replace("\\", "")
        forum_info = re.sub(r'(\b\w+\b): ', r'"\1":', forum_info)
        forum_info = json.loads(forum_info)
    except json.JSONDecodeError as e:
        print(e)
        print(forum_info)
        exit()
    
    try:
        thread_info_head = request.index("PageData.thread = {")
        thread_info_begin = request.index("{", thread_info_head)
        thread_info_end = request.index(";", thread_info_begin)
        thread_info = request[thread_info_begin:thread_info_end].replace("\'", "\"").replace("\\", "").replace("/*null,*/", "")
        thread_info = re.sub(r'(\b\w+\b):', r'"\1":', thread_info)
        thread_info = json.loads(thread_info)
    except json.JSONDecodeError as e:
        print(e)
        print(thread_info)
        exit()

    forum_data = {
        "forum_id": forum_info['forum_id'],
        "forum_name": forum_info['forum_name']}
    thread_data = {
        "forum_id": forum_info['forum_id'],
        "thread_id": thread_info['thread_id'],
        "thread_title": thread_info['title'],
        "abstract": "",
        "reply_num": thread_info['reply_num']
    }
    return forum_data, thread_data

def fetch_post(thread_id, pn=1):
    post_crawler = tb_crawlers.PostDataCrawler()

    print("正在获取" + str(thread_id) + "第" + str(pn) + "页          \r", end="")
    request = requests.get("https://tieba.baidu.com/p/" + str(thread_id) + "?pn=" + str(pn), headers=HEADERS).text
    post_crawler.feed(request)

    hasNext = False
    if "下一页" in request:
        hasNext = True

    return post_crawler.user_list, \
        post_crawler.badge_list, \
            post_crawler.post_list, \
                post_crawler.reply_indicator_list, \
                    post_crawler.resource_list, \
                        hasNext, post_crawler.max_page

def fetch_reply(thread_id, post_id, pn=1):
    reply_crawler = tb_crawlers.ReplyDataCrawler()
    
    print("正在获取" + str(thread_id) + "第" + str(pn) + "页          \r", end="")
    request = requests.get("https://tieba.baidu.com/p/comment?tid=" + str(thread_id) + "&pid=" + str(post_id) + "&pn=" + str(pn), headers=HEADERS).text
    request = html.unescape(request)
    reply_crawler.feed(request)

    hasNext = False
    if "下一页" in request:
        hasNext = True

    return reply_crawler.user_list, \
        reply_crawler.reply_list, \
            hasNext

def fetch_home(portrait, username="", use82=False):
    if use82:
        home_crawler = tb_crawlers.HomeDataCrawler82()
        print("正在获取首页          \r", end="")
        user_info_request = requests.get("https://124.221.26.245/tieba/info/" + username, headers=HEADERS, verify=False).text
        forum_info_request = requests.get("https://124.221.26.245/tieba/forum/" + username + "/1", headers=HEADERS, verify=False).text
        user_info = html.unescape(user_info_request)
        forum_info = html.unescape(forum_info_request)
        home_crawler.feed(user_info, forum_info)
    else:
        home_crawler = tb_crawlers.HomeDataCrawler()
        print("正在获取首页          \r", end="")
        request = requests.get("https://tieba.baidu.com/home/main?id=" + portrait + "&ie=utf-8&fr=pb", headers=HEADERS).text
        request = html.unescape(request)
        home_crawler.feed(request)

    return home_crawler.user_id, home_crawler.user_portrait, home_crawler.user_name, home_crawler.user_nickname, home_crawler.badges, home_crawler.forums

if __name__ == "__main__":
    fetch_thread_info(9352056700)