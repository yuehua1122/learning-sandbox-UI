import calendar
import random
import string
import os
import time
import mysql.connector
from kivy.uix.screenmanager import Screen, SlideTransition
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.dropdown import DropDown
from kivy.uix.scrollview import ScrollView
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.popup import Popup
from kivy.uix.filechooser import FileChooserIconView
from kivy.core.text import LabelBase
from kivy.uix.checkbox import CheckBox

# 註冊粉圓體字體
LabelBase.register(name="BiauKai", fn_regular="font/粉圓體.ttf")

class AddExamPage(Screen):
    def __init__(self, **kwargs):
        super(AddExamPage, self).__init__(**kwargs)
        self.teacher_id = None  # 用於保存 teacher_id
        self.restricted_websites = []  # 保存選擇的禁用網站
        layout = BoxLayout(orientation='vertical', padding=20, spacing=20)

        # 上方部分
        top_layout = AnchorLayout(anchor_x='center', anchor_y='center', size_hint=(1, 0.2))
        title_label = Label(text="新增考試", font_size=48, font_name="BiauKai", size_hint=(None, None))
        top_layout.add_widget(title_label)
        layout.add_widget(top_layout)

        # 中間部分
        middle_layout = BoxLayout(orientation='vertical', size_hint=(1, 0.6))
        scroll_view = ScrollView(size_hint=(1, None), size=(self.width, 400))

        form_layout = GridLayout(cols=2, padding=10, spacing=10, size_hint_y=None)
        form_layout.bind(minimum_height=form_layout.setter('height'))

        # 名稱 (下拉式選單)
        self.name_dropdown = DropDown()
        for name in ["Java程式設計(一)", "Python程式設計(一)"]:
            btn = Button(text=name, size_hint_y=None, height=44, font_name="BiauKai")
            btn.bind(on_release=lambda btn: self.name_dropdown.select(btn.text))
            self.name_dropdown.add_widget(btn)

        self.name_main_button = Button(text='選擇名稱', size_hint=(1.2, None), height=40, font_name="BiauKai")
        self.name_main_button.bind(on_release=self.name_dropdown.open)
        self.name_dropdown.bind(on_select=lambda instance, x: setattr(self.name_main_button, 'text', x))

        form_layout.add_widget(Label(text="名稱:", font_size=22, font_name="BiauKai"))
        form_layout.add_widget(self.name_main_button)

        # 科目
        self.subject_input = TextInput(font_size=22, size_hint=(1.2, None), height=40, font_name="BiauKai")
        form_layout.add_widget(Label(text="科目:", font_size=22, font_name="BiauKai"))
        form_layout.add_widget(self.subject_input)

        # 開放時間(開始)
        self.start_time_button = Button(text="選擇開始時間", size_hint=(0.6, None), height=40, font_name="BiauKai")
        self.start_time_button.bind(on_release=lambda x: self.open_time_selector('start'))
        self.start_time_label = Label(text="", font_size=18, font_name="BiauKai", size_hint=(0.6, None), height=40)
        
        start_time_layout = BoxLayout(orientation='horizontal', size_hint=(1.2, None), height=40)
        start_time_layout.add_widget(self.start_time_button)
        start_time_layout.add_widget(self.start_time_label)
        
        form_layout.add_widget(Label(text="開放時間(開始):", font_size=22, font_name="BiauKai"))
        form_layout.add_widget(start_time_layout)

        # 開放時間(結束)
        self.end_time_button = Button(text="選擇結束時間", size_hint=(0.6, None), height=40, font_name="BiauKai")
        self.end_time_button.bind(on_release=lambda x: self.open_time_selector('end'))
        self.end_time_label = Label(text="", font_size=18, font_name="BiauKai", size_hint=(0.6, None), height=40)

        end_time_layout = BoxLayout(orientation='horizontal', size_hint=(1.2, None), height=40)
        end_time_layout.add_widget(self.end_time_button)
        end_time_layout.add_widget(self.end_time_label)

        form_layout.add_widget(Label(text="開放時間(結束):", font_size=22, font_name="BiauKai"))
        form_layout.add_widget(end_time_layout)

        # 作答時長
        self.duration_input = TextInput(font_size=22, size_hint=(1.2, None), height=40, font_name="BiauKai")
        form_layout.add_widget(Label(text="作答時長:", font_size=22, font_name="BiauKai"))
        form_layout.add_widget(self.duration_input)

        # 考試類型 (下拉式選單)
        self.exam_type_dropdown = DropDown()
        for exam_type in ["小考", "期中考", "期末考"]:
            btn = Button(text=exam_type, size_hint_y=None, height=44, font_name="BiauKai")
            btn.bind(on_release=lambda btn: self.exam_type_dropdown.select(btn.text))
            self.exam_type_dropdown.add_widget(btn)
        self.exam_type_main_button = Button(text='選擇考試類型', size_hint=(1.2, None), height=40, font_name="BiauKai")
        self.exam_type_main_button.bind(on_release=self.exam_type_dropdown.open)
        self.exam_type_dropdown.bind(on_select=lambda instance, x: setattr(self.exam_type_main_button, 'text', x))

        form_layout.add_widget(Label(text="考試類型:", font_size=22, font_name="BiauKai"))
        form_layout.add_widget(self.exam_type_main_button)

        # 考試代碼 (隨機生成六位代碼)
        self.exam_code = self.generate_exam_code()
        self.exam_code_label = Label(text=self.exam_code, font_size=22, size_hint=(1.2, None), height=40, font_name="BiauKai")
        form_layout.add_widget(Label(text="考試代碼:", font_size=22, font_name="BiauKai"))
        form_layout.add_widget(self.exam_code_label)

        # 上傳題目
        self.exam_file = ""
        exam_file_layout = BoxLayout(orientation='horizontal', size_hint=(1.2, None), height=40)
        self.upload_exam_button = Button(text="選擇檔案", size_hint=(0.5, 1), font_name="BiauKai")
        self.upload_exam_button.bind(on_press=lambda x: self.open_file_chooser('exam'))
        self.exam_file_label = Label(text="", font_size=18, font_name="BiauKai", size_hint=(0.5, 1))
        exam_file_layout.add_widget(self.upload_exam_button)
        exam_file_layout.add_widget(self.exam_file_label)
        form_layout.add_widget(Label(text="上傳題目:", font_size=22, font_name="BiauKai"))
        form_layout.add_widget(exam_file_layout)

        # 上傳評分標準
        self.grading_file = ""
        grading_file_layout = BoxLayout(orientation='horizontal', size_hint=(1.2, None), height=40)
        self.upload_grading_button = Button(text="選擇檔案", size_hint=(0.5, 1), font_name="BiauKai")
        self.upload_grading_button.bind(on_press=lambda x: self.open_file_chooser('grading'))
        self.grading_file_label = Label(text="", font_size=18, font_name="BiauKai", size_hint=(0.5, 1))
        grading_file_layout.add_widget(self.upload_grading_button)
        grading_file_layout.add_widget(self.grading_file_label)
        form_layout.add_widget(Label(text="上傳評分標準:", font_size=22, font_name="BiauKai"))
        form_layout.add_widget(grading_file_layout)

        # 提示功能 (開或關)
        self.hint_dropdown = DropDown()
        for option in ["開", "關"]:
            btn = Button(text=option, size_hint_y=None, height=44, font_name="BiauKai")
            btn.bind(on_release=lambda btn: self.hint_dropdown.select(btn.text))
            self.hint_dropdown.add_widget(btn)
        self.hint_main_button = Button(text='選擇提示功能', size_hint=(1.2, None), height=40, font_name="BiauKai")
        self.hint_main_button.bind(on_release=self.hint_dropdown.open)
        self.hint_dropdown.bind(on_select=lambda instance, x: setattr(self.hint_main_button, 'text', x))

        form_layout.add_widget(Label(text="提示功能:", font_size=22, font_name="BiauKai"))
        form_layout.add_widget(self.hint_main_button)
        
        # 禁用的網站 (顯示CheckBox和網站名稱)
        websites_dict = {
                "ChatGPT": "chatgpt.com", 
                "Claude": "claude.ai",
                "Codeium": "codeium.com", 
                "AI21 Labs": "studio.ai21.com",
                "Copilot": "copilot.cloud.microsoft", 
                "Messenger": "www.messenger.com",
                "LINE": "uts-front.line-apps.com" ,
        }

        self.checkbox_dict = {}  # 用來存放每個網站的CheckBox

        form_layout.add_widget(Label(text="禁用的網站:", font_size=22, font_name="BiauKai"))

        # 為每個網站生成一個垂直的CheckBox和網站名稱
        website_layout = BoxLayout(orientation='vertical', size_hint=(1.2, None), height=280)
        for name, site in websites_dict.items():
            site_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=40, size_hint_x=None, width=250, spacing=150)
            checkbox = CheckBox()
            checkbox.bind(active=lambda checkbox, value, site=site: self.on_checkbox_active(checkbox, value, site))
            self.checkbox_dict[site] = checkbox  # 將 CheckBox 和網站網址存入字典
            site_layout.add_widget(checkbox)
            site_layout.add_widget(Label(text=name, font_size=18, font_name="BiauKai", halign='left', size_hint_x=0.8, text_size=(300, None)))
            website_layout.add_widget(site_layout)
        form_layout.add_widget(website_layout)

        scroll_view.add_widget(form_layout)
        middle_layout.add_widget(scroll_view)
        layout.add_widget(middle_layout)              

        # 底部部分
        bottom_layout = AnchorLayout(anchor_x='center', anchor_y='bottom', size_hint=(1, 0.2))
        button_layout = BoxLayout(orientation='horizontal', size_hint=(1, None), height=80, spacing=20)

        # 上一頁按鈕
        back_button = Button(text="上一頁", font_size=24, size_hint=(0.4, 0.8), font_name="BiauKai")
        back_button.bind(on_press=self.go_back)
        button_layout.add_widget(back_button)

        # 確定按鈕
        confirm_button = Button(text="確定", font_size=24, size_hint=(0.4, 0.8), font_name="BiauKai")
        confirm_button.bind(on_press=lambda x: self.save_exam_to_db(
            self.teacher_id,
            self.name_main_button.text, 
            self.subject_input.text, 
            self.start_time_label.text, 
            self.end_time_label.text, 
            self.duration_input.text,
            self.exam_type_main_button.text, 
            self.exam_code, 
            self.exam_file, 
            self.grading_file,
            self.hint_main_button.text,
            self.restricted_websites
        ))
        button_layout.add_widget(confirm_button)

        bottom_layout.add_widget(button_layout)
        layout.add_widget(bottom_layout)

        self.add_widget(layout)

    def on_checkbox_active(self, checkbox, value, site):
        """處理Checkbox選中狀態變更"""
        if value:
            self.restricted_websites.append(site)
        else:
            if site in self.restricted_websites:
                self.restricted_websites.remove(site)

    def open_time_selector(self, time_type):
        year_dropdown = DropDown()
        month_dropdown = DropDown()
        day_dropdown = DropDown()
        hour_dropdown = DropDown()
        minute_dropdown = DropDown()

        current_time = time.localtime()
        selected_year = current_time.tm_year
        selected_month = current_time.tm_mon
        selected_day = current_time.tm_mday
        selected_hour = current_time.tm_hour
        selected_minute = current_time.tm_min

        # 更新天數下拉列表
        def update_days(year, month):
            day_dropdown.clear_widgets()
            days_in_month = calendar.monthrange(year, month)[1]
            for day in range(1, days_in_month + 1):
                btn = Button(text=str(day).zfill(2), size_hint_y=None, height=44, font_name="BiauKai")
                btn.bind(on_release=lambda btn: day_dropdown.select(btn.text))
                day_dropdown.add_widget(btn)
            day_dropdown.select(str(selected_day).zfill(2))

        def on_year_selected(btn):
            nonlocal selected_year
            selected_year = int(btn.text)
            year_dropdown.select(btn.text)
            update_days(selected_year, selected_month)

        def on_month_selected(btn):
            nonlocal selected_month
            selected_month = int(btn.text)
            month_dropdown.select(btn.text)
            update_days(selected_year, selected_month)

        for year in range(selected_year, selected_year + 5):
            btn = Button(text=str(year), size_hint_y=None, height=44, font_name="BiauKai")
            btn.bind(on_release=on_year_selected)
            year_dropdown.add_widget(btn)
        year_dropdown.select(str(selected_year))

        for month in range(1, 13):
            btn = Button(text=str(month).zfill(2), size_hint_y=None, height=44, font_name="BiauKai")
            btn.bind(on_release=on_month_selected)
            month_dropdown.add_widget(btn)
        month_dropdown.select(str(selected_month).zfill(2))

        for hour in range(0, 24):
            btn = Button(text=str(hour).zfill(2), size_hint_y=None, height=44, font_name="BiauKai")
            btn.bind(on_release=lambda btn: hour_dropdown.select(btn.text))
            hour_dropdown.add_widget(btn)
        hour_dropdown.select(str(selected_hour).zfill(2))

        for minute in range(0, 60, 5):
            btn = Button(text=str(minute).zfill(2), size_hint_y=None, height=44, font_name="BiauKai")
            btn.bind(on_release=lambda btn: minute_dropdown.select(btn.text))
            minute_dropdown.add_widget(btn)
        nearest_minute = (selected_minute // 5) * 5
        minute_dropdown.select(str(nearest_minute).zfill(2))

        update_days(selected_year, selected_month)

        time_selector_layout = BoxLayout(orientation='horizontal', spacing=10)

        year_button = Button(text=str(selected_year), size_hint_y=None, height=40, font_name="BiauKai")
        month_button = Button(text=str(selected_month).zfill(2), size_hint_y=None, height=40, font_name="BiauKai")
        day_button = Button(text=str(selected_day).zfill(2), size_hint_y=None, height=40, font_name="BiauKai")
        hour_button = Button(text=str(selected_hour).zfill(2), size_hint_y=None, height=40, font_name="BiauKai")
        minute_button = Button(text=str(nearest_minute).zfill(2), size_hint_y=None, height=40, font_name="BiauKai")

        year_button.bind(on_release=year_dropdown.open)
        month_button.bind(on_release=month_dropdown.open)
        day_button.bind(on_release=day_dropdown.open)
        hour_button.bind(on_release=hour_dropdown.open)
        minute_button.bind(on_release=minute_dropdown.open)

        year_dropdown.bind(on_select=lambda instance, x: setattr(year_button, 'text', x))
        month_dropdown.bind(on_select=lambda instance, x: setattr(month_button, 'text', x))
        day_dropdown.bind(on_select=lambda instance, x: setattr(day_button, 'text', x))
        hour_dropdown.bind(on_select=lambda instance, x: setattr(hour_button, 'text', x))
        minute_dropdown.bind(on_select=lambda instance, x: setattr(minute_button, 'text', x))

        time_selector_layout.add_widget(year_button)
        time_selector_layout.add_widget(month_button)
        time_selector_layout.add_widget(day_button)
        time_selector_layout.add_widget(hour_button)
        time_selector_layout.add_widget(minute_button)

        popup_content = BoxLayout(orientation='vertical', spacing=10)
        popup_content.add_widget(time_selector_layout)

        buttons_layout = BoxLayout(orientation='horizontal', spacing=10)

        def confirm_time_selection(instance):
            if (year_button.text == "年" or month_button.text == "月" or 
                day_button.text == "日" or hour_button.text == "時" or 
                minute_button.text == "分"):
                self.show_error_popup("請選擇完整的時間")
                return

            selected_time = f"{year_button.text}-{month_button.text}-{day_button.text} {hour_button.text}:{minute_button.text}:00"
            if time_type == 'start':
                self.start_time_label.text = selected_time
            elif time_type == 'end':
                self.end_time_label.text = selected_time
            popup.dismiss()

        confirm_button = Button(text="確認", size_hint_y=None, height=40, font_name="BiauKai")
        confirm_button.bind(on_press=confirm_time_selection)
        cancel_button = Button(text="取消", size_hint_y=None, height=40, font_name="BiauKai")
        cancel_button.bind(on_press=lambda x: popup.dismiss())

        buttons_layout.add_widget(confirm_button)
        buttons_layout.add_widget(cancel_button)

        popup_content.add_widget(buttons_layout)

        popup = Popup(title="選擇時間", content=popup_content, size_hint=(0.6, 0.5), title_font="BiauKai")
        popup.open()
        
    def open_file_chooser(self, file_type):
        # 每次創建一個新的文件選擇器窗口
        filechooser = FileChooserIconView(filters=['*.pdf'], path=os.getcwd())
        
        # 設置選擇文件的功能
        filechooser_popup = Popup(
            title="選擇檔案", 
            size_hint=(0.8, 0.8),
            title_font="BiauKai"  # 設置標題字體
        )

        # 允許用戶選擇文件並返回
        def select_file(instance):
            selected_file = filechooser.selection
            if selected_file:
                if file_type == 'exam':
                    self.exam_file = selected_file[0]
                    self.exam_file_label.text = f"已選擇檔案: {os.path.basename(selected_file[0])}"
                elif file_type == 'grading':
                    self.grading_file = selected_file[0]
                    self.grading_file_label.text = f"已選擇檔案: {os.path.basename(selected_file[0])}"
            filechooser_popup.dismiss()

        # 創建彈出視窗中的選擇按鈕
        select_button = Button(text="選擇", size_hint=(1, 0.2), font_name="BiauKai")
        select_button.bind(on_press=select_file)

        # 組合文件選擇器和選擇按鈕
        layout = BoxLayout(orientation='vertical')
        layout.add_widget(filechooser)
        layout.add_widget(select_button)
        
        # 設置彈出窗口內容和字體
        filechooser_popup.content = layout
        filechooser_popup.open()    

    def generate_exam_code(self):
        while True:
            letters = random.sample(string.ascii_uppercase, 3)
            digits = random.sample(string.digits, 3)
            exam_code = ''.join(letters + digits)
            
            # 檢查是否已存在相同的考試代碼
            conn = mysql.connector.connect(
                host="localhost",
                user="root",
                password="",
                database="learning sandbox"
            )
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM exams WHERE exam_code = %s", (exam_code,))
            result = cursor.fetchone()
            cursor.close()
            conn.close()
            
            if result[0] == 0:  # 如果沒有重複，則返回該考試代碼
                return exam_code
            
    def set_teacher_id(self, teacher_id):
        """設置教師ID"""
        self.teacher_id = teacher_id

    def save_exam_to_db(self, teacher_id, name, subject, start_time, end_time, duration, exam_type, exam_code, exam_file, grading_file, hint_function, restricted_websites):
        # 檢查每個欄位是否已填寫
        if not name or name == "選擇名稱":
            self.show_error_popup("請選擇考試名稱")
            return
        if not subject:
            self.show_error_popup("請輸入科目名稱")
            return
        if not start_time:
            self.show_error_popup("請選擇開放時間(開始)")
            return
        if not end_time:
            self.show_error_popup("請選擇開放時間(結束)")
            return
        if not duration:
            self.show_error_popup("請輸入作答時長")
            return
        if not exam_type or exam_type == "選擇考試類型":
            self.show_error_popup("請選擇考試類型")
            return
        if not exam_file:
            self.show_error_popup("請上傳題目檔案")
            return
        if not grading_file:
            self.show_error_popup("請上傳評分標準檔案")
            return
        if not hint_function or hint_function == "選擇提示功能":
            self.show_error_popup("請選擇提示功能")
            return
        if not restricted_websites:
            restricted_websites_str = ""
        else:
            restricted_websites_str = ','.join(restricted_websites)

        try:
            # 讀取上傳的檔案內容並獲取檔案名稱
            exam_file_blob = None
            grading_file_blob = None
            exam_file_name = None
            grading_file_name = None
            
            if exam_file:
                with open(exam_file, 'rb') as file:  # 使用二進制模式讀取
                    exam_file_blob = file.read()
                exam_file_name = os.path.basename(exam_file)  # 保存檔案名稱

            if grading_file:
                with open(grading_file, 'rb') as file:  # 使用二進制模式讀取
                    grading_file_blob = file.read()
                grading_file_name = os.path.basename(grading_file)

            conn = mysql.connector.connect(
                host="localhost",
                user="root",
                password="",
                database="learning sandbox",
                charset="utf8mb4"  # 設定連線為 UTF-8 編碼
            )
            cursor = conn.cursor()

            # 查詢資料庫內最大的 ID
            cursor.execute("SELECT MAX(id) FROM exams")
            max_id = cursor.fetchone()[0]
            if max_id is None:
                max_id = 0  # 如果資料庫內沒有資料，從 0 開始
            new_id = max_id + 1

            # 新增資料到資料庫
            query = """
                INSERT INTO exams (id, teacher_id, exam_name, subject, start_time, end_time, duration, exam_type, exam_code, exam_file, exam_file_name, grading_file, grading_file_name, hint_function, restricted_websites)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(query, (
                new_id, teacher_id, name, subject, start_time, end_time, duration, exam_type, 
                exam_code, exam_file_blob, exam_file_name, grading_file_blob, grading_file_name, hint_function, restricted_websites_str
            ))
            conn.commit()
            cursor.close()
            conn.close()
            self.show_success_popup("新增成功")
            self.clear_form()  # 清空表單
        except mysql.connector.Error as err:
            self.show_error_popup(f"錯誤: {err}")

    def clear_form(self):
        # 重置所有輸入欄位和下拉選單
        self.name_main_button.text = '選擇名稱'
        self.subject_input.text = ''
        self.start_time_label.text = ''
        self.end_time_label.text = ''
        self.duration_input.text = ''
        self.exam_type_main_button.text = '選擇考試類型'
        self.exam_code = self.generate_exam_code()
        self.exam_code_label.text = self.exam_code
        self.exam_file = ''
        self.exam_file_label.text = ''
        self.grading_file = ''
        self.grading_file_label.text = ''
        self.hint_main_button.text = '選擇提示功能'
        self.restricted_websites = []  # 清空禁用網站
        
        # 取消所有复选框勾选状态
        for site, checkbox in self.checkbox_dict.items():
            if isinstance(checkbox, CheckBox):
                checkbox.active = False

    def show_success_popup(self, message):
        popup = Popup(
            title="成功", 
            title_font="BiauKai",  # 設置標題字體
            content=Label(text=message, font_size=24, font_name="BiauKai"), 
            size_hint=(0.6, 0.4)
        )
        popup.open()

    def show_error_popup(self, message):
        popup = Popup(
            title="錯誤", 
            title_font="BiauKai",  # 設置標題字體
            content=Label(text=message, font_size=24, font_name="BiauKai"), 
            size_hint=(0.6, 0.4)
        )
        popup.open()
        
    def go_back(self, instance):
        self.clear_form()  # 清空表單
        self.manager.transition = SlideTransition(direction='right')
        self.manager.current = 'upload'