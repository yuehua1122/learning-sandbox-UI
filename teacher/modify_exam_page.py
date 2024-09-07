import calendar
import os
import mysql.connector
import time
from kivy.uix.screenmanager import Screen, SlideTransition
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.dropdown import DropDown
from kivy.uix.scrollview import ScrollView
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.core.text import LabelBase
from kivy.uix.filechooser import FileChooserIconView

# 註冊粉圓體字體
LabelBase.register(name="BiauKai", fn_regular="font/粉圓體.ttf")

class ModifyExamPage(Screen):
    def __init__(self, **kwargs):
        super(ModifyExamPage, self).__init__(**kwargs)
        self.exam_id = None  # 保存當前要修改的考試ID

        layout = BoxLayout(orientation='vertical', padding=20, spacing=20)

        # 上方部分
        top_layout = AnchorLayout(anchor_x='center', anchor_y='center', size_hint=(1, 0.2))
        title_label = Label(text="修改考試", font_size=48, font_name="BiauKai", size_hint=(None, None))
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
        self.start_time_button.bind(on_release=lambda x: self.open_time_selector('start', self.start_time_label.text or "選擇開始時間"))
        self.start_time_label = Label(text="", font_size=18, font_name="BiauKai", size_hint=(0.6, None), height=40)
        
        start_time_layout = BoxLayout(orientation='horizontal', size_hint=(1.2, None), height=40)
        start_time_layout.add_widget(self.start_time_button)
        start_time_layout.add_widget(self.start_time_label)
        
        form_layout.add_widget(Label(text="開放時間(開始):", font_size=22, font_name="BiauKai"))
        form_layout.add_widget(start_time_layout)

        # 開放時間(結束)
        self.end_time_button = Button(text="選擇結束時間", size_hint=(0.6, None), height=40, font_name="BiauKai")
        self.end_time_button.bind(on_release=lambda x: self.open_time_selector('end', self.end_time_label.text or "選擇結束時間"))
        self.end_time_label = Label(text="", font_size=18, font_name="BiauKai", size_hint=(0.6, None), height=40)

        end_time_layout = BoxLayout(orientation='horizontal', size_hint=(1.2, None), height=40)
        end_time_layout.add_widget(self.end_time_button)
        end_time_layout.add_widget(self.end_time_label)

        form_layout.add_widget(Label(text="開放時間(結束):", font_size=22, font_name="BiauKai"))
        form_layout.add_widget(end_time_layout)
        
        # 作答時間
        self.duration_input = TextInput(font_size=22, size_hint=(1.2, None), height=40, font_name="BiauKai")
        form_layout.add_widget(Label(text="作答時間:", font_size=22, font_name="BiauKai"))
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

        # 考試代碼 (保持不變)
        self.exam_code_label = Label(font_size=22, size_hint=(1.2, None), height=40, font_name="BiauKai")
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
        confirm_button.bind(on_press=lambda x: self.update_exam_in_db())
        button_layout.add_widget(confirm_button)

        bottom_layout.add_widget(button_layout)
        layout.add_widget(bottom_layout)

        self.add_widget(layout)

    def open_time_selector(self, time_type, current_time):
        # 打開時間選擇器彈窗並預填充當前時間
        popup_layout = BoxLayout(orientation='vertical', spacing=10)

        # 初始化時間元素
        try:
            if current_time != "選擇開始時間" and current_time != "選擇結束時間":
                date_part, time_part = current_time.split()
                year, month, day = date_part.split('-')
                hour, minute, _ = time_part.split(':')
            else:
                raise ValueError
        except ValueError:
            # 當 current_time 格式不符合預期時，使用當前時間填充
            year, month, day, hour, minute = time.strftime('%Y-%m-%d-%H-%M').split('-')

        # 创建主按钮
        year_main_button = Button(text=year, size_hint_y=None, height=40, font_name="BiauKai")
        month_main_button = Button(text=month, size_hint_y=None, height=40, font_name="BiauKai")
        day_main_button = Button(text=day, size_hint_y=None, height=40, font_name="BiauKai")
        hour_main_button = Button(text=hour, size_hint_y=None, height=40, font_name="BiauKai")
        minute_main_button = Button(text=minute, size_hint_y=None, height=40, font_name="BiauKai")

        # 创建下拉列表并绑定选择事件
        year_dropdown = DropDown()
        month_dropdown = DropDown()
        day_dropdown = DropDown()
        hour_dropdown = DropDown()
        minute_dropdown = DropDown()

        # 处理年份选择
        current_year = time.localtime().tm_year
        selected_year = int(year)
        selected_month = int(month)

        def update_days():
            day_dropdown.clear_widgets()
            days_in_month = calendar.monthrange(selected_year, selected_month)[1]
            for d in range(1, days_in_month + 1):
                btn = Button(text=f'{d:02}', size_hint_y=None, height=44, font_name="BiauKai")
                btn.bind(on_release=lambda btn: day_dropdown.select(btn.text))
                day_dropdown.add_widget(btn)

        def on_year_selected(btn):
            nonlocal selected_year
            selected_year = int(btn.text)
            year_dropdown.select(btn.text)
            update_days()

        def on_month_selected(btn):
            nonlocal selected_month
            selected_month = int(btn.text)
            month_dropdown.select(btn.text)
            update_days()

        # Populate the year dropdown
        for y in range(current_year, current_year + 5):
            btn = Button(text=str(y), size_hint_y=None, height=44, font_name="BiauKai")
            btn.bind(on_release=on_year_selected)
            year_dropdown.add_widget(btn)
        year_main_button.bind(on_release=year_dropdown.open)
        year_dropdown.bind(on_select=lambda instance, x: setattr(year_main_button, 'text', x))

        # Populate the month dropdown
        for m in range(1, 13):
            btn = Button(text=f'{m:02}', size_hint_y=None, height=44, font_name="BiauKai")
            btn.bind(on_release=on_month_selected)
            month_dropdown.add_widget(btn)
        month_main_button.bind(on_release=month_dropdown.open)
        month_dropdown.bind(on_select=lambda instance, x: setattr(month_main_button, 'text', x))

        # Initialize day dropdown with the selected year and month
        update_days()
        day_main_button.bind(on_release=day_dropdown.open)
        day_dropdown.bind(on_select=lambda instance, x: setattr(day_main_button, 'text', x))

        # Populate the hour dropdown
        for h in range(0, 24):
            btn = Button(text=f'{h:02}', size_hint_y=None, height=44, font_name="BiauKai")
            btn.bind(on_release=lambda btn: hour_dropdown.select(btn.text))
            hour_dropdown.add_widget(btn)
        hour_main_button.bind(on_release=hour_dropdown.open)
        hour_dropdown.bind(on_select=lambda instance, x: setattr(hour_main_button, 'text', x))

        # Populate the minute dropdown
        for m in range(0, 60, 5):
            btn = Button(text=f'{m:02}', size_hint_y=None, height=44, font_name="BiauKai")
            btn.bind(on_release=lambda btn: minute_dropdown.select(btn.text))
            minute_dropdown.add_widget(btn)
        minute_main_button.bind(on_release=minute_dropdown.open)
        minute_dropdown.bind(on_select=lambda instance, x: setattr(minute_main_button, 'text', x))
        
        # 弹窗内容布局
        time_select_layout = BoxLayout(orientation='horizontal', spacing=10)
        time_select_layout.add_widget(year_main_button)
        time_select_layout.add_widget(month_main_button)
        time_select_layout.add_widget(day_main_button)
        time_select_layout.add_widget(hour_main_button)
        time_select_layout.add_widget(minute_main_button)

        # 使時間選擇部分居中
        centered_layout = AnchorLayout(anchor_x='center', anchor_y='center')
        centered_layout.add_widget(time_select_layout)

        popup_layout.add_widget(centered_layout)

        # 確認按鈕
        confirm_button = Button(text="確認", size_hint_y=None, height=40, font_name="BiauKai")
        confirm_button.bind(on_press=lambda x: self.set_time(time_type, year_main_button.text, month_main_button.text, day_main_button.text, hour_main_button.text, minute_main_button.text, popup))
        
        # 取消按鈕
        cancel_button = Button(text="取消", size_hint_y=None, height=40, font_name="BiauKai")
        cancel_button.bind(on_press=lambda x: popup.dismiss())

        # 按钮布局
        buttons_layout = BoxLayout(orientation='horizontal', spacing=10)
        buttons_layout.add_widget(confirm_button)
        buttons_layout.add_widget(cancel_button)

        popup_layout.add_widget(buttons_layout)

        popup = Popup(title="選擇時間", content=popup_layout, size_hint=(0.8, 0.5), title_font="BiauKai")
        popup.open()

    def set_time(self, time_type, year, month, day, hour, minute, popup):
        if not all([year, month, day, hour, minute]):
            self.show_error_popup("請選擇所有時間元素")
            return

        selected_time = f"{year}-{month}-{day} {hour}:{minute}:00"
        
        if time_type == 'start':
            self.start_time_label.text = selected_time
        elif time_type == 'end':
            self.end_time_label.text = selected_time

        popup.dismiss()

    def load_exam_data(self, exam_id):
        self.exam_id = exam_id
        try:
            conn = mysql.connector.connect(
                host="localhost",
                user="root",
                password="",
                database="learning sandbox"
            )
            cursor = conn.cursor()
            cursor.execute("""
                SELECT exam_name, subject, start_time, end_time, 
                    duration, exam_type, exam_code, exam_file_name, grading_file_name, 
                    hint_function 
                FROM exams WHERE id = %s
            """, (exam_id,))
            exam = cursor.fetchone()
            cursor.close()
            conn.close()

            if exam:
                self.name_main_button.text = exam[0]
                self.subject_input.text = exam[1]
                self.start_time_label.text = exam[2].strftime('%Y-%m-%d %H:%M:%S') if exam[2] else "選擇開始時間"
                self.end_time_label.text = exam[3].strftime('%Y-%m-%d %H:%M:%S') if exam[3] else "選擇結束時間"
                self.duration_input.text = exam[4]
                self.exam_type_main_button.text = exam[5]
                self.exam_code_label.text = exam[6]
                self.exam_file_label.text = exam[7]
                self.grading_file_label.text = exam[8]
                self.hint_main_button.text = '開' if exam[9] else '關'

        except mysql.connector.Error as err:
            self.show_error_popup(f"錯誤: {err}")

    def update_exam_in_db(self):
        try:
            # 檢查開放時間格式是否正確
            start_time = self.start_time_label.text
            end_time = self.end_time_label.text

            if start_time == "選擇開始時間" or end_time == "選擇結束時間":
                self.show_error_popup("請選擇正確的開始和結束時間")
                return

            # 確保結束時間大於開始時間
            if end_time <= start_time:
                self.show_error_popup("結束時間需大於開始時間")
                return

            conn = mysql.connector.connect(
                host="localhost",
                user="root",
                password="",
                database="learning sandbox"
            )
            cursor = conn.cursor()
            query = """
                UPDATE exams SET exam_name=%s, subject=%s, start_time=%s, end_time=%s, 
                duration=%s, exam_type=%s, exam_file_name=%s, grading_file_name=%s, 
                hint_function=%s WHERE id=%s
            """
            cursor.execute(query, (
                self.name_main_button.text, 
                self.subject_input.text, 
                start_time, end_time, 
                self.duration_input.text, 
                self.exam_type_main_button.text, 
                self.exam_file_label.text,
                self.grading_file_label.text,
                self.hint_main_button.text == "開",
                self.exam_id
            ))
            conn.commit()
            cursor.close()
            conn.close()
            self.show_success_popup("修改成功")
        except mysql.connector.Error as err:
            self.show_error_popup(f"錯誤: {err}")

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
                    self.exam_file_label.text = os.path.basename(selected_file[0])
                elif file_type == 'grading':
                    self.grading_file = selected_file[0]
                    self.grading_file_label.text = os.path.basename(selected_file[0])
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
        self.manager.transition = SlideTransition(direction='right')
        self.manager.current = 'upload'
