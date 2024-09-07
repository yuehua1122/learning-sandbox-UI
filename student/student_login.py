from kivy.uix.screenmanager import Screen, SlideTransition
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.core.text import LabelBase
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.popup import Popup
import mysql.connector
from datetime import datetime

from student.exam_interface_page import ExamInterfacePage

# 註冊粉圓體字體
LabelBase.register(name="BiauKai", fn_regular="font/粉圓體.ttf")

class CenteredTextInput(TextInput):
    def __init__(self, **kwargs):
        super(CenteredTextInput, self).__init__(**kwargs)
        self.halign = 'center'  # 設置水平居中
        self.valign = 'middle'  # 設置垂直居中
        self.bind(size=self.update_text_size)

    def update_text_size(self, *args):
        # 更新文本框大小以保持居中
        self.text_size = (self.width, None)

class StudentLoginPage(Screen):
    def __init__(self, **kwargs):
        super(StudentLoginPage, self).__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=50, spacing=10)  # 設置主佈局，垂直方向排列
        
        # 標籤顯示學生身分，使用粉圓體顯示字體
        label = Label(text="使用者身分: 學生", font_size=48, font_name="BiauKai", size_hint_y=None, height=60)  
        layout.add_widget(label)
        
        # 標籤提示輸入考試代碼
        exam_code_label = Label(text="請輸入考試代碼：", font_size=28, size_hint=(1.0, 0.5), font_name="BiauKai")
        layout.add_widget(exam_code_label)
        
        # 中心對齊的文字輸入框，用於輸入考試代碼
        self.exam_code_input = CenteredTextInput(font_size=32, size_hint=(0.5, 0.3), pos_hint={'center_x': 0.5}, font_name="BiauKai")
        layout.add_widget(self.exam_code_input)
        
        # 標籤提示輸入學號
        student_id_label = Label(text="請輸入學號：", font_size=28, size_hint=(1.0, 0.5), font_name="BiauKai")
        layout.add_widget(student_id_label)
        
        # 中心對齊的文字輸入框，用於輸入學號
        self.student_id_input = CenteredTextInput(font_size=32, size_hint=(0.5, 0.3), pos_hint={'center_x': 0.5}, font_name="BiauKai")
        layout.add_widget(self.student_id_input)
        
        # 使用 AnchorLayout 將按鈕固定在底部
        bottom_layout = AnchorLayout(anchor_x='center', anchor_y='bottom')
        button_layout = BoxLayout(orientation='horizontal', size_hint=(1, None), height=80, spacing=20)
        
        # 上一頁按鈕
        back_btn = Button(text="上一頁", font_size=24, size_hint=(0.5, 0.8), font_name="BiauKai")
        back_btn.bind(on_press=self.go_to_home)  # 綁定返回首頁的函數
        button_layout.add_widget(back_btn)

        # 確認按鈕
        start_btn = Button(text="確認", font_size=24, size_hint=(0.5, 0.8), font_name="BiauKai")
        start_btn.bind(on_press=self.go_to_exam_interface)  # 綁定進入考試介面的函數
        button_layout.add_widget(start_btn)
        
        # 將按鈕布局添加到底部布局中
        bottom_layout.add_widget(button_layout)
        # 將底部布局添加到主布局中
        layout.add_widget(bottom_layout)
        
        # 將佈局添加到 Screen 中
        self.add_widget(layout)

    def check_exam_validity(self, student_id, exam_code):
        # 連接到 MySQL 資料庫
        conn = mysql.connector.connect(
                host="localhost",            # 資料庫主機地址
                user="root",                 # 資料庫用戶名
                password="",                 # 資料庫密碼
                database="learning sandbox"  # 資料庫名稱
        )
        cursor = conn.cursor()

        # 檢查是否存在該學生
        cursor.execute("SELECT COUNT(*) FROM students WHERE student_id = %s", (student_id,))
        student_exists = cursor.fetchone()[0] > 0

        if not student_exists:
            conn.close()
            return False, "學生不存在"  # 學生不存在提示訊息
        
        # 檢查是否存在該考試代碼
        cursor.execute("SELECT start_time, end_time FROM exams WHERE exam_code = %s", (exam_code,))
        exam_row = cursor.fetchone()

        if exam_row is None:
            conn.close()
            return False, "考試不存在"  # 考試代碼無效提示訊息

        start_time, end_time = exam_row
        current_time = datetime.now()

        # 檢查當前時間是否在考試時間範圍內
        if not (start_time <= current_time <= end_time):
            conn.close()
            return False, "考試不在有效時間範圍內"  # 考試時間無效提示訊息

        # 檢查學生是否已參加過該考試
        cursor.execute("""
            SELECT COUNT(*) FROM student_exams 
            WHERE student_id = %s AND exam_code = %s
        """, (student_id, exam_code))
        exam_taken = cursor.fetchone()[0] > 0

        if exam_taken:
            conn.close()
            return False, "您已參加過該場考試"  # 提示學生已參加過考試

        conn.close()
        return True, ""  # 考試有效，返回True

    def go_to_exam_interface(self, instance):
        # 從輸入框中獲取學號和考試代碼
        student_id = self.student_id_input.text.strip()
        exam_code = self.exam_code_input.text.strip()

        # 檢查學生ID和考試代碼是否有效
        valid, message = self.check_exam_validity(student_id, exam_code)

        if valid:
            # 檢查是否已經存在一個名為 'exam_interface' 的 Screen
            if self.manager.has_screen('exam_interface'):
                # 如果存在，先移除舊的 Screen
                old_screen = self.manager.get_screen('exam_interface')
                self.manager.remove_widget(old_screen)

            # 創建並添加新屏幕
            exam_page = ExamInterfacePage(name='exam_interface', exam_code=exam_code, student_id=student_id)
            self.manager.add_widget(exam_page)
            
            self.clear_inputs()  # 清空輸入框

            # 切換到 'exam_interface' 頁面
            self.manager.transition = SlideTransition(direction='left')
            self.manager.current = 'exam_interface'
        else:
            # 如果無效，顯示錯誤訊息，並套用字體
            popup = Popup(title='錯誤', 
                        title_font="BiauKai",
                        content=Label(text=message, font_name="BiauKai", font_size=24), 
                        size_hint=(0.6, 0.4))
            popup.open()

    def go_to_home(self, instance):
        # 設置向右滑動過渡動畫並返回首頁
        self.clear_inputs()  # 清空輸入框
        self.manager.transition = SlideTransition(direction='right')
        self.manager.current = 'home'

    def clear_inputs(self):
        # 清空輸入框
        self.student_id_input.text = ''
        self.exam_code_input.text = ''
