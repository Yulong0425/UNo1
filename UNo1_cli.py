import pandas as pd
import threading
import requests
import argparse
import random
import html
import time
import re
import os

from utils import tb_database
from utils import tb_services
from utils import tb_aux

class UNo1_cli():

    # Config
    db = tb_database.Database("database")
    min_wait_time = 1
    max_wait_time = 5

    # Status
    download_status = 0
    download_progress = 0

    # Data
    watchlist = []
    marked_users = []
    download_queue = []

    # Constructor
    def __init__(self):
        pass

    # Func
    def update_thread_list(self, kw, args=None):        
        self.watchlist = tb_services.fetch_thread(kw)
        for idx, thread in enumerate(self.watchlist):
            print(idx, thread['thread_title'], thread['reply_num'])
        while True:
            idx = int(input("请输入帖子:"))
            if idx < 0:
                break
            self.download_queue.append(self.watchlist[idx])
        
        self.download_thread_queue(args)
    
    def download_thread_queue(self, args=None):
        while len(self.download_queue) > 0:
            thread = self.download_queue.pop(0)
            self.download_thread(thread['thread_id'], args)

    def mark_user(self, user_id, username=None):
        # Read Badges by user_id and then join to forums
        badges = self.db.read(table_name="badges", user_id=user_id)
        red_district_names = ["有男偷玩", "异色格", "新男权", "二游笑话", "快乐雪花", "北落野", "原神滑坡"]

        rds = {}
        for rdn in red_district_names:
            rd = self.db.read(table_name="forums", forum_name=rdn)
            rds.update({rd['forum_id'].values[0]: rdn})

        red_district_components = []
        for idx, badge in badges.iterrows():
            forum_id = badge['forum_id']
            if forum_id in rds.keys():
                red_district_components.append({"forum_name": rds[forum_id], "badge_lv": badge['badge_lv']})
        
        if username is not None:
            if len(red_district_components) > 0:
                print(f"用户{user_id}({username})被标记为: ", end="")
                for idx, badge in enumerate(red_district_components):
                    if badge['badge_lv'] > 1:
                        print(f"{badge['forum_name']}成分({badge['badge_lv']}级) ", end="")
                    if badge['badge_lv'] == 1:
                        print(f"{badge['forum_name']}发过言 ", end="")
                print()

        return {"user_id": user_id, "badges": red_district_components}
        
    def download_thread(self, thread_id, args=None):
        # 默认参数
        download_resources=False
        show_user=False
        marking_user=False

        # 获取参数
        if args is not None:
            download_resources=args.resource
            show_user=args.user
            marking_user=args.mark

        forum_data, thread_data = tb_services.fetch_thread_info(thread_id)
        self.db.create(table_name="forums", records=[forum_data])
        self.db.create(table_name="threads", records=[thread_data])

        # 获取回帖
        pn = 1
        print(thread_id)
        last_layer = self.db.read(table_name="posts", thread_id=int(thread_id))["layer"].max()

        if pd.notna(last_layer):
            pn = last_layer//15
            print("最后更新于第 " + str(pn) + " 页")
        else:
            print("没有回帖")

        while True:
            tb_aux.random_sleep(self.min_wait_time, self.max_wait_time)
            print("正在获取第 " + str(pn) + " 页          \r", end="")
            post_data = tb_services.fetch_post(thread_id, pn)
            user_list = post_data[0]
            badge_list = post_data[1]
            post_list = post_data[2]
            
            if marking_user:
                for user in user_list:
                    self.mark_user(user['user_id'], user['username'])

            max_page = post_data[6]
            self.download_progress = pn/max_page
            self.db.create(table_name="users", records=user_list)
            self.db.create(table_name="badges", records=badge_list)
            self.db.create(table_name="posts", records=post_list)

            if show_user:
                for user in user_list:
                    print(user)

            # 获取回复
            reply_indicator_list = post_data[3]
            for post_id, comment_num in reply_indicator_list:
                hold = self.db.read(table_name="replies", post_id=post_id)
                if len(hold) > 0:
                    continue
                tb_aux.random_sleep(self.min_wait_time, self.max_wait_time)
                reply_pn = 1
                while True:
                    print("正在获取回复" + str(reply_pn) + " 页          \r", end="")
                    reply_data = tb_services.fetch_reply(thread_id, post_id, reply_pn)
                    reply_user_list = reply_data[0]
                    reply_list = reply_data[1]
                    reply_hasNext = reply_data[2]

                    for idx, reply in enumerate(reply_list):
                        reply['post_id'] = post_id
                        hold = self.db.read(table_name="users", portrait=reply['user_portrait_from'])
                        if len(hold) == 0:
                            tb_aux.random_sleep(self.min_wait_time, self.max_wait_time)
                            print("正在获取用户" + str(idx) + " 页          \r", end="")
                            home_data = tb_services.fetch_home(reply['user_portrait_from'])
                            reply_user_list[idx]['user_id'] = home_data[0]
                            self.db.create(table_name="forums", records=home_data[-1])
                            self.db.create(table_name="badges", records=home_data[4])
                        else:
                            reply_user_list[idx]['user_id'] = hold['user_id'].values[0]
                        if show_user:
                            print(reply_user_list[idx])
                    
                    if marking_user:
                        for user in reply_user_list:
                            self.mark_user(user['user_id'], user['username'])

                    self.db.create(table_name="users", records=reply_user_list)
                    self.db.create(table_name="replies", records=reply_list)
                    
                    if reply_hasNext:
                        reply_pn += 1
                    else:
                        break

            # 获取图片资源
            resource_list = post_data[4]
            if download_resources:
                for i in range(len(resource_list)):           # 遍历每层楼
                    rsc_list = []
                    fname = resource_list[i][2].replace('?', '/').split('/')[-2]
                    if os.path.exists('resources/' + fname):
                        continue
                    tb_aux.random_sleep(self.min_wait_time, self.max_wait_time)
                    print("正在获取资源" + str(i) + "/" + str(len(resource_list)) + " 页")
                    img = requests.get(resource_list[i][2]).content
                    
                    with open('resources/' + fname, 'wb') as f:
                        f.write(img)
                    rsc_list.append({'thread_id':int(thread_id), 'post_id':int(resource_list[i][1]), 'file_name':fname})
                    self.db.create(table_name="resources", records=rsc_list)
                    rsc_list.clear()
            
            hasNext = post_data[5]
            if hasNext:
                pn += 1
            else:
                break

if __name__ == "__main__":
    main = UNo1_cli()

    parser = argparse.ArgumentParser(description="有男不玩UNo1--抓狗机")
    parser.add_argument("-r", "--resource", action="store_true", help="同时下载图片")
    parser.add_argument("-u", "--user", action="store_true", help="下载时显示用户信息")
    parser.add_argument("-k", "--kit", action="store_true", help="信息源是否切换为不二工具箱")
    parser.add_argument("-m", "--mark", action="store_true", help="是否标记用户？")
    parser.add_argument("-f", "--forum", help="指定吧名，扫描指定吧", type=str, default=None)
    parser.add_argument("-t", "--thread_id", help="指定贴ID，扫描指定贴", type=int, default=None)
    args = parser.parse_args()

    if args.forum is not None:
        main.update_thread_list(args.forum, args)

    if args.thread_id is not None:
        main.download_thread(args.thread_id, args)