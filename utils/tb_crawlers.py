from lxml import etree
import html.parser
import requests
import html
import json
import random
import time
import re

class Crawler():
    def __init__(self):
        self.data = []

    def feed(self, request):
        pass

    def reset(self):
        self.data.clear()

class HomeDataCrawler82(Crawler):
    user_id = 0
    user_portrait = ""
    user_name = ""
    user_nickname = ""
    badges = []
    def __init__(self):
        pass

    def feed(self, user_info, forum_info):
        # 解析 HTML 内容
        parse_html = etree.HTML(user_info)

        # 提取用户数据
        user_name_bds = '//span[contains(@class, "tb-uname")]/text()'
        user_data_bds = '//ul[contains(@class, "left-list")]/li/text()'
        
        '''
        # <li><span class="module-brand">百度ID：</span>6534809106</li>
        # <li><span class="module-brand">昵称：</span>胧川延</li>
        # <li><span class="module-brand">吧龄：</span>1.2年</li>
        # <li><span class="module-brand">粉丝数：</span>137</li>
        # <li><span class="module-brand">发帖量：</span>2713</li>
        # <li><span class="module-brand">回帖数：</span>2667</li>
        # <li><span class="module-brand">主题数：</span>46</li>
        '''
        try:
            self.user_name = parse_html.xpath(user_name_bds)
            user_data = parse_html.xpath(user_data_bds)
            self.user_id = user_data[0]
            self.user_nickname = user_data[1]
            self.followers = user_data[3]
            self.post_num = user_data[4]
            self.reply_num = user_data[5]
            self.thread_num = user_data[6]
        except:
            print('解析用户名错误')
            
        parse_forum_html = etree.HTML(forum_info)
        badges = parse_forum_html.xpath('//tbody/tr/td/text()')
        badge_lv = parse_forum_html.xpath('//tbody/tr/td[3]/span/text()')
        cleaned_badge_lv = list(map(lambda x: int(x.replace('级', '')), badge_lv))

        try:
            for idx in range(len(badges)):
                self.badges.append({"user_id":int(self.user_id), "badge":badges[idx].strip()+'吧', "badge_lv":cleaned_badge_lv[idx]})
        except:
            print('未关注吧')

class HomeDataCrawler(Crawler):
    def __init__(self):
        self.user_id = -1
        self.user_portrait = ""
        self.user_name = ""
        self.user_nickname = ""
        self.badges = []
        self.forums = []

    def feed(self, html_content):
        # 解析 HTML 内容
        parse_html = etree.HTML(html_content)

        # 提取用户数据
        user_data_bds = '//a[contains(@class, "mygift-more")]/@data-user-id'
        user_portrait_bds = '//a[contains(@class, "mygift-more")]/@data-portrait'

        # 提取用户的数字 ID
        try:
            user_id = int(parse_html.xpath(user_data_bds)[0])
            user_portrait = parse_html.xpath(user_portrait_bds)[0].split("?")[0]
            self.user_id = user_id
            self.user_portrait = user_portrait
        except Exception as e:
            print(f"解析错误: {e}")
            
        try:
            head_idx = html_content.index('{\"user\"')
            user_data = html_content[head_idx: html_content.index(')', head_idx)]
            user_data = json.loads(user_data)

            self.user_name = user_data['user']['homeUserName']
            self.user_nickname = user_data['user']['show_nickname']
        except:
            print('解析用户名错误')
        
        forumArr = []
        try:
            forumArr_head = html_content.index('{\"forumArr\"')
            forumArr_parse = html_content[forumArr_head: html_content.index(';', forumArr_head)-1]
            forumArr = json.loads(forumArr_parse)['forumArr']
        except:
            print('解析主页信息错误：未找到论坛（大概率由于用户隐藏关注信息）')
            print(self.user_portrait, self.user_nickname)

        try:
            for forum in forumArr:
                self.badges.append({'user_id':user_id, 'forum_id':forum['forum_id'], 'badge_lv':forum['level_id']})
                self.forums.append({'forum_id':forum['forum_id'], 'forum_name':forum['forum_name']})
        except:
            print('已隐藏关注信息')
            print(parse_html.xpath('//div[@id="forum_group_wrap"]/text()'))

class ThreadDataCrawler:
    thread_list = []
    def __init__(self):
        pass

    def feed(self, html_content):
        # 解析 HTML 内容
        parse_html = etree.HTML(html_content)

        # 匹配帖子数据路径
        thread_bds = '//li[contains(@class, "j_thread_list")]/@data-field'
        titles_bds = '//a[contains(@class, "j_th_tit")]/text()'
        abstracts_bds = '//div[contains(@class, "threadlist_abs")]/text()'

        # 提取数据
        thread_data = parse_html.xpath(thread_bds)
        titles = parse_html.xpath(titles_bds)
        abstracts = parse_html.xpath(abstracts_bds)

        # 清洗数据
        abstracts = [abstract.strip() for abstract in abstracts]

        # 解析每个帖子
        for index, thread_json in enumerate(thread_data):
            try:
                # 加载 JSON 数据
                thread_info = json.loads(thread_json)

                # 提取字段
                fid_head = html_content.index("{\"forum_id\"")
                forum_data = json.loads(html_content[fid_head: html_content.index("}", fid_head + 1)+1])
                
                forum_id = forum_data['forum_id']
                thread_id = str(thread_info.get("id", ""))
                title = titles[index] if index < len(titles) else ""
                abstract = abstracts[index] if index < len(abstracts) else ""
                reply_num = thread_info.get("reply_num", 0)

                # 打印结果
                # print(f"Thread ID: {thread_id}")
                # print(f"Title: {title}")
                # print(f"Abstract: {abstract}")
                # print(f"Comment Number: {reply_num}")
                # print("-" * 50)
                self.thread_list.append({'forum_id':forum_id, 'thread_id':thread_id, 'thread_title':title, 'abstract':abstract, 'reply_num':reply_num})
            except Exception as e:
                print(f"解析错误: {e}")
  
class PostDataCrawler(Crawler):
    def __init__(self):
        self.post_list = []
        self.user_list = []
        self.badge_list = []
        self.reply_indicator_list = []
        self.resource_list = []
        self.max_page = 1

    def feed(self, html_content):
        # 解析 HTML 内容
        parse_html = etree.HTML(html_content)

        # 匹配包含帖子数据的节点路径
        posts_bds = '//div[@class="p_postlist"]/div[contains(@class, "l_post")]/@data-field'
        post_times_bds = '//div[contains(@class, "l_post")]/div[contains(@class, "d_post_content_main")]//span[@class="tail-info" and contains(text(), "-")]/text()'
        author_shown_name_bds = '//div[contains(@class, "l_post")]//li[@class="d_name"]/a/text()'
        badge_lv_bds = '//div[contains(@class, "l_post")]/div[contains(@class, "d_author")]//div[@class="d_badge_lv"]/text()'
        max_page_bds = '//input[@class="jump_input_bright"]/@max-page'
        
        # 提取帖子数据
        posts_data = parse_html.xpath(posts_bds)
        post_times = parse_html.xpath(post_times_bds)
        author_shown_name = parse_html.xpath(author_shown_name_bds)
        badge_lv = parse_html.xpath(badge_lv_bds)
        if parse_html.xpath(max_page_bds) != []:
            self.max_page = int(parse_html.xpath(max_page_bds)[0])

        # 确保帖子的 JSON 数据和时间数据一一对应
        for post_data, post_time, badge_lv in zip(posts_data, post_times, badge_lv):
            try:
                # 加载 JSON 数据
                posts_data_converted = html.unescape(post_data)
                # Remove HTML-like tags
                data_cleaned = re.sub(r'<[^>]*>', '', posts_data_converted)
                data = json.loads(data_cleaned)
            except KeyError as e:
                print(f"解析错误，缺失键: {e}")
            except IndexError as e:
                print(f"解析错误，缺失索引: {e}")
            except json.JSONDecodeError as e:
                print(f"POST-JSON解析错误: {e}")
                print(f"JSON数据: {post_data}")

            # 提取所需字段
            author = data.get('author', {})
            content = data.get('content', {})

            # 收集数据
            user = {'user_id':author['user_id'], 'portrait':author['portrait'].split("?")[0], 'username':author['user_name'], 'nickname':author['user_nickname']}
            badge = {'user_id':author['user_id'], 'forum_id':content['forum_id'], 'badge_lv':badge_lv}

            post = {
                'thread_id':content.get('thread_id', None),  # 帖子ID
                'post_id':content.get('post_id', None),    # 回复ID
                'user_id':author.get('user_id', None),     # 用户数字ID
                'time':post_time.strip(),               # 发表时间（从 HTML 提取）
                'layer':content.get('post_no', None),    # 楼层号
                'content':content.get('content', None)  # 帖子内容
            }
            
            resource = etree.HTML(str(data.get('content', {}))).xpath('//img[@class="BDE_Image"]/@src')
            # 添加
            self.post_list.append(post)
            self.user_list.append(user)
            self.badge_list.append(badge)
            if content.get('comment_num', []) != 0:
                self.reply_indicator_list.append([content.get('post_id', 0), content.get('comment_num', 0)])
            for addr in resource:
                self.resource_list.append([content.get('thread_id', None), content.get('post_id', None), addr])

class ReplyDataCrawler(Crawler):
    def __init__(self):
        self.user_list = []
        self.reply_list = []

    def feed(self, html_content):
        # 解析 HTML 内容
        parse_html = etree.HTML(html_content)

        # 匹配包含楼中楼数据的节点路径
        reply_bds = '//li[contains(@class, "lzl_single_post")]/@data-field'
        content_bds = '//li[contains(@class, "lzl_single_post")]/div[@class="lzl_cnt"]'

        # 提取楼中楼数据
        replies_data = parse_html.xpath(reply_bds)
        content_data = parse_html.xpath(content_bds)

        for data, content in zip(replies_data, content_data):
            try:
                # 解析主 data-field JSON
                reply_info = json.loads(data)
                showname = reply_info.get("showname", "")
                username = reply_info.get("user_name", "")
                user_portrait = reply_info.get("portrait", "")

                # 提取内容和时间
                lzl_content = content.xpath('.//span[@class="lzl_content_main"]/text()')
                lzl_to_portrait_parse = content.xpath('.//span[@class="lzl_content_main"]/a/@portrait')
                if lzl_to_portrait_parse != []:
                    lzl_to_portrait = lzl_to_portrait_parse[0]
                else:
                    lzl_to_portrait = ""
                    
                lzl_content = ''.join(lzl_content.strip() for lzl_content in lzl_content)
                lzl_time = content.xpath('.//span[@class="lzl_time"]/text()')
                lzl_time = lzl_time[0] if lzl_time else ""

                user = {'user_id':-1, 'portrait':user_portrait, 'username':username, 'nickname':showname}
                reply = {'post_id':-1, 'user_portrait_from':user_portrait, 'user_portrait_to':lzl_to_portrait, 'time':lzl_time, 'content':lzl_content}

                self.user_list.append(user)
                self.reply_list.append(reply)
            except Exception as e:
                print(f"REPLY解析错误: {e}")
                print(f"JSON数据: {data}")

def test_resource_get(url, fname, download=False, verify=True):
    DOWNLOAD = download

    request = ""
    if DOWNLOAD:
        headers = {
            'User-Agent': 'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.1; WOW64; Trident/4.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; .NET4.0C; InfoPath.3)'
        }
        request = requests.get(url,headers=headers, verify=verify).text
        with open(fname, "w", encoding="utf-8") as f:
            f.write(request)
    else:
        with open(fname, "r", encoding="utf-8") as f:
            request = f.read()
            request = html.unescape(request)

    return request

if __name__ == "__main__":

    print("------------------------------------")
    # user_cwl = user_crawler()
    # badge_cwl = badge_crawler()
    # post_cwl = post_crawler()
    
    # user_cwl.feed(request)
    # badge_cwl.feed(request)
    # post_cwl.feed(request)

    # print(user_cwl.data)
    # print(badge_cwl.data)
    # print(post_cwl.data)

    # -----Post Crawler-----
    # test_resource_get("https://tieba.baidu.com/p/9383795166?pn=8", ".test_rsc/post.html")
    # 读取文件内容
    with open(".test_rsc/post.html", "r", encoding="utf-8") as file:
        html_content = file.read()

    # 创建爬虫实例并运行
    crawler = PostDataCrawler()
    crawler.feed(html_content)

    # -----Reply Crawler-----
    # reply_cwl = reply_crawler()
    # request = test_resource_get("https://tieba.baidu.com/p/comment?tid=9356169960&pid=151428509536&pn=1", ".test_rsc/reply.html")
    # reply_cwl.feed(request)
    # print(reply_cwl.data)
    # 读取文件内容
    # with open(".test_rsc/reply.html", "r", encoding="utf-8") as file:
    #     html_content = file.read()

    # # 创建爬虫实例并运行
    # crawler = ReplyDataCrawler()
    # crawler.feed(html_content)

    # -----Thread Crawler-----
    # thread_cwl = thread_crawler()
    # request = test_resource_get("https://tieba.baidu.com/f?kw=%E5%8E%9F%E7%A5%9E%E5%86%85%E9%AC%BC&fr=home", ".test_rsc/forum.html", True)
    # thread_cwl.feed(request)
    # print(thread_cwl.data)
    # # 读取文件内容
    # with open(".test_rsc/forum.html", "r", encoding="utf-8") as file:
    #     html_content = file.read()

    # # 创建爬虫实例并运行
    # crawler = ThreadDataCrawler()
    # crawler.feed(html_content)

    # -----Home Crawler-----
    # home_cwl = home_crawler()
    # request = test_resource_get("https://tieba.baidu.com/home/main?id=tb.1.fe837de9.Q-9ehLkqHGuqy6EaLRk1Cw?t=1716660588&fr=pb", ".test_rsc/home.html", False)
    # home_cwl.feed(request)
    # print(home_cwl.data)
    # print(home_cwl.badges)
    # # 读取文件内容
    # with open(".test_rsc/home.html", "r", encoding="utf-8") as file:
    #     html_content = file.read()

    # # 创建爬虫实例并运行
    # crawler = HomeDataCrawler()
    # crawler.feed(html_content)

    # -----Home82 Crawler-----
    # html_content = test_resource_get("https://124.221.26.245/tieba/info/泷川d", ".test_rsc/home82.html", download=False, verify=False)
    # forum_info = test_resource_get("https://124.221.26.245/tieba/forum/泷川d/1", ".test_rsc/forum_info.html", download=False, verify=False)
    # # 读取文件内容
    # with open(".test_rsc/home82.html", "r", encoding="utf-8") as file:
    #     html_content = file.read()
    # with open(".test_rsc/forum_info.html", "r", encoding="utf-8") as file:
    #     forum_info = file.read()

    # # 创建爬虫实例并运行
    # crawler = HomeDataCrawler82()
    # crawler.feed(html_content, forum_info)