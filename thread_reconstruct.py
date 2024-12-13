import pandas as pd
import os
import sys
from utils.tb_database import Database

db = Database("database")

tid = int(sys.argv[1])

thread = db.get_full_thread_by_id(int(tid))

print(thread.columns)

with open("thread_output.md", "w", encoding="utf-8") as f:
    current_pid = -1
    for idx, data in thread.iterrows():
        if int(data['post_id']) != current_pid:
            current_pid = int(data['post_id'])
            f.write("***\n")
            user = db.get_user_by_id(int(data['user_id']))
            f.write("###### " + user['username'].values[0] + "\n")
            f.write(str(data.loc['content_x']) + "\n")
            rsc = db.get_resource_by_tid_pid(int(tid), int(data['post_id']))
            for idx, r in rsc.iterrows():
                f.write("![](" + os.path.join('resources', str(r.loc['file_name'])) + ")\n")
        f.write("- " + str(data.loc['content_y']) + "\n")