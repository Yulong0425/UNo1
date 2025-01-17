import pandas as pd
import os

class Database:
    def __init__(self, path):
        self.path = path
        if not os.path.exists(self.path):
            self.setup()
        self.users = pd.read_csv(os.path.join(path, 'users.csv'))
        self.badges = pd.read_csv(os.path.join(path, 'badges.csv'))
        self.forums = pd.read_csv(os.path.join(path, 'forums.csv'))
        self.threads = pd.read_csv(os.path.join(path, 'threads.csv'))
        self.posts = pd.read_csv(os.path.join(path, 'posts.csv'))
        self.replies = pd.read_csv(os.path.join(path, 'replies.csv'))
        self.resources = pd.read_csv(os.path.join(path, 'resources.csv'))
        
    def setup(self):
        os.makedirs(self.path)
        pd.DataFrame(columns=['user_id', 'addr', 'username']).to_csv(os.path.join(self.path, 'users.csv'), index=False)
        pd.DataFrame(columns=['user_id', 'badge', 'badge_lv']).to_csv(os.path.join(self.path, 'badges.csv'), index=False)
        pd.DataFrame(columns=['forum_name']).to_csv(os.path.join(self.path, 'forums.csv'), index=True)
        pd.DataFrame(columns=['forum_id', 'thread_id', 'thread_title', 'reply_num']).to_csv(os.path.join(self.path, 'threads.csv'), index=False)
        pd.DataFrame(columns=['thread_id', 'post_id', 'user_id', 'time', 'layer', 'content']).to_csv(os.path.join(self.path, 'posts.csv'), index=False)
        pd.DataFrame(columns=['post_id', 'user_id_from', "user_id_to", 'time', 'content']).to_csv(os.path.join(self.path, 'replies.csv'), index=False)
        pd.DataFrame(columns=['thread_id', 'post_id', 'file_name']).to_csv(os.path.join(self.path, 'resources.csv'), index=False)

    def get_user_by_id(self, user_id):
        return self.users.where(self.users["user_id"] == user_id).dropna()

    def get_user_by_addr(self, addr):
        return self.users[self.users["addr"] == addr]
    
    def get_user_by_portrait(self, portrait):
        return self.users[self.users["addr"].str.contains(portrait)]
    
    def get_full_user_by_id(self, user_id):
        candidates = pd.merge(self.users, self.badges, how='inner', on=['user_id'])
        return candidates[candidates["user_id"] == user_id]

    def get_thread_by_id(self, thread_id):
        return self.threads[self.threads["thread_id"] == thread_id]
    
    def get_threads_by_forum_id(self, forum_id):
        return self.threads[self.threads["forum_id"] == forum_id]

    def get_post_by_id(self, post_id):
        return self.posts[self.posts["post_id"] == post_id]
    
    def get_posts_by_thread_id(self, thread_id):
        return self.posts[self.posts["thread_id"] == thread_id]
    
    def get_reply_by_post_id(self, post_id):
        return self.replies[self.replies["post_id"] == post_id]
    
    def get_full_thread_by_id(self, thread_id):
        candidates = self.threads[self.threads["thread_id"] == thread_id]
        candidates = pd.merge(candidates, self.posts, how='inner', on=['thread_id'])
        candidates = pd.merge(candidates, self.replies, how='inner', on=['post_id'])
        return candidates

    def get_resource_by_id(self, resource_id):
        return self.resources[self.resources["resource_id"] == resource_id]

    def get_resource_by_thread_id(self, thread_id):
        return self.resources[self.resources["thread_id"] == thread_id]

    def get_resource_by_tid_pid(self, thread_id, post_id):
        return self.resources.where((self.resources["thread_id"] == thread_id) & (self.resources["post_id"] == post_id))
    
    def get_last_layer_by_tid(self, thread_id):
        return self.posts[self.posts["thread_id"] == thread_id]["layer"].max()

    # [[self, user_id, addr, username]]
    def add_user(self, user_items):
        for item in user_items:
            user_id = item[0]
            addr = item[1]
            username = item[2]
            self.users = pd.concat([self.users, 
                    pd.DataFrame.from_records([{'user_id': user_id, 'addr': addr, 'username': username}])], 
                    ignore_index=True)
        self.users.drop_duplicates(subset=['user_id', 'username'], keep='first', inplace=True)
        self.users.to_csv(os.path.join(self.path, 'users.csv'), index=False)
    
    def add_badge(self, badge_items):
        for item in badge_items:
            user_id = item[0]
            badge = item[1]
            badge_lv = item[2]
            self.badges = pd.concat([self.badges, 
                    pd.DataFrame.from_records([{'user_id': user_id, 'badge': badge, 'badge_lv': badge_lv}])], 
                    ignore_index=True)
        self.badges.drop_duplicates(subset=['user_id', 'badge'], keep='last', inplace=True)
        self.badges.to_csv(os.path.join(self.path, 'badges.csv'), index=False)

    def add_forum(self, forum_items):
        for forum_name in forum_items:
            self.forums = pd.concat([self.forums, 
                    pd.DataFrame.from_records([{'forum_name': forum_name}])], 
                    ignore_index=True)
        self.forums.drop_duplicates(subset=['forum_name'], keep='first', inplace=True)
        self.forums.to_csv(os.path.join(self.path, 'forums.csv'), index=False)

    def add_thread(self, thread_items):
        for item in thread_items:
            forum_id = item[0]
            thread_id = item[1]
            thread_title = item[2]
            reply_num = item[3]
            self.threads = pd.concat([self.threads, 
                    pd.DataFrame.from_records([{'forum_id': forum_id, 'thread_id': thread_id, 'thread_title': thread_title, 'reply_num': reply_num}])], 
                    ignore_index=True)
        self.threads.drop_duplicates(subset=['thread_id'], keep='first', inplace=True)
        self.threads.to_csv(os.path.join(self.path, 'threads.csv'), index=False)

    def add_post(self, post_items):
        for item in post_items:
            thread_id = item[0]
            post_id = item[1]
            user_id = item[2]
            time = item[3]
            layer = item[4]
            content = item[5]
            self.posts = pd.concat([self.posts, 
                    pd.DataFrame.from_records([{'thread_id': thread_id, 'post_id': post_id, 'user_id': user_id, 'time': time, 'layer': layer, 'content': content}])], 
                    ignore_index=True)
        self.posts.drop_duplicates(subset=['post_id'], keep='first', inplace=True)
        self.posts.to_csv(os.path.join(self.path, 'posts.csv'), index=False)

    def add_reply(self, reply_items):
        for item in reply_items:
            post_id = item[0]
            user_id_from = item[1]
            user_id_to = item[2]
            time = item[3]
            content = item[4]
            self.replies = pd.concat([self.replies, 
                    pd.DataFrame.from_records([{'post_id': post_id, 'user_id_from': user_id_from, 'user_id_to': user_id_to, 'time': time, 'content': content}])], 
                    ignore_index=True)
        self.replies.drop_duplicates(subset=['post_id', 'content'], keep='first', inplace=True)
        self.replies.to_csv(os.path.join(self.path, 'replies.csv'), index=False)

    def add_resource(self, resource_items):
        for item in resource_items:
            thread_id = item[0]
            post_id = item[1]
            file_name = item[2]
            self.resources = pd.concat([self.resources, 
                    pd.DataFrame.from_records([{'thread_id': thread_id, 'post_id': post_id, 'file_name': file_name}])], 
                    ignore_index=True)
        self.resources.drop_duplicates(subset=['thread_id', 'post_id', 'file_name'], keep='first', inplace=True)
        self.resources.to_csv(os.path.join(self.path, 'resources.csv'), index=False)