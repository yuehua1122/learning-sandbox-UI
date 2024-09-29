import os
import time
import mysql.connector
from kivy.uix.screenmanager import Screen, SlideTransition
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.core.text import LabelBase
from kivy.uix.anchorlayout import AnchorLayout
import webbrowser
from student.recording_in_progress_page import RecordingInProgressPage

# 註冊粉圓體字體
LabelBase.register(name="BiauKai", fn_regular="font/粉圓體.ttf")

class RecordingPage(Screen):
    def __init__(self, student_id, exam_code, **kwargs):
        super(RecordingPage, self).__init__(**kwargs)
        self.student_id = student_id  # 保存學生ID
        self.exam_code = exam_code  # 保存考試代碼
        self.exam_file = None  # 保存考試文件路徑
        self.exam_file_name = None  # 保存考試文件名稱
        self.pdf_directory = "pdf"  # 設定存放PDF的目錄
        self.pdf_filename = "說明書.pdf"  # 預設PDF文件名稱
        self.pdf_path = os.path.join(self.pdf_directory, self.pdf_filename)  # PDF完整路徑

        layout = BoxLayout(orientation='vertical', padding=50, spacing=20)
        
        # 標題文字顯示，使用粉圓體字體
        label = Label(text="考試錄製", font_size=48, font_name="BiauKai")
        layout.add_widget(label)
        
        # 提示考試開始後不可暫停
        note = "開始錄製後無法暫停，且將記錄所有操作行為，請注意。"
        note_label = Label(text=note, font_size=24, font_name="BiauKai")
        layout.add_widget(note_label)

        # 加載考試文件
        self.load_exam_file()

        # 題目下載區
        download_layout = AnchorLayout(size_hint_y=None, height=40, pos_hint={'center_x': 0.4})
        download_content = BoxLayout(orientation='horizontal', spacing=10, size_hint_x=None)
        download_label = Label(text="題目下載 :", font_size=24, font_name="BiauKai", size_hint_x=None, width=100)
        download_content.add_widget(download_label)
        
        # 固定顯示 "說明書.pdf" 並可點擊下載
        download_link = Button(text=self.pdf_filename, font_size=24, font_name="BiauKai", size_hint_x=None, width=200, background_color=(0, 0, 0, 0), color=(1, 0, 0, 1), underline=True)
        download_link.bind(on_press=self.download_file)
        download_content.add_widget(download_link)
        
        download_layout.add_widget(download_content)
        layout.add_widget(download_layout)
        
        # 將按鈕固定在底部
        bottom_layout = AnchorLayout(anchor_x='center', anchor_y='bottom')
        button_layout = BoxLayout(orientation='horizontal', size_hint=(1, None), height=80, spacing=20)
        
        # 返回按鈕
        back_btn = Button(text="上一頁", font_size=24, size_hint=(0.5, 0.8), font_name="BiauKai")
        back_btn.bind(on_press=self.go_back) 
        button_layout.add_widget(back_btn)

        # 開始錄製按鈕
        start_btn = Button(text="開始錄製", font_size=24, size_hint=(0.5, 0.8), font_name="BiauKai")
        start_btn.bind(on_press=self.go_to_recording_in_progress)
        button_layout.add_widget(start_btn)
        
        bottom_layout.add_widget(button_layout)
        layout.add_widget(bottom_layout)
        
        self.add_widget(layout)

    def load_exam_file(self):
        # 確保PDF目錄存在
        os.makedirs(self.pdf_directory, exist_ok=True)
        
        # 連接到資料庫並獲取 exam_file 和 exam_file_name
        conn = None
        cursor = None
        try:
            conn = mysql.connector.connect(
                    host="localhost",            # 資料庫主機地址
                    user="root",                 # 資料庫用戶名
                    password="",                 # 資料庫密碼
                    database="learning sandbox", # 資料庫名稱
                    use_unicode=True     
            )
            cursor = conn.cursor()

            # 查詢考試文件
            cursor.execute("""SELECT exam_file, exam_file_name FROM exams WHERE exam_code = %s""", (self.exam_code,))
            result = cursor.fetchone()

            if result:
                self.exam_file = result[0]  # 考試文件BLOB
                self.exam_file_name = result[1]  # 考試文件名稱

                # 將BLOB數據保存為PDF文件
                with open(self.pdf_path, 'wb') as file:
                    file.write(self.exam_file)

        except mysql.connector.Error as err:
            print(f"資料庫錯誤: {err}")

        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    def download_file(self, instance):
        # 打開下載的PDF文件
        if os.path.exists(self.pdf_path):
            webbrowser.open(os.path.abspath(self.pdf_path))

    def go_back(self, instance):
        # 切換回考試介面頁面
        self.manager.transition = SlideTransition(direction='right')
        self.manager.current = 'exam_interface'

    def go_to_recording_in_progress(self, instance):
        conn = None  # 初始化資料庫連接變量
        cursor = None
        try:
            conn = mysql.connector.connect(
                host="localhost",            # 資料庫主機地址
                user="root",                 # 資料庫用戶名
                password="",                 # 資料庫密碼
                database="learning sandbox"  # 資料庫名稱
            )
            cursor = conn.cursor()

            # 查詢目前表中的最大ID
            cursor.execute("""SELECT MAX(id) FROM student_exams""")
            result = cursor.fetchone()
            max_id = result[0] if result[0] is not None else 0  # 如果表為空，設置max_id為0

            # 新的ID為最大ID加1
            new_id = max_id + 1

            # 插入新的考試錄製記錄
            start_time = time.strftime('%Y-%m-%d %H:%M:%S')
            cursor.execute("""
                INSERT INTO student_exams (id, student_id, exam_code, start_time)
                VALUES (%s, %s, %s, %s)
            """, (new_id, self.student_id, self.exam_code, start_time))

            conn.commit()

        except mysql.connector.Error as err:
            print(f"資料庫錯誤: {err}")

        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

        # 移除舊的錄製進行中頁面
        if self.manager.has_screen('recording_in_progress'):
            old_screen = self.manager.get_screen('recording_in_progress')
            self.manager.remove_widget(old_screen)

        # 添加新的錄製進行中頁面，並傳遞相關參數
        recording_in_progress_page = RecordingInProgressPage(
            name='recording_in_progress',
            student_id=self.student_id,
            exam_code=self.exam_code,
            file_path=self.pdf_path
        )
        self.manager.add_widget(recording_in_progress_page)

        # 切換到錄製進行中頁面
        self.manager.transition = SlideTransition(direction='left')
        self.manager.current = 'recording_in_progress'
