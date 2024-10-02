import socket
import eel
import threading
from kivy.uix.screenmanager import Screen, SlideTransition
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.widget import Widget
import database

# Initialize eel with the web folder that contains the HTML, CSS, and JS files
eel.init('web')

class TeacherMenuPage(Screen):
    def __init__(self, **kwargs):
        super(TeacherMenuPage, self).__init__(**kwargs)
        self.teacher_id = None  # 初始化 teacher_id
        
        # 使用 AnchorLayout 將主內容置中
        anchor_layout = AnchorLayout()
        layout = BoxLayout(orientation='vertical', padding=20, spacing=20, size_hint=(0.9, 0.9))
        
        # 標題標籤
        title_label = Label(text="老師功能選單", font_size=32, font_name="BiauKai", size_hint=(1, 0.2))
        layout.add_widget(title_label)
        
        # 按鈕置中布局
        def center_button(button_text, button_action):
            button_layout = BoxLayout(orientation='horizontal', size_hint=(1, 0.1))
            button = Button(text=button_text, font_size=24, size_hint=(0.6, 1), width=200, font_name="BiauKai")
            button.bind(on_press=button_action)
            button_layout.add_widget(Widget())  # 左側空白填充
            button_layout.add_widget(button)  # 按鈕
            button_layout.add_widget(Widget())  # 右側空白填充
            return button_layout

        # 上傳題目按鈕
        layout.add_widget(center_button("上傳題目", self.go_to_upload))

        # 分析結果按鈕
        layout.add_widget(center_button("分析結果", self.go_to_analyze))

        # 返回首頁按鈕
        layout.add_widget(center_button("返回首頁", self.go_to_home))

        anchor_layout.add_widget(layout)
        self.add_widget(anchor_layout)

    # 設置 teacher_id 的方法
    def set_teacher_id(self, teacher_id):
        self.teacher_id = teacher_id

    def go_to_upload(self, instance):
        # 設置向左滑動過渡動畫
        self.manager.transition = SlideTransition(direction='left')

        # 傳遞 teacher_id 到上傳題目頁面
        upload_page = self.manager.get_screen('upload')
        upload_page.set_teacher_id(self.teacher_id)  # 將 teacher_id 傳遞到 upload 頁面
        
        self.manager.current = 'upload'
        
    def go_to_analyze(self, instance):
        # 在單獨的執行緒中啟動 Eel
        threading.Thread(target=self.start_eel).start()

    def find_available_port(self, start_port=5000):
        """ 找到一個可用的端口 """
        port = start_port
        while True:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                if sock.connect_ex(('localhost', port)) != 0:  # 如果端口沒被佔用
                    return port
                port += 1  # 增加端口號

    def start_eel(self):
        port = self.find_available_port(5000)  # 從8080開始找可用端口
        eel.start('index.html', port=port)  # 在可用的端口啟動 Eel

    def go_to_home(self, instance):
        self.manager.transition = SlideTransition(direction='right')
        self.manager.current = 'home'