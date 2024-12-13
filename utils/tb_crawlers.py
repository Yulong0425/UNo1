from lxml import etree
import html.parser
import requests
import html
import random
import time

class Crawler():
    def __init__(self):
        self.data = []

    def feed(self, request):
        pass

    def reset(self):
        self.data.clear()

class user_crawler(Crawler):
    def __init__(self):
        super().__init__()

    def feed(self, request):
        parse_html=etree.HTML(request)
        for i in range(50):
            post_xpath = '//div[@class="p_postlist"]/div[@class="l_post l_post_bright j_l_post clearfix  "][' + str(i+1) + ']'
            if parse_html.xpath(post_xpath) == []:
                break
            
            user_id_bds = post_xpath + '//li[@class="d_name"]/@data-field' 
            user_addr_bds = post_xpath + '//li[@class="d_name"]/a/@href'
            username_bds = post_xpath + '//li[@class="d_name"]/a/text()'  

            user_id = parse_html.xpath(user_id_bds)[0].strip("\{\}").split(":")[1]
            user_addr = parse_html.xpath(user_addr_bds)[0]
            try:
                username = parse_html.xpath(username_bds)[0]
            except:
                username = "!错误:纯图片昵称"


            self.data.append([int(user_id), user_addr, username])

class home_crawler(Crawler):
    def __init__(self):
        super().__init__()
        self.badges = []

    def feed(self, request):
        parse_html=etree.HTML(request)

        # username_bds = post_xpath + '//li[@class="d_name"]/a/text()'  

        try:
            user_id = parse_html.xpath('//a/@data-user-id')[0]
        except:
            print(parse_html.xpath('//a/@data-user-id'))
            print("error")
            exit()
        # username = parse_html.xpath(username_bds)[0]forum_group_wrap
        
        badges = parse_html.xpath('//div[@id="forum_group_wrap"]//span/text()')
        badge_lv = parse_html.xpath('//div[@id="forum_group_wrap"]/a/span[2]/@class')

        try:
            for idx in range(len(badges)):
                self.badges.append([user_id, badges[idx].strip(), int(badge_lv[idx].split("lv")[1])])
            print(self.badges)
            self.data.append(int(user_id))
        except:
            print(parse_html.xpath('//div[@id="forum_group_wrap"]/text()'))
    
    def reset(self):
        super().reset()
        self.badges.clear()

class badge_crawler(Crawler):
    def __init__(self):
        super().__init__()

    def feed(self, request):
        parse_html=etree.HTML(request)
        badge_bds = '//a[@class="card_title_fname"]/text()'
        try:
            badge = parse_html.xpath(badge_bds)[0].strip()
        except:
            badge_bds = '//a[@class="plat_title_h3"]/text()'
            badge = parse_html.xpath(badge_bds)[0].strip()
            print("badge error")
            print(parse_html.xpath(badge_bds))
        # badge = parse_html.xpath(badge_bds)[0].strip()

        for i in range(50):
            post_xpath = '//div[@class="p_postlist"]/div[@class="l_post l_post_bright j_l_post clearfix  "][' + str(i+1) + ']'
            if parse_html.xpath(post_xpath) == []:
                break
            
            user_id_bds = post_xpath + '//li[@class="d_name"]/@data-field' 
            badge_lv_bds = post_xpath + '//li[@class="l_badge"]//div[@class="d_badge_lv"]/text()'  

            try:
                user_id = parse_html.xpath(user_id_bds)[0].strip("\{\}").split(":")[1]
                badge_lv = parse_html.xpath(badge_lv_bds)[0]
            except:
                print("error when fetch this badge")
                print(parse_html.xpath('//li[@class="l_badge"]//div[@class="d_badge_lv"]/text()'))
                continue

            self.data.append([int(user_id), badge, int(badge_lv)])

class thread_crawler(Crawler):
    def __init__(self):
        super().__init__()

    def feed(self, request):
        parse_html=etree.HTML(request)
        for i in range(50):
            post_xpath = '//ul[@id="thread_list"]/li[' + str(i+1) + ']'
            if parse_html.xpath(post_xpath) == []:
                break

            thread_id_bds = post_xpath + '/@data-tid'
            title_bds = post_xpath + '//a[@class= "j_th_tit "]/text()'
            abstract_bds = post_xpath + '//div[@class="threadlist_abs threadlist_abs_onlyline "]/text()'
            reply_num_bds = post_xpath + '//span[@class="threadlist_rep_num center_text"]/text()'
            try:
                thread_id = parse_html.xpath(thread_id_bds)[0]
                title = parse_html.xpath(title_bds)[0].strip()
                abstract = parse_html.xpath(abstract_bds)[0].strip()
                reply_num = parse_html.xpath(reply_num_bds)[0].strip()
            except:
                continue

            self.data.append([str(thread_id), title, abstract, int(reply_num)])
            

class post_crawler(Crawler):
    def __init__(self):
        super().__init__()
        self.reply_indicator_list = []
        self.resource_list = []

    def feed(self, request):
        parse_html=etree.HTML(request)
        for i in range(50):
            post_xpath = '//div[@class="p_postlist"]/div[@class="l_post l_post_bright j_l_post clearfix  "][' + str(i+1) + ']'
            if parse_html.xpath(post_xpath) == []:
                break
            
            meta_info_bds = post_xpath + '//div[@class="j_lzl_r p_reply"]/@data-field'
            author_id_bds = post_xpath + '//li[@class="d_name"]/@data-field'
            tail_bds = post_xpath + '//span[@class="tail-info"]/text()'
            content_bds = post_xpath + '//div[@class="d_post_content j_d_post_content "]/text()'
            resource_bds = post_xpath + '//div[@class="d_post_content j_d_post_content "]//img[@class="BDE_Image"]/@src'
            resource = parse_html.xpath(resource_bds)

            meta_info = parse_html.xpath(meta_info_bds)
            if meta_info == []:
                meta_info = [":0,:0"]
            data = meta_info[0].strip("\{\}").split(",")

            post_id = data[0].split(":")[1]
            author_id = parse_html.xpath(author_id_bds)[0].strip("\{\}").split(":")[1]
            time = parse_html.xpath(tail_bds)[-1]
            layer = parse_html.xpath(tail_bds)[-2].replace("楼", "")
            content = parse_html.xpath(content_bds)

            reply_num = data[1].split(":")[1]
            if reply_num != "null" and int(reply_num) > 0:
                self.reply_indicator_list.append(post_id)

            self.data.append([int(post_id), int(author_id), time, int(layer), '。'.join(content).strip()])
            self.resource_list.append([post_id, resource])
    
    def reset(self):
        super().reset()
        self.reply_indicator_list.clear()
        self.resource_list.clear()

class reply_crawler(Crawler):
    def __init__(self):
        super().__init__()
        self.users = []
    
    def link_users(self, idx, user_id):
        self.users[idx][0] = user_id
        self.data[idx][0] = user_id

    def feed(self, request):
        parse_html=etree.HTML(request)
        for i in range(50):
            reply_xpath = '/html/body/li[' + str(i+1) + ']'
            
            spid_bds = reply_xpath + '/a/@name'
            if parse_html.xpath(spid_bds) == []:
                break
            
            author_link_bds = reply_xpath + '/div[@class="lzl_cnt"]/a/@href'
            author_bds = reply_xpath + '/div[@class="lzl_cnt"]/a/text()'
            content_bds = reply_xpath + '//span[@class="lzl_content_main"]/text()'
            tail_bds = reply_xpath + '//span[@class="lzl_time"]/text()'

            author_link = parse_html.xpath(author_link_bds)
            author = parse_html.xpath(author_bds)
            content = parse_html.xpath(content_bds)
            time = parse_html.xpath(tail_bds)[0]
            
            self.users.append([i, author_link[0], author[0]])
            self.data.append([i, -1, time, ''.join(content).strip()])

    
    def reset(self):
        super().reset()
        self.users.clear()

class resource_crawler(Crawler):
    def __init__(self):
        super().__init__()

    def feed(self, request):
        parse_html=etree.HTML(request)
        for i in range(50):
            post_xpath = '//div[@class="p_postlist"]/div[@class="l_post l_post_bright j_l_post clearfix  "][' + str(i+1) + ']'
            if parse_html.xpath(post_xpath) == []:
                break
            
            resource_bds = post_xpath + '//div[@class="d_post_content j_d_post_content "]//img[@class="BDE_Image"]/@src'
            meta_info_bds = post_xpath + '//div[@class="j_lzl_r p_reply"]/@data-field'

            resource = parse_html.xpath(resource_bds)
            meta_info = parse_html.xpath(meta_info_bds)

            if meta_info == []:
                meta_info = [":0,:0"]
            data = meta_info[0].replace("}", "").split(",")
            post_id = data[0].split(":")[1]

            self.data.append([post_id, resource])

def test_resource_get(url, fname, download=False):
    DOWNLOAD = download

    request = ""
    if DOWNLOAD:
        headers = {
            'User-Agent': 'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.1; WOW64; Trident/4.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; .NET4.0C; InfoPath.3)'
        }
        request = requests.get(url,headers=headers).text
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

    # -----Thread Crawler-----
    thread_cwl = thread_crawler()
    request = test_resource_get("https://tieba.baidu.com/f?kw=%E5%8E%9F%E7%A5%9E%E5%86%85%E9%AC%BC&fr=home", ".test_rsc/forum.html", True)
    thread_cwl.feed(request)
    print(thread_cwl.data)

    # -----Home Crawler-----
    # home_cwl = home_crawler()
    # request = test_resource_get("https://tieba.baidu.com/home/main?id=tb.1.fe837de9.Q-9ehLkqHGuqy6EaLRk1Cw?t=1716660588&fr=pb", ".test_rsc/home.html", False)
    # home_cwl.feed(request)
    # print(home_cwl.data)
    # print(home_cwl.badges)