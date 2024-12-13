import pandas as pd
import requests
import random
import time
import html
import os

from utils import tb_database
from utils import tb_crawlers
import threads_fetch

random_sleep_min_time = 3
random_sleep_max_time = 5
def random_sleep():
    time.sleep(random.randint(random_sleep_min_time, random_sleep_max_time))

def download_post(tid, pn=1, db_name="database"):
    headers = {
        'User-Agent': 'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.1; WOW64; Trident/4.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; .NET4.0C; InfoPath.3)'
    }
    database = tb_database.Database(db_name)

    crawlers = {'user': tb_crawlers.user_crawler(), 
                'badge': tb_crawlers.badge_crawler(), 
                'post': tb_crawlers.post_crawler()}

    # 获取回帖
    request = requests.get("https://tieba.baidu.com/p/" + tid + "?pn=" + str(pn), headers=headers).text
    request = html.unescape(request)
    for crawler in crawlers.values():
        crawler.feed(request)

    posts = []
    for elm in crawlers["post"].data:
        posts.append([int(tid), *elm])

    database.add_user(crawlers["user"].data)
    database.add_badge(crawlers["badge"].data)
    database.add_post(posts)

    # 调试信息
    for idx, user in enumerate(crawlers["user"].data):
        b = database.get_full_user_by_id(user[0])
        print(b.loc[:,["username", "badge", "badge_lv"]])

    for crawler in crawlers.values():
        crawler.reset()

    # # 空回复处理
    # if crawlers["post"].reply_indicator_list == []:
    #     print("没有回复")
    #     crawlers["post"].reply_indicator_list.append(["", "", "", "", ""])

    return {'pids_have_replies':crawlers["post"].reply_indicator_list, 
            'pids_have_resources':crawlers["post"].resource_list, 
            'has_next_page':"下一页" in request}

def download_reply(tid, pid, pn=1, db_name="database"):
    headers = {
        'User-Agent': 'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.1; WOW64; Trident/4.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; .NET4.0C; InfoPath.3)'
    }
    
    database = tb_database.Database(db_name)
    reply_cwl = tb_crawlers.reply_crawler()
    home_cwl = tb_crawlers.home_crawler()

    # 获取回复
    print("正在获取回复" + str(pn) + " 页          \r", end="")
    request = requests.get("https://tieba.baidu.com/p/comment?tid=" + tid + "&pid=" + pid + "&pn=" + str(pn), headers=headers).text
    reply_cwl.feed(request)
    
    rep_list = []
    for idx in range(len(reply_cwl.data)):
        hold = database.get_user_by_portrait(reply_cwl.users[idx][1].split("&")[0].split("=")[-1])
        if len(hold) == 0:
            random_sleep()
            print("正在获取用户" + str(idx) + " 页          \r", end="")
            request = requests.get("https://tieba.baidu.com" + reply_cwl.users[idx][1]).text
            home_cwl.feed(request)
            try:
                reply_cwl.link_users(idx, home_cwl.data[0])
                database.add_badge(home_cwl.badges)
            except:
                print("无法获取用户信息")
                print("https://tieba.baidu.com" + reply_cwl.users[idx][1])
            home_cwl.reset()
        else:
            reply_cwl.link_users(idx, hold.iloc[0,0])
        rep_list.append([int(i), *reply_cwl.data[idx]])
    
    database.add_reply(rep_list)
    database.add_user(reply_cwl.users)
    
    for idx, user in enumerate(reply_cwl.users):
        b = database.get_full_user_by_id(user[0])
        print(b.loc[:,["username", "badge", "badge_lv"]])

    # reply_cwl.reset()

    return {'has_next_page':("下一页" in request)}

def download_resource(tid, pid, db_name="database"):
    pass


def download_thread(thread_id, download_resources=False):
    headers = {
        'User-Agent': 'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.1; WOW64; Trident/4.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; .NET4.0C; InfoPath.3)'
    }
    database = tb_database.Database("database")

    crawlers = {'user': tb_crawlers.user_crawler(), 
                'badge': tb_crawlers.badge_crawler(), 
                'post': tb_crawlers.post_crawler(),
                'reply': tb_crawlers.reply_crawler(),
                'resource': tb_crawlers.resource_crawler()}
    reply_cwl = tb_crawlers.reply_crawler()
    home_cwl = tb_crawlers.home_crawler()

    # 获取回帖
    pn = 1
    last_layer = database.get_last_layer_by_tid(int(thread_id))
    if pd.notna(last_layer):
        pn = last_layer//15
        print("最后更新于第 " + str(pn) + " 页")
    else:
        print("没有回帖")

    while True:
        jump = False
        random_sleep()
        print("正在获取第 " + str(pn) + " 页          \r", end="")
        request = requests.get("https://tieba.baidu.com/p/" + thread_id + "?pn=" + str(pn), headers=headers).text
        request = html.unescape(request)
        for crawler in crawlers.values():
            crawler.feed(request)
        database.add_user(crawlers["user"].data)
        database.add_badge(crawlers["badge"].data)
        posts = []
        for elm in crawlers["post"].data:
            posts.append([int(thread_id), *elm])
        database.add_post(posts)


        for idx, user in enumerate(crawlers["user"].data):
            b = database.get_full_user_by_id(user[0])
            print(b.loc[:,["username", "badge", "badge_lv"]])
    
        if "下一页" in request:
            jump = True
            

        # 获取回复
        for i in crawlers["post"].reply_indicator_list:
            hold = database.get_reply_by_post_id(i)
            if len(hold) > 0:
                continue
            random_sleep()
            counter = 1
            while True:
                print("正在获取回复" + str(counter) + " 页          \r", end="")
                request = requests.get("https://tieba.baidu.com/p/comment?tid=" + thread_id + "&pid=" + i + "&pn=" + str(counter), headers=headers).text
                crawlers["reply"].feed(request)
                reply_cwl.feed(request)
                
                rep_list = []
                for idx in range(len(reply_cwl.data)):
                    hold = database.get_user_by_portrait(reply_cwl.users[idx][1].split("&")[0].split("=")[-1])
                    if len(hold) == 0:
                        random_sleep()
                        print("正在获取用户" + str(idx) + " 页          \r", end="")
                        request = requests.get("https://tieba.baidu.com" + reply_cwl.users[idx][1]).text
                        home_cwl.feed(request)
                        try:
                            reply_cwl.link_users(idx, home_cwl.data[0])
                            database.add_badge(home_cwl.badges)
                        except:
                            print("无法获取用户信息")
                            print("https://tieba.baidu.com" + reply_cwl.users[idx][1])
                        home_cwl.reset()
                    else:
                        reply_cwl.link_users(idx, hold.iloc[0,0])
                    rep_list.append([int(i), *reply_cwl.data[idx]])
                
                database.add_reply(rep_list)
                database.add_user(reply_cwl.users)
                
                for idx, user in enumerate(reply_cwl.users):
                    b = database.get_full_user_by_id(user[0])
                    print(b.loc[:,["username", "badge", "badge_lv"]])

                reply_cwl.reset()

                if "下一页" in request:
                    counter += 1
                else:
                    break
        # 空回复处理
        if crawlers["post"].reply_indicator_list == []:
            print("没有回复")
            crawlers["post"].reply_indicator_list.append(["", "", "", "", ""])

        # 获取图片资源
        if download_resources:
            for i in range(len(crawlers["resource"].data)):           # 遍历每层楼
                rsc_list = []
                for j in range(len(crawlers["resource"].data[i][1])): # 遍历每个资源
                    fname = crawlers["resource"].data[i][1][j].replace('?', '/').split('/')[-2]
                    if os.path.exists('resources/' + fname):
                        continue
                    random_sleep()
                    print("正在获取资源" + str(i) + "/" + str(len(crawlers["resource"].data)) + " 页")
                    img = requests.get(crawlers["resource"].data[i][1][j]).content
                    
                    with open('resources/' + fname, 'wb') as f:
                        f.write(img)
                    rsc_list.append([int(thread_id), int(crawlers["resource"].data[i][0]), fname])
                database.add_resource(rsc_list)
                rsc_list.clear()
            
        for crawler in crawlers.values():
            crawler.reset()
        
        if jump:
            pn += 1
        else:
            break

    return crawlers["post"].data, crawlers["resource"].data

def fetch_threads(forum_name):
    headers = {
        'User-Agent': 'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.1; WOW64; Trident/4.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; .NET4.0C; InfoPath.3)'
    }

    forum_parser = threads_fetch.forum_parser()
    thread_cwl = tb_crawlers.thread_crawler()

    request = requests.get("https://tieba.baidu.com/f?kw="+forum_name, headers=headers).text
    request = html.unescape(request)
    forum_parser.feed(request)
    thread_cwl.feed(request)

    return thread_cwl.data

if __name__ == "__main__":
    pass