import html.parser
import requests
import html

# site = "https://tieba.baidu.com/f?kw="
# forum = "原神内鬼"
# request = requests.get(site + forum).text

class forum_parser(html.parser.HTMLParser):
    def __init__(self):
        super().__init__()
        self.extraction_permission = False
        self.extraction_guide = []
        self.thread_buffer = ["", "", ""]
        self.threads_list = []

    def handle_starttag(self, tag, attrs):
        if tag == "span":
            if len(attrs) < 2:
                return
            if attrs[0][1] == "threadlist_rep_num center_text":
                self.extraction_permission = True
                self.extraction_guide.append(2)
        if tag == "a":
            if attrs[-1][1] == "j_th_tit ":
                self.extraction_permission = True
                self.extraction_guide.append(1)
                self.extraction_guide.append(3)
                self.thread_buffer[0] = attrs[1][1]

    def handle_data(self, data):
        if self.extraction_permission:
            self.extraction_permission = False
            for i in self.extraction_guide:
                if i == 1:
                    self.thread_buffer[1] = data
                if i == 2:
                    self.thread_buffer[2] = data
                if i == 3:
                    self.threads_list.append(self.thread_buffer.copy())
            self.extraction_guide.clear()

    def print(self):
        for i in self.threads_list:
            print(i)

if __name__ == "__main__":
    with open("content.txt", "r", encoding="utf-8") as f:
        request = f.read()

    request = html.unescape(request)
    parser = forum_parser()
    parser.feed(request)
    parser.print()
