#解析HTML字符串
from lxml import etree
text = ''
with open('thread_sample.txt', 'r', encoding='utf-8') as f:
    text = f.read()

# 开始初始化
parse_html=etree.HTML(text)
# 书写xpath表达式,提取文本最终使用text()
# xpath_bds='//div/text()'
# # 提取文本数据，以列表形式输出
# r_list=parse_html.xpath(xpath_bds)
# # 打印数据列表
# print(r_list)


# xpath_bds='//a/@href'
# # 提取文本数据，以列表形式输出
# r_list=parse_html.xpath(xpath_bds)
# # 打印数据列表
# print(r_list)

# user_bds='//li[@class="d_name"]/a/text()'
# # 提取文本数据，以列表形式输出
# user_list=parse_html.xpath(user_bds)
# # 打印数据列表
# for i in range(len(user_list)):
#     post_bds='//div[@class="p_postlist"]/div[@class="l_post l_post_bright j_l_post clearfix  "]['+ str(i+1) +']//div[@class="d_post_content j_d_post_content "]/text()'
#     post_list=parse_html.xpath(post_bds)
#     if len(post_list) == 0:
#         break
#     else:
#         print(user_list[i] + ": " + ''.join(post_list).strip())

# xpath_bds='//li[@class="d_name"]/a/text()'
xpath_bds='//span[@class="tail-info"]/text()'
# 提取文本数据，以列表形式输出
r_list=parse_html.xpath(xpath_bds)
r_list.remove('来自')
# 打印数据列表
print(r_list)