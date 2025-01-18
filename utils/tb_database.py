import pandas as pd
import os

class Database:
    def __init__(self, path):
        self.path = path
        if not os.path.exists(self.path):
            self.setup()
        self.tables = {}
        for file_name in os.listdir(self.path):
            if file_name.endswith('.csv'):
                table_name = os.path.splitext(file_name)[0]
                self.tables[table_name] = pd.read_csv(os.path.join(self.path, file_name))

    def setup(self):
        os.makedirs(self.path)
        tables = {
            'users.csv': ['user_id', 'portrait', 'username', 'nickname'],
            'badges.csv': ['user_id', 'forum_id', 'badge_lv'],
            'forums.csv': ['forum_id', 'forum_name'],
            'threads.csv': ['forum_id', 'thread_id', 'thread_title', 'abstract', 'reply_num'],
            'posts.csv': ['thread_id', 'post_id', 'user_id', 'time', 'layer', 'content'],
            'replies.csv': ['post_id', 'user_portrait_from', 'user_portrait_to', 'time', 'content'],
            'resources.csv': ['thread_id', 'post_id', 'file_name'],
        }
        for file_name, columns in tables.items():
            pd.DataFrame(columns=columns).to_csv(os.path.join(self.path, file_name), index=False)
        
        if not os.path.exists('resources'):
            os.mkdir('resources')
        
    def save_table(self, table_name):
        """保存表数据到对应的 CSV 文件"""
        file_name = f"{table_name}.csv"
        self.tables[table_name].to_csv(os.path.join(self.path, file_name), index=False)

    def create(self, table_name, records):
        """批量插入记录并去重"""
        if table_name not in self.tables:
            raise ValueError(f"Table {table_name} does not exist")

        # 当前表的列名
        columns = self.tables[table_name].columns

        # 将新记录转换为 DataFrame，并确保字段匹配
        new_records = pd.DataFrame(records, columns=columns)

        # 合并现有表数据和新记录
        updated_table = pd.concat([self.tables[table_name], new_records], ignore_index=True)

        # 去重逻辑（根据特定列，如主键去重）
        if table_name == "users":
            updated_table = updated_table.drop_duplicates(subset=["portrait"], keep="first")
        elif table_name == "posts":
            updated_table = updated_table.drop_duplicates(subset=["post_id"])
        elif table_name == "badges":
            updated_table = updated_table.drop_duplicates(subset=["user_id", "forum_id"], keep="last").astype('int64')
        elif table_name == "replies":
            updated_table = updated_table.drop_duplicates(subset=["post_id", "content"])
        elif table_name == "resources":
            updated_table = updated_table.drop_duplicates(subset=["post_id", "file_name"])
        elif table_name == "forums":
            updated_table = updated_table.drop_duplicates(subset=["forum_id"])

        # 更新表数据
        self.tables[table_name] = updated_table

        # 保存更新后的表到文件
        self.save_table(table_name)

    def read(self, table_name, **conditions):
        """读取表中的数据，支持按条件筛选"""
        if table_name not in self.tables:
            raise ValueError(f"Table {table_name} does not exist")
        table = self.tables[table_name]
        for column, value in conditions.items():
            table = table[table[column] == value]
        return table

    def update(self, table_name, conditions, updates):
        """更新表中满足条件的记录"""
        if table_name not in self.tables:
            raise ValueError(f"Table {table_name} does not exist")
        table = self.tables[table_name]
        for index, row in table.iterrows():
            if all(row[col] == val for col, val in conditions.items()):
                for col, val in updates.items():
                    table.at[index, col] = val
        self.tables[table_name] = table
        self.save_table(table_name)

    def delete(self, table_name, **conditions):
        """删除表中满足条件的记录"""
        if table_name not in self.tables:
            raise ValueError(f"Table {table_name} does not exist")
        table = self.tables[table_name]
        for column, value in conditions.items():
            table = table[table[column] != value]
        self.tables[table_name] = table
        self.save_table(table_name)