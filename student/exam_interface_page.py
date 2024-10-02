from kivy.uix.screenmanager import Screen, SlideTransition
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.core.text import LabelBase
from kivy.uix.widget import Widget
from kivy.uix.scrollview import ScrollView
from kivy.uix.anchorlayout import AnchorLayout
from kivy.graphics import Color, RoundedRectangle
import mysql.connector

from student.recording_page import RecordingPage

# 註冊粉圓體字體
LabelBase.register(name="BiauKai", fn_regular="font/粉圓體.ttf")

class ExamInterfacePage(Screen):
    def __init__(self, exam_code, student_id, **kwargs):
        super(ExamInterfacePage, self).__init__(**kwargs)
        self.exam_code = exam_code  # 保存考試代碼
        self.student_id = student_id  # 保存學生ID
        layout = BoxLayout(orientation='vertical', padding=[50, 20, 50, 20], spacing=20)

        # 標題使用粉圓體字體顯示
        label = Label(text="考試介面、規則", font_size=48, font_name="BiauKai", size_hint_y=None, height=100)
        
        # 使用 AnchorLayout 將標題固定在頂部
        top_layout = AnchorLayout(anchor_x='center', anchor_y='top')
        top_layout.add_widget(label)
        layout.add_widget(top_layout)

        # 在標題和表格之間增加空白區域
        layout.add_widget(Widget(size_hint_y=None, height=20))
        
        # 使用 ScrollView 來包裹內容，允許滾動
        scroll_view = ScrollView(size_hint=(1, None), size=(self.width, 450))
        
        # content_layout 作為包裹內容的 BoxLayout，並允許滾動
        self.content_layout = BoxLayout(orientation='vertical', spacing=10, size_hint_y=None, padding=[20, 20, 20, 20])
        self.content_layout.bind(minimum_height=self.content_layout.setter('height'))

        # 添加半透明白色背景圓角矩形以凸顯內容
        with self.content_layout.canvas.before:
            Color(1, 1, 1, 0.6)  # 設置白色半透明背景
            self.rect = RoundedRectangle(size=(self.content_layout.width, self.content_layout.height), 
                                         pos=self.content_layout.pos, radius=[20, 20, 20, 20])
        self.content_layout.bind(pos=self.update_rect, size=self.update_rect)

        scroll_view.add_widget(self.content_layout)
        layout.add_widget(scroll_view)

        # 使用 AnchorLayout 將按鈕固定在底部
        bottom_layout = AnchorLayout(anchor_x='center', anchor_y='bottom', size_hint_y=None, height=100)
        
        button_layout = BoxLayout(orientation='horizontal', size_hint=(1, None), height=80, spacing=20)
        
        # 返回首頁按鈕
        back_button = Button(text="返回首頁", font_size=24, size_hint=(0.5, 0.8), font_name="BiauKai")
        back_button.bind(on_press=self.go_back)  
        button_layout.add_widget(back_button)
        
        # 確認按鈕，點擊後進入錄製頁面
        confirm_btn = Button(text="確認", font_size=24, size_hint=(0.5, 0.8), font_name="BiauKai")
        confirm_btn.bind(on_press=self.go_to_recording)
        button_layout.add_widget(confirm_btn)
        
        bottom_layout.add_widget(button_layout)
        layout.add_widget(bottom_layout)
        
        # 將布局添加到畫面
        self.add_widget(layout)

        # 加載考試資料
        self.load_exam_data()

    def update_rect(self, *args):
        # 更新背景矩形的位置和大小
        self.rect.pos = self.content_layout.pos
        self.rect.size = self.content_layout.size

    def load_exam_data(self):
        # 連接到 MySQL 資料庫
        conn = mysql.connector.connect(
                host="localhost",            # 資料庫主機地址
                user="root",                 # 資料庫用戶名
                password="",                 # 資料庫密碼
                database="learning sandbox"  # 資料庫名稱
        )
        cursor = conn.cursor()

        # 查詢考試相關資訊及學生姓名
        cursor.execute("""
            SELECT e.exam_name, e.subject, e.start_time, e.end_time, e.duration, e.hint_function, s.student_name
            FROM exams e
            JOIN students s ON s.student_id = %s
            WHERE e.exam_code = %s
        """, (self.student_id, self.exam_code))
        exam_data = cursor.fetchone()

        conn.close()

        if exam_data:
            exam_name, subject, start_time, end_time, duration, hint_function, student_name = exam_data

            # 根據 hint_function 值設置提示功能狀態
            hint_status = "已開啟" if hint_function == 1 else "未開啟"

            # 動態添加考試資料到介面
            self.add_content_row("名稱  :  ", exam_name)
            self.add_content_row("考生姓名  :  ", student_name)
            self.add_content_row("考生學號  :  ", self.student_id)
            self.add_content_row("科目  :  ", subject)
            self.add_content_row("開放時間  :  ", f"{start_time} ~ {end_time}")
            self.add_content_row("作答時長  :  ", duration)
            self.add_content_row("提示功能  :  ", hint_status)
            self.add_content_row("作答說明/師長叮嚀  :  ", "不能使用ChatGPT等AI工具或開書考\n本次考試可以上網自行尋求解題素材，但是不可以與他人或智慧機器人交談取得答案")

    def add_content_row(self, title, content):
        # 動態添加考試資料每一行的標題和內容
        row_layout = AnchorLayout(size_hint_y=None, height=40)
        row_content = BoxLayout(orientation='horizontal')
        title_label = Label(text=title, font_size=24, font_name="BiauKai", size_hint_x=0.3, halign="right", valign="middle", color=(0, 0, 0, 1))
        title_label.bind(size=lambda *x: title_label.setter('text_size')(title_label, (title_label.width, None)))
        content_label = Label(text=content, font_size=24, font_name="BiauKai", size_hint_x=0.7, halign="left", valign="middle", color=(0, 0, 0, 1))
        content_label.bind(size=lambda *x: content_label.setter('text_size')(content_label, (content_label.width, None)))
        row_content.add_widget(title_label)
        row_content.add_widget(content_label)
        row_layout.add_widget(row_content)
        self.content_layout.add_widget(row_layout)

    def go_back(self, instance):
        # 設置向右滑動過渡動畫並返回首頁
        self.manager.transition = SlideTransition(direction='right')
        self.manager.current = 'home'

    def go_to_recording(self, instance):
        # 獲取學生ID和考試代碼
        student_id = self.student_id
        exam_code = self.exam_code

        # 移除舊的 RecordingPage
        if self.manager.has_screen('recording_page'):
            old_screen = self.manager.get_screen('recording_page')
            self.manager.remove_widget(old_screen)

        # 添加新的 RecordingPage 並傳遞學生ID和考試代碼
        recording_page = RecordingPage(name='recording_page', student_id=student_id, exam_code=exam_code)
        self.manager.add_widget(recording_page)
        
        # 切換到錄製頁面
        self.manager.transition = SlideTransition(direction='left')
        self.manager.current = 'recording_page'
