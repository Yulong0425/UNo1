import pandas as pd
import os
import sys
from utils.tb_database import Database

replace = {}
with open("replace.txt", "r", encoding="utf-8") as f:
    for line in f.readlines():
        replace[line[0]] = line[1]

def speak(text):
    print(text)
    for k, v in replace.items():
        text = text.replace(k, v)
    os.system("termux-tts-speak " + text)
    # pyttsx3.speak(text)

db = Database("database")

forum = sys.argv[1]

fid = db.forums[db.forums['forum_name'] == forum].index[0]
threads = db.get_threads_by_forum_id(fid)

for idx, data in threads.iterrows():
    print(idx,data['thread_title'])

tids = []

while True:
    idx = int(input("请输入帖子:"))
    if idx == -1:
        break
    tids.append(threads.loc[idx]['thread_id'])


for tid in tids:
    thread = db.get_full_thread_by_id(int(tid))
    print(thread)
    speak("主题： " + thread['thread_title'].values[0])
    current_pid = -1
    for idx, data in thread.iterrows():
        if int(data['post_id']) != current_pid:
            current_pid = int(data['post_id'])
            print("***\n")
            user = db.get_user_by_id(int(data['user_id']))
            speak("用户： " + user['username'].values[0] + " 回帖：")
            speak(str(data.loc['content_x']))
            # rsc = db.get_resource_by_tid_pid(int(tid), int(data['post_id']))
            # for idx, r in rsc.iterrows():
            #     f.write("![](" + os.path.join('resources', str(r.loc['file_name'])) + ")\n")
        speak("回复：" + str(data.loc['content_y']))