from html.parser import HTMLParser
import threading
import requests
import html
import wx

from utils import tb_api
import threads_fetch

def t():
    threading.Thread(target=tb_api.fetch_threads, args=("原神内鬼",)).start()

class UNo1_main(wx.Frame):
    def __init__(self, parent=None,size=(700,700)):
        # 数据初始化
        self.thread_list = []
        self.download_queue = []

        # 窗口初始化
        wx.Frame.__init__(self,parent=parent, title="有男不玩UNo1-抓狗机",size=size)
        self.panel = wx.Panel(self)
        
        # 功能导航栏
        self.navigation1 = wx.Button(self.panel, label="侦察")
        self.navigation2 = wx.Button(self.panel, label="留档")
        self.navigation3 = wx.Button(self.panel, label="查看")
        self.navigation4 = wx.Button(self.panel, label="抓狗")
        self.navigation1.Bind(wx.EVT_BUTTON,self.detection_box)
        self.navigation2.Bind(wx.EVT_BUTTON,self.archive_box)

        self.navigation_box = wx.BoxSizer(wx.HORIZONTAL)
        self.navigation_box.Add(self.navigation1, 0, wx.ALL, 5)
        self.navigation_box.Add(self.navigation2, 0, wx.ALL, 5)
        self.navigation_box.Add(self.navigation3, 0, wx.ALL, 5)
        self.navigation_box.Add(self.navigation4, 0, wx.ALL, 5)

        self.panel_box = wx.BoxSizer(wx.VERTICAL)
        self.panel_box.Add(self.navigation_box, 0, wx.ALL, 10)
        self.panel.SetSizer(self.panel_box)

    def generate_navigation(self):
        self.navigation1 = wx.Button(self.panel, label="侦察")
        self.navigation2 = wx.Button(self.panel, label="留档")
        self.navigation3 = wx.Button(self.panel, label="查看")
        self.navigation4 = wx.Button(self.panel, label="抓狗")
        self.navigation1.Bind(wx.EVT_BUTTON,self.detection_box)
        self.navigation2.Bind(wx.EVT_BUTTON,self.archive_box)

        self.navigation_box = wx.BoxSizer(wx.HORIZONTAL)
        self.navigation_box.Add(self.navigation1, 0, wx.ALL, 5)
        self.navigation_box.Add(self.navigation2, 0, wx.ALL, 5)
        self.navigation_box.Add(self.navigation3, 0, wx.ALL, 5)
        self.navigation_box.Add(self.navigation4, 0, wx.ALL, 5)
        return self.navigation_box
    
    def generate_download_status_box(self):
        status_box = wx.BoxSizer(wx.HORIZONTAL)
        # 下载状态
        self.download_gauge = wx.Gauge(self.panel, -1)
        self.download_info = wx.TextCtrl(self.panel, -1, value="下载日志", style=wx.TE_MULTILINE | wx.TE_READONLY)
        status_box.Add(self.download_gauge, 1, wx.ALL, 5)
        status_box.Add(self.download_info, 1, wx.ALL, 5)
        return status_box

    def detection_box(self, evt):
        self.panel_box.Clear(True)

        navigation_box = self.generate_navigation()
        search_box = wx.BoxSizer(wx.HORIZONTAL)
        threads_box = wx.BoxSizer(wx.HORIZONTAL)
        action_box = wx.BoxSizer(wx.HORIZONTAL)
        status_box = wx.BoxSizer(wx.HORIZONTAL)

        forum_name = wx.TextCtrl(self.panel, -1,"原神内鬼")
        search_button = wx.Button(self.panel, label="搜索")
        def load_thread_list(evt):
            kw = forum_name.GetValue()
            self.thread_list = tb_api.fetch_threads(kw)
            self.thread_list_box.SetItems([i[1] for i in self.thread_list])
            self.thread_list_box.Refresh()
            self.Layout()
        search_button.Bind(wx.EVT_BUTTON, load_thread_list)
        search_box.Add(forum_name, 0, wx.ALL, 5)
        search_box.Add(search_button, 0, wx.ALL, 5)

        # 帖子列表
        titles = []
        for i in self.thread_list:
            titles.append(i[1])
        select_all = wx.Button(self.panel, label="全选")
        def select_all_threads(evt):
            print("点击：全选")
            # print(titles)
            # print(len(titles))
            for i in range(len(self.thread_list)):
                self.thread_list_box.Check(i)
                print("Checked"+str(i))
            self.thread_list_box.Refresh()
            self.Layout()
        select_all.Bind(wx.EVT_BUTTON, select_all_threads)
        self.thread_list_box = wx.CheckListBox(self.panel, id=1, choices=titles)
        self.thread_info = wx.TextCtrl(self.panel, -1, value="帖子信息", style=wx.TE_MULTILINE | wx.TE_READONLY)
        def reveal_thread_info(evt):
            self.thread_info.SetValue("帖子ID:" + str(self.thread_list[self.thread_list_box.GetSelection()][0]) + 
                            "\n帖子标题:" + self.thread_list[self.thread_list_box.GetSelection()][1]+
                            "\n帖子摘要:" + self.thread_list[self.thread_list_box.GetSelection()][2]+
                            "\n回复量:" + str(self.thread_list[self.thread_list_box.GetSelection()][3]))
            self.thread_info.Refresh()
            self.Layout()
        self.thread_list_box.Bind(wx.EVT_LISTBOX, reveal_thread_info)
        threads_box.Add(select_all, 1, wx.ALL, 5)
        threads_box.Add(self.thread_list_box, 6, wx.EXPAND | wx.ALL, 5)
        threads_box.Add(self.thread_info, 3, wx.EXPAND | wx.ALL, 5)

        # 下载
        download_button = wx.Button(self.panel, label="下载")
        download_resources = wx.CheckBox(self.panel, label="下载图片")
        download_replies = wx.CheckBox(self.panel, label="下载回复")
        def download_thread(evt):
            self.download_gauge.SetValue(0)
            items = self.thread_list_box.GetCheckedItems()
            for idx in range(len(items)):   
                self.download_gauge.SetValue(int(idx / len(items) * 100))
                thread_id = self.thread_list[items[idx]][0]
                try:
                    self.download_info.WriteText("开始下载第"+str(idx+1)+"条\n")
                    tb_api.download_thread(thread_id, download_resources=download_resources.IsChecked())
                    self.download_info.WriteText("已下载第"+str(idx+1)+"条\n")
                except:
                    self.download_info.WriteText("下载失败\n")
                    print("下载失败")
                self.download_gauge.Refresh()
                self.Layout()
            self.download_gauge.SetValue(100)
            self.download_gauge.Refresh()
            self.Layout()

        def threading_download(evt):
            thread = threading.Thread(target=download_thread, args=(evt,))
            thread.start()
        download_button.Bind(wx.EVT_BUTTON, threading_download)
        action_box.Add(download_button, 3, wx.ALL, 5)
        action_box.Add(download_resources, 1, wx.ALL, 5)
        action_box.Add(download_replies, 1, wx.ALL, 5)

        # 下载状态
        self.download_gauge = wx.Gauge(self.panel, -1)
        self.download_info = wx.TextCtrl(self.panel, -1, value="下载日志", style=wx.TE_MULTILINE | wx.TE_READONLY)
        status_box.Add(self.download_gauge, 1, wx.ALL, 5)
        status_box.Add(self.download_info, 1, wx.ALL, 5)

        self.panel_box.Add(navigation_box, 1, wx.ALL, 10)
        self.panel_box.Add(search_box, 1, wx.ALL, 10)
        self.panel_box.Add(threads_box, 10, wx.ALL, 10)
        self.panel_box.Add(action_box, 1, wx.ALL, 10)
        self.panel_box.Add(status_box, 1, wx.ALL, 10)

        self.panel.SetSizer(self.panel_box)
        self.panel.Refresh()
        self.panel.Layout()

    def archive_box(self, evt):
        self.panel_box.Clear(True)

        navigation_box = self.generate_navigation()
        search_box = wx.BoxSizer(wx.HORIZONTAL)
        threads_box = wx.BoxSizer(wx.HORIZONTAL)
        action_box = wx.BoxSizer(wx.HORIZONTAL)
        status_box = wx.BoxSizer(wx.HORIZONTAL)

        thread_id = wx.TextCtrl(self.panel, -1,"帖子ID")
        def push_queue(evt):
            self.download_queue.append(thread_id.GetValue())
            self.download_queue_box.SetItems(self.download_queue)
            self.download_queue_box.Refresh()
            self.Layout()
        search_button = wx.Button(self.panel, label="加入队列")
        search_button.Bind(wx.EVT_BUTTON, push_queue)
        search_box.Add(thread_id, 0, wx.ALL, 5)
        search_box.Add(search_button, 0, wx.ALL, 5)

        # 帖子列表
        self.download_queue_box = wx.ListBox(self.panel, id=1, choices=self.download_queue)
        threads_box.Add(self.download_queue_box, 1, wx.EXPAND | wx.ALL, 5)

        # 下载
        download_button = wx.Button(self.panel, label="下载")
        download_resources = wx.CheckBox(self.panel, label="下载图片")
        download_resources.SetValue(True)
        download_replies = wx.CheckBox(self.panel, label="下载回复")
        def download_thread(evt):
            self.download_gauge.SetValue(0)
            while True:
                if len(self.download_queue) == 0:
                    break
                item = self.download_queue[0]
                # self.download_gauge.SetValue(int(idx / len(self.download_queue) * 100))
                thread_id = item
                try:
                    self.download_info.WriteText("开始下载"+thread_id+"\n")
                    tb_api.download_thread(thread_id, download_resources=download_resources.IsChecked())
                    self.download_info.WriteText("已下载"+thread_id+"\n")
                except:
                    self.download_info.WriteText("下载失败\n")
                    print("下载失败")
                self.download_queue.pop(0)
                self.download_queue_box.SetItems(self.download_queue)
                self.download_queue_box.Refresh()
                self.download_queue_box.Layout()
                # self.download_gauge.Refresh()
                # self.Layout()
            # self.download_gauge.SetValue(100)
            # self.download_gauge.Refresh()
            # self.Layout()

        def threading_download(evt):
            thread = threading.Thread(target=download_thread, args=(evt,))
            thread.start()
        download_button.Bind(wx.EVT_BUTTON, threading_download)

        action_box.Add(download_button, 3, wx.ALL, 5)
        action_box.Add(download_resources, 1, wx.ALL, 5)
        action_box.Add(download_replies, 1, wx.ALL, 5)

        self.panel_box.Add(navigation_box, 1, wx.ALL, 10)
        self.panel_box.Add(search_box, 1, wx.ALL, 10)
        self.panel_box.Add(threads_box, 10, wx.ALL, 10)
        self.panel_box.Add(action_box, 1, wx.ALL, 10)
        self.panel_box.Add(self.generate_download_status_box(), 1, wx.ALL, 10)

        self.panel.SetSizer(self.panel_box)
        self.panel.Refresh()
        self.panel.Layout()

    def check_thread(self, evt):
        self.thread_info.SetValue("帖子ID:" + self.thread_list[self.thread_list_box.GetSelection()][0] + 
                                "\n帖子标题:" + self.thread_list[self.thread_list_box.GetSelection()][1]+
                                "\n回复量:" + self.thread_list[self.thread_list_box.GetSelection()][2])

    def refresh(self, evt):
        self.Update()

    def mode(self, state):
        self.state = state

    # def on_button_click(self,evt):
    #     match evt.GetEventObject().GetLabel():
    #         case "侦察":
    #             self.detection_box()
            #     self.txtSelfText.SetLabel("啊变了")
            #     btnTest = wx.Button(self,-1,"按吧搜索",(0,30),(100,20))
            #     btnTest.Bind(wx.EVT_BUTTON,self.on_button_click)
            # case "按吧搜索":
            #     self.txtSelfText.SetLabel("按吧搜索")
                
            #     self.setText = wx.TextCtrl(self,-1,"input",(0,60),(100,20))
            #     search_button = wx.Button(self,-1,"搜索",(100,60),(50,20))
            #     search_button.Bind(wx.EVT_BUTTON,self.on_button_click)
            # case "搜索":
            #     self.txtSelfText.SetLabel(self.setText.GetValue())

    # def onText(self,evt):
    #     self.txtSelfText.SetLabel(self.setText.GetValue())

    # def onText(self,evt):
    #     self.txtSelfText.SetLabel(self.setText.GetValue())


if __name__ == '__main__':
    app = wx.App()
    frame = UNo1_main()
    frame.Show()
    app.MainLoop()
