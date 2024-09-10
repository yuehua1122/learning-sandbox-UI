import mysql.connector
from kivy.uix.screenmanager import Screen, SlideTransition
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.checkbox import CheckBox
from kivy.uix.scrollview import ScrollView
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.widget import Widget
from kivy.graphics import Color, RoundedRectangle
from kivy.uix.popup import Popup

class UploadExamPage(Screen):
    def __init__(self, **kwargs):
        super(UploadExamPage, self).__init__(**kwargs)
        self.selected_ids = []  # 用來記錄選中的考試 ID
        self.teacher_id = None  # 保存 teacher_id
        layout = BoxLayout(orientation='vertical', padding=20, spacing=20)

        # 頁面上方部分：包含返回按鈕
        top_layout = AnchorLayout(anchor_x='right', anchor_y='center', size_hint=(1, 0.2))
        back_button = Button(text="上一頁", font_size=24, size_hint=(0.3, 0.5), pos_hint={'right': 1}, font_name="BiauKai")
        back_button.bind(on_press=self.go_back)
        top_layout.add_widget(Widget())  # 用於將按鈕推到右邊
        top_layout.add_widget(back_button)
        layout.add_widget(top_layout)

        # 中間部分：顯示考試的表格
        middle_layout = BoxLayout(orientation='vertical', size_hint=(1, 0.6))

        # 表格背景設置
        self.table_layout = BoxLayout(orientation='vertical', padding=10, size_hint_y=None)
        self.table_layout.bind(minimum_height=self.table_layout.setter('height'))

        # 設置圓角矩形作為背景
        with self.table_layout.canvas.before:
            Color(1, 1, 1, 0.6)  # 白色半透明背景
            self.rect = RoundedRectangle(size=self.table_layout.size, pos=self.table_layout.pos, radius=[20, 20, 20, 20])
        self.table_layout.bind(pos=self.update_rect, size=self.update_rect)

        # 使用 ScrollView 來支援表格滾動
        self.scroll_view = ScrollView(size_hint=(1, None), size=(self.width, 400))
        self.scroll_view.add_widget(self.table_layout)

        middle_layout.add_widget(self.scroll_view)
        layout.add_widget(middle_layout)

        # 底部部分：新增考試按鈕
        self.bottom_layout = AnchorLayout(anchor_x='center', anchor_y='bottom', size_hint=(1, 0.2))
        self.add_exam_button = Button(text="新增考試", font_size=24, size_hint=(0.3, 0.5), font_name="BiauKai")
        self.add_exam_button.bind(on_press=self.add_exam)
        self.bottom_layout.add_widget(self.add_exam_button)
        layout.add_widget(self.bottom_layout)

        self.add_widget(layout)
        self.populate_table()  # 從資料庫中抓取資料並填充表格

    def set_teacher_id(self, teacher_id):
        """設置teacher_id並重新填充表格"""
        self.teacher_id = teacher_id
        self.populate_table()

    def update_rect(self, *args):
        # 更新背景矩形的位置和大小
        self.rect.pos = self.table_layout.pos
        self.rect.size = self.table_layout.size

    def go_back(self, instance):
        # 返回上一頁
        self.manager.transition = SlideTransition(direction='right')
        self.manager.current = 'teacher_menu'

    def add_exam(self, instance):
        # 傳遞 teacher_id 到 add_exam 頁面
        add_exam_page = self.manager.get_screen('addexam')
        add_exam_page.set_teacher_id(self.teacher_id)  # 傳遞 teacher_id
        self.manager.transition = SlideTransition(direction='left')
        self.manager.current = 'addexam'

    def on_enter(self):
        # 每次進入頁面時，刷新表格內容和選中的 ID
        self.populate_table()
        self.selected_ids = []
        self.bottom_layout.clear_widgets()
        self.bottom_layout.add_widget(self.add_exam_button)

    def populate_table(self):
        # 從資料庫抓取考試資料並填充到表格中
        self.table_layout.clear_widgets()
        self.selected_ids = []

        # 預定義的網站名稱與網址對應字典
        websites_dict = {
            "ChatGPT"  : "https://openai.com/blog/openai-codex",
            "Copilot"  : "https://github.com/features/copilot",
            "Tabnine"  : "https://www.tabnine.com",
            "Claude"   : "https://claude.ai/new",
            "Snyk Code": "https://snyk.io/product/snyk-code"
        }

        # 設置標題
        header_layout = GridLayout(cols=11, size_hint_y=None, height=50, spacing=5)
        """ headers = [
            {"text": "名稱", "size_hint_x": 0.16}, 
            {"text": "科目", "size_hint_x": 0.05}, 
            {"text": "開放時間", "size_hint_x": 0.104}, 
            {"text": "作答時間", "size_hint_x": 0.080}, 
            {"text": "考試類型", "size_hint_x": 0.088}, 
            {"text": "考試代碼", "size_hint_x": 0.088}, 
            {"text": "題目", "size_hint_x": 0.072}, 
            {"text": "評分標準", "size_hint_x": 0.104}, 
            {"text": "提示功能", "size_hint_x": 0.084}, 
            {"text": "禁用網站", "size_hint_x": 0.088}
        ]
        
        # 為每個標題設置不同的寬度
        for header in headers:
            header_label = Label(text=header["text"], font_size=18, font_name="BiauKai", color=(0, 0, 0, 1),
                                halign='center', valign='middle', size_hint=(None, None), 
                                width=header["width"], height=50, text_size=(header["width"], 50))
            header_layout.add_widget(header_label)

        self.table_layout.add_widget(header_layout) """

        headers = [
            {"text": "名稱", "width": 115}, 
            {"text": "科目", "width": 110}, 
            {"text": "開放時間", "width": 130}, 
            {"text": "作答時間", "width": 115}, 
            {"text": "考試類型", "width": 110}, 
            {"text": "考試代碼", "width": 110}, 
            {"text": "題目", "width": 90}, 
            {"text": "評分標準", "width": 130}, 
            {"text": "提示功能", "width": 105}, 
            {"text": "禁用網站", "width": 110}
        ]

        # 為每個標題設置不同的寬度
        for header in headers:
            header_label = Label(text=header["text"], font_size=18, font_name="BiauKai", color=(0, 0, 0, 1),
                                halign='right', valign='middle', size_hint=(None, None), 
                                width=header["width"], height=50, text_size=(header["width"], 50))
            header_layout.add_widget(header_label)

        self.table_layout.add_widget(header_layout)


        # 從資料庫中抓取考試資料並填入表格，根據 teacher_id 篩選
        try:
            conn = mysql.connector.connect(
                host="localhost",
                user="root",
                password="",
                database="learning sandbox"
            )
            cursor = conn.cursor()
            cursor.execute("""
                SELECT 
                    id, 
                    exam_name, 
                    subject, 
                    CONCAT(start_time, ' ~ ', end_time) AS open_time, 
                    duration, 
                    exam_type, 
                    exam_code, 
                    exam_file_name,
                    grading_file_name,
                    IF(hint_function=1, '開', '關') AS hint_function_text,
                    restricted_websites
                FROM exams
                WHERE teacher_id = %s
            """, (self.teacher_id,))
            exams = cursor.fetchall()
            cursor.close()
            conn.close()

            if not exams:
                # 如果沒有考試，顯示提示文字
                no_exam_label = Label(text="目前無任何考試", font_size=24, font_name="BiauKai", color=(1, 0, 0, 1))
                no_exam_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=50, padding=5)
                no_exam_layout.add_widget(no_exam_label)
                self.table_layout.add_widget(no_exam_layout)
            else:
                for exam in exams:
                    # 每筆考試資料顯示在表格中
                    exam_id = exam[0]
                    row_layout = GridLayout(cols=11, size_hint_y=None, height=80, spacing=5)  # 每一行的佈局
                    checkbox = CheckBox(size_hint_x=None, width=40)
                    checkbox.color = (0, 0, 0, 1)
                    checkbox.bind(active=lambda checkbox, value, exam_id=exam_id: self.on_checkbox_active(checkbox, value, exam_id))
                    row_layout.add_widget(checkbox)
                    
                    for item in exam[1:10]:
                        item_text = str(item) if item is not None else ""
                        label = Label(text=item_text, font_size=18, font_name="BiauKai", color=(0, 0, 0, 1),
                                    halign='center', valign='middle', text_size=(150, None))  # 設置 text_size 來控制換行
                        label.bind(size=lambda s, w: setattr(s, 'text_size', (w[0], None)))  # 自動調整 text_size
                        row_layout.add_widget(label)

                    # 顯示禁用的網站
                    restricted_websites = exam[10]
                    if restricted_websites:
                        # 將查詢出來的禁用網址進行比對，轉換成網站名稱
                        websites_list = restricted_websites.split(',')
                        websites_names = [name for name, url in websites_dict.items() if url in websites_list]
                        if not websites_names:
                            websites_names = ["未知網站"]  # 如果沒有匹配的，顯示“未知網站”
                        websites_text = '\n'.join(websites_names)  # 將網站名稱換行顯示
                    else:
                        websites_text = "無"
                    
                    websites_label = Label(text=websites_text, font_size=18, font_name="BiauKai", color=(0, 0, 0, 1),
                                        halign='center', valign='middle', text_size=(150, None))
                    websites_label.bind(size=lambda s, w: setattr(s, 'text_size', (w[0], None)))
                    row_layout.add_widget(websites_label)

                    self.table_layout.add_widget(row_layout)

        except mysql.connector.Error as err:
            # 顯示錯誤訊息
            error_label = Label(text=f"錯誤: {err}", font_size=24, font_name="BiauKai", color=(1, 0, 0, 1))
            self.table_layout.add_widget(error_label)

    def on_checkbox_active(self, checkbox, value, exam_id):
        # 處理複選框狀態變更，選擇或取消選擇考試
        if value:
            if exam_id not in self.selected_ids:
                self.selected_ids.append(exam_id)
        else:
            if exam_id in self.selected_ids:
                self.selected_ids.remove(exam_id)

        if self.selected_ids:
            # 如果有選中的考試，顯示刪除和修改按鈕
            self.bottom_layout.clear_widgets()
            button_layout = BoxLayout(orientation='horizontal', size_hint=(1, None), height=80, spacing=20)
            delete_button = Button(text="整筆刪除", font_size=24, size_hint=(0.5, 0.8), font_name="BiauKai")
            delete_button.bind(on_press=self.show_delete_confirmation_popup)
            modify_button = Button(text="修改內容", font_size=24, size_hint=(0.5, 0.8), font_name="BiauKai")
            modify_button.bind(on_press=self.modify_selected_item)
            button_layout.add_widget(delete_button)
            button_layout.add_widget(modify_button)
            self.bottom_layout.add_widget(button_layout)
        else:
            # 如果沒有選中的考試，顯示新增考試按鈕
            self.bottom_layout.clear_widgets()
            self.bottom_layout.add_widget(self.add_exam_button)

    def show_delete_confirmation_popup(self, instance):
        # 顯示確認刪除的彈出框
        popup_layout = BoxLayout(orientation='vertical', padding=20, spacing=10)
        confirmation_label = Label(text="您確定要刪除選中的考試嗎？", font_size=24, font_name="BiauKai")
        popup_layout.add_widget(confirmation_label)

        # 是與否的按鈕
        button_layout = BoxLayout(orientation='horizontal', size_hint=(1, None), height=50, spacing=20)
        yes_button = Button(text="是", font_size=24, font_name="BiauKai")
        yes_button.bind(on_press=lambda x: self.confirm_delete())
        no_button = Button(text="否", font_size=24, font_name="BiauKai")
        no_button.bind(on_press=lambda x: self.cancel_delete())
        button_layout.add_widget(yes_button)
        button_layout.add_widget(no_button)

        popup_layout.add_widget(button_layout)

        # 顯示刪除確認的彈出框
        self.delete_popup = Popup(
            title="確認刪除",
            title_font="BiauKai",
            content=popup_layout,
            size_hint=(0.8, 0.4)
        )
        self.delete_popup.open()

    def confirm_delete(self):
        # 確認刪除選中的考試
        self.delete_selected_items()
        self.delete_popup.dismiss()

    def cancel_delete(self):
        # 取消刪除
        self.delete_popup.dismiss()

    def delete_selected_items(self):
        # 刪除選中的考試
        try:
            conn = mysql.connector.connect(
                host="localhost",
                user="root",
                password="",
                database="learning sandbox"
            )
            cursor = conn.cursor()

            # 刪除選中的資料
            format_strings = ','.join(['%s'] * len(self.selected_ids))
            cursor.execute(f"DELETE FROM exams WHERE id IN ({format_strings})", tuple(self.selected_ids))
            conn.commit()

            # 重新編排 ID
            cursor.execute("SET @count = 0;")
            cursor.execute("UPDATE exams SET id = @count:= @count + 1;")
            cursor.execute("ALTER TABLE exams AUTO_INCREMENT = 1;")
            conn.commit()

            cursor.close()
            conn.close()
            self.populate_table()  # 刪除後刷新表格
            self.bottom_layout.clear_widgets()
            self.bottom_layout.add_widget(self.add_exam_button)

        except mysql.connector.Error as err:
            # 顯示錯誤彈出框
            self.show_error_popup("此考試已經開始或完成，無法刪除。\n如果您有任何問題，請與管理員聯繫以獲取幫助。")
    
    def modify_selected_item(self, instance):
        # 修改選中的考試
        if len(self.selected_ids) > 1:
            self.show_error_popup("不能同時修改兩筆資料")
        elif len(self.selected_ids) == 1:
            selected_id = self.selected_ids[0]
            self.manager.get_screen('modifyexam').load_exam_data(selected_id)
            self.manager.transition = SlideTransition(direction='left')
            self.manager.current = 'modifyexam'

    def show_error_popup(self, message):
        # 顯示錯誤信息的彈出框
        popup = Popup(
            title="錯誤", 
            title_font="BiauKai",  # 設置標題字體
            content=Label(text=message, font_size=24, font_name="BiauKai"), 
            size_hint=(0.6, 0.4)
        )
        popup.open()
