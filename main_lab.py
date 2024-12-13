from utils.tb_crawlers import user_crawler, badge_crawler, post_crawler, reply_crawler, home_crawler, resource_crawler
from utils.tb_database import Database

import threads_fetch

from lxml import etree
import argparse
import threading
import pandas as pd
import requests
import html
import random
import time
import sys
import os

tmp = Database("database")

def get_title(request):
    parse_html=etree.HTML(request)

    title = parse_html.xpath('//div[@class="core_title_wrap_bright clearfix"]/h3/text()')[0]
    # print(title)
    reply_num = parse_html.xpath('//li[@class="l_reply_num"]/span[1]/text()')[0]
    return [title.strip(), reply_num]

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
        jump = False
        random_stop()
        print("正在获取第 " + str(pn) + " 页          \r", end="")
        request = requests.get("https://tieba.baidu.com/p/" + thread_id + "?pn=" + str(pn), headers=headers).text
        request = html.unescape(request)
        for crawler in crawlers.values():
            crawler.feed(request)
        tmp.add_user(crawlers["user"].data)
        tmp.add_badge(crawlers["badge"].data)
        posts = []
        for elm in crawlers["post"].data:
            posts.append([int(thread_id), *elm])
        tmp.add_post(posts)


        for idx, user in enumerate(crawlers["user"].data):
            b = tmp.get_full_user_by_id(user[0])
            print(b.loc[:,["username", "badge", "badge_lv"]])
    
        if "下一页" in request:
            jump = True
            

        # 获取回复
        for i in crawlers["post"].reply_indicator_list:
            hold = tmp.get_reply_by_post_id(i)
            if len(hold) > 0:
                continue
            random_stop()
            counter = 1
            while True:
                print("正在获取回复" + str(counter) + " 页          \r", end="")
                request = requests.get("https://tieba.baidu.com/p/comment?tid=" + thread_id + "&pid=" + i + "&pn=" + str(counter), headers=headers).text
                crawlers["reply"].feed(request)
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
                        tmp.add_badge(home_cwl.badges)
                        home_cwl.reset()
                    else:
                        reply_cwl.link_users(idx, hold.iloc[0,0])
                    rep_list.append([int(i), *reply_cwl.data[idx]])
                
                tmp.add_reply(rep_list)
                tmp.add_user(reply_cwl.users)
                
                for idx, user in enumerate(reply_cwl.users):
                    b = tmp.get_full_user_by_id(user[0])
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
        if len(sys.argv) > 3 and sys.argv[3] == "r":
            for i in range(len(crawlers["resource"].data)):           # 遍历每层楼
                rsc_list = []
                for j in range(len(crawlers["resource"].data[i][1])): # 遍历每个资源
                    fname = crawlers["resource"].data[i][1][j].replace('?', '/').split('/')[-2]
                    if os.path.exists('resources/' + fname):
                        continue
                    random_stop()
                    print("正在获取资源" + str(i) + "/" + str(len(crawlers["resource"].data)) + " 页")
                    img = requests.get(crawlers["resource"].data[i][1][j]).content
                    
                    with open('resources/' + fname, 'wb') as f:
                        f.write(img)
                    rsc_list.append([int(thread_id), int(crawlers["resource"].data[i][0]), fname])
                tmp.add_resource(rsc_list)
                rsc_list.clear()
            
        for crawler in crawlers.values():
            crawler.reset()
        
        if jump:
            pn += 1
        else:
            break

    return crawlers["post"].data, crawlers["resource"].data


# parser = argparse.ArgumentParser(description='有男不玩UNo1-存档/补档机')
# parser.add_argument('--forum', metavar='N', help='输入吧名（不带“吧”字）。例：原神内鬼')
# parser.add_argument('--tid', type=int, metavar='T', help='input batch size for training (default: 128)')
# parser.add_argument('--test-batch-size', type=int, default=128, metavar='N',
#                     help='input batch size for testing (default: 128)')
# parser.add_argument('--epochs', type=int, default=100, metavar='N',
#                     help='number of epochs to train')
# parser.add_argument('--lr', type=float, default=0.01, metavar='LR',
#                     help='learning rate')
# parser.add_argument('--momentum', type=float, default=0.9, metavar='M',
#                     help='SGD momentum')
# parser.add_argument('--no-cuda', action='store_true', default=False,
#                     help='disables CUDA training')
# parser.add_argument('--epsilon', default=0.3,
#                     help='perturbation')
# parser.add_argument('--num-steps', default=40,
#                     help='perturb number of steps')
# parser.add_argument('--step-size', default=0.01,
#                     help='perturb step size')
# parser.add_argument('--beta', default=1.0,
#                     help='regularization, i.e., 1/lambda in TRADES')
# parser.add_argument('--seed', type=int, default=1, metavar='S',
#                     help='random seed (default: 1)')
# parser.add_argument('--log-interval', type=int, default=100, metavar='N',
#                     help='how many batches to wait before logging training status')
# parser.add_argument('--model-dir', default='./model-mnist-smallCNN',
#                     help='directory of model for saving checkpoint')
# parser.add_argument('--save-freq', '-s', default=5, type=int, metavar='N',
#                     help='save frequency')
# args = parser.parse_args()


if __name__ == "__main__":
    headers = {
        'User-Agent': 'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.1; WOW64; Trident/4.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; .NET4.0C; InfoPath.3)'
    }

    print(tmp.posts.columns.dtype)

    crawlers = {'user': user_crawler(), 
                'badge': badge_crawler(), 
                'post': post_crawler(),
                'reply': reply_crawler(),
                'resource': resource_crawler()}
    reply_cwl = reply_crawler()

    forum_parser = threads_fetch.forum_parser()

    thread_fetch_list = []
    forum = '孙笑川吧'
    match sys.argv[1]:
        case '0':
            # 参数获取
            kw = sys.argv[2]# 网页获取
            forum = sys.argv[2] + '吧'
            tmp.add_forum([forum])
            random_stop()
            request = requests.get("https://tieba.baidu.com/f?kw="+kw, headers=headers).text
            request = html.unescape(request)
            forum_parser.feed(request)

            # 打印帖子
            for i in range(len(forum_parser.threads_list)):
                print(str(i) + "：" + forum_parser.threads_list[i][1] + " | 楼层：" + forum_parser.threads_list[i][2])
            
            thread_num = input("输入帖子序号: ")
            if thread_num == "all":
                thread_fetch_list = forum_parser.threads_list
            else:
                while int(thread_num) > -1:
                    thread_fetch_list.append(forum_parser.threads_list[int(thread_num)])
                    thread_num = input("输入帖子序号: ")
        case '1':
            request = requests.get("https://tieba.baidu.com/p/" + sys.argv[2] + "?pn=1", headers=headers).text
            request = html.unescape(request)
            
            parse_html=etree.HTML(request)
            badge_bds = '//a[@class="card_title_fname"]/text()'
            try:
                forum = parse_html.xpath(badge_bds)[0].strip()
            except:
                badge_bds = '//a[@class="plat_title_h3"]/text()'
                forum = parse_html.xpath(badge_bds)[0].strip()
                print("badge error")
                print(parse_html.xpath(badge_bds))
            tmp.add_forum([forum])
    
            title = get_title(request)
            thread_fetch_list.append(['/p/' + sys.argv[2], title[0], title[1]])

        case '2':
            thread_list = pd.read_csv("thread_list.csv")

            for idx, thread_info in thread_list.iterrows():
                print(str(idx) + "：" + str(thread_info[1]) + " | 楼层：" + str(thread_info[2]))
            thread_fetch_list = []
            thread_num = input("输入帖子序号: ")
            while int(thread_num) > -1:
                thread_fetch_list.append(thread_list.iloc[int(thread_num)].to_list())
                thread_num = input("输入帖子序号: ")

    for thread in thread_fetch_list:
        print("正在获取帖子：" + thread[1] + " | 楼层：" + str(thread[2]))
        thread_id = str(thread[0]).split('/')[2]
        
        tmp.add_thread([[tmp.forums[tmp.forums['forum_name'] == forum].index[0], thread_id, thread[1], thread[2]]])
        post_list, reply_list = fetch_thread(thread_id)
