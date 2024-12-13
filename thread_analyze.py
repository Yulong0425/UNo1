import threads_fetch
import post_fetch_lab as posts_fetch
import replies_fetch
import threading

from utils.tb_crawlers import user_crawler, badge_crawler, post_crawler, reply_crawler, home_crawler
from utils.tb_database import Database

import pandas as pd
import requests
import html
import random
import time
import sys
import os

tmp = Database("database")

def random_stop():
    secs = random.randint(3, 5)
    print("随机时停" + str(secs) + "秒          \r", end="")
    time.sleep(secs)

def fetch_thread(thread_id):
    home_cwl = home_crawler()
    # 获取回帖
    pn = 1
    last_layer = tmp.get_last_layer_by_tid(int(thread_id))
    if pd.notna(last_layer):
        pn = last_layer//15
        print("最后更新于第 " + str(pn) + " 页")
    else:
        print("没有回帖")

    while True:
        random_stop()
        print("正在获取第 " + str(pn) + " 页          \r", end="")
        request = requests.get("https://tieba.baidu.com/p/" + thread_id + "?pn=" + str(pn), headers=headers).text
        request = html.unescape(request)
        thread_parser.feed(request)
        for crawler in crawlers.values():
            crawler.feed(request)
        tmp.add_user(crawlers["user"].data)
        tmp.add_badge(crawlers["badge"].data)
        posts = []
        for elm in crawlers["post"].data:
            posts.append([thread_id, *elm])
        tmp.add_post(posts)


        for idx, user in enumerate(crawlers["user"].data):
            b = tmp.get_full_user_by_id(user[0])
            print(b.loc[:,["username", "badge", "badge_lv"]])

        for crawler in crawlers.values():
            crawler.reset()
        

        if "下一页" in request:
            pn += 1
        else:
            break
    
    # 获取回复
    for i in thread_parser.reply_list:
        random_stop()
        counter = 1
        while True:
            print("正在获取回复" + str(counter) + " 页          \r", end="")
            request = requests.get("https://tieba.baidu.com/p/comment?tid=" + thread_id + "&pid=" + i + "&pn=" + str(counter), headers=headers).text
            reply_parser.feed(request, i)
            reply_cwl.feed(request)
            
            rep_list = []
            for idx in range(len(reply_cwl.data)):
                hold = tmp.get_user_by_portrait(reply_cwl.users[idx][1].split("&")[0].split("=")[-1])
                if len(hold) == 0:
                    random_stop()
                    print("正在获取用户" + str(idx) + " 页          \r", end="")
                    request = requests.get("https://tieba.baidu.com" + reply_cwl.users[idx][1]).text
                    home_cwl.feed(request)
                    reply_cwl.link_users(idx, home_cwl.data[0])
                    home_cwl.reset()
                else:
                    reply_cwl.link_users(idx, hold.iloc[0,0])
                rep_list.append([int(i), *reply_cwl.data[idx]])
            tmp.add_reply(rep_list)
            tmp.add_user(reply_cwl.users)
            reply_cwl.reset()

            if "下一页" in request:
                counter += 1
            else:
                break
    # 空回复处理
    if reply_parser.reply_list == []:
        print("没有回复")
        reply_parser.reply_list.append(["", "", "", "", ""])

    # 获取图片资源
    for i in range(len(thread_parser.resource_list)):           # 遍历每层楼
        for j in range(len(thread_parser.resource_list[i][1])): # 遍历每个资源
            random_stop()
            print("正在获取资源" + str(i) + "/" + str(len(thread_parser.resource_list)) + " 页")
            img = requests.get(thread_parser.resource_list[i][1][j]).content
            fname = thread_parser.resource_list[i][1][j].replace('?', '/').split('/')[-2]
            # print(thread_parser.post_list[i])
            # print(j)
            thread_parser.post_list[i][6+j] = fname
            with open('resources/' + fname, 'wb') as f:
                f.write(img)
                
    return thread_parser.post_list, reply_parser.reply_list

def save_thread(thread_id, post_list, reply_list):
    # 存储

    if not os.path.exists("threads/" + thread_id + "_posts.csv"):
        print("正在保存帖子" + thread_id)
        pd.DataFrame(post_list).to_csv("threads/" + thread_id + "_posts.csv", encoding="utf-8", index=False)
        pd.DataFrame(reply_list).to_csv("threads/" + thread_id + "_replies.csv", encoding="utf-8", index=False)
    else:
        print("正在更新帖子" + thread_id)
        prev_posts = pd.read_csv("threads/" + thread_id + "_posts.csv").astype(str)
        prev_posts_list = prev_posts.iloc[:, 0].tolist()
        for i in range(len(post_list)):
            if not post_list[i][0] in prev_posts_list:
                prev_posts = pd.concat([prev_posts, pd.DataFrame([post_list[i]], columns=prev_posts.columns)], ignore_index=True)
                
        prev_replies = pd.read_csv("threads/" + thread_id + "_replies.csv").astype(str)
        prev_replies_list = prev_replies.iloc[:, -1].tolist()
        for i in range(len(reply_list)):
            if not reply_list[i][-1] in prev_replies_list:
                prev_replies = pd.concat([prev_replies, pd.DataFrame([reply_list[i]], columns=prev_replies.columns)], ignore_index=True)

        prev_posts.to_csv("threads/" + thread_id + "_posts.csv", encoding="utf-8", index=False)
        prev_replies.to_csv("threads/" + thread_id + "_replies.csv", encoding="utf-8", index=False)

if __name__ == "__main__":
    db = Database("./database")

    thread = db.get_full_thread_by_id(int(sys.argv[1]))
    for idx, data in thread.iterrows():

        badges = db.get_full_user_by_id(data['user_id'])
        p = badges.loc[:,["username", "badge", "badge_lv"]]
        if not p.empty:
            print(p)
