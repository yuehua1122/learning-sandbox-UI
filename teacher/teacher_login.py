import mysql.connector
from kivy.uix.screenmanager import Screen, SlideTransition
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.core.text import LabelBase
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.popup import Popup

# 註冊粉圓體字體
LabelBase.register(name="BiauKai", fn_regular="font/粉圓體.ttf")

class CenteredTextInput(TextInput):
    def __init__(self, **kwargs):
        super(CenteredTextInput, self).__init__(**kwargs)
        self.halign = 'center'  # 設置水平居中
        self.valign = 'middle'  # 設置垂直居中
        self.bind(size=self.update_text_size)

    def update_text_size(self, *args):
        self.text_size = (self.width, None)  # 更新文本框大小以保持居中

class TeacherLoginPage(Screen):
    def __init__(self, **kwargs):
        super(TeacherLoginPage, self).__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=50, spacing=10)  # 減少總體間距
        
        # 使用粉圓體顯示中文文字
        label = Label(text="使用者身分: 老師", font_size=48, font_name="BiauKai", size_hint_y=None, height=60)  # 減少標題高度
        layout.add_widget(label)
        
        teacher_id_label = Label(text="請輸入教師編號(帳號)：", font_size=28, size_hint=(1.0, 0.5), font_name="BiauKai")
        layout.add_widget(teacher_id_label)
        
        self.teacher_id_input = CenteredTextInput(font_size=32, size_hint=(0.5, 0.3), pos_hint={'center_x': 0.5}, font_name="BiauKai")
        layout.add_widget(self.teacher_id_input)
        
        password_label = Label(text="請輸入密碼：", font_size=28, size_hint=(1.0, 0.5), font_name="BiauKai")
        layout.add_widget(password_label)

        self.password_input = CenteredTextInput(font_size=32, size_hint=(0.5, 0.3), pos_hint={'center_x': 0.5}, font_name="BiauKai", password=True, password_mask="*")
        layout.add_widget(self.password_input)

        
        # 使用 AnchorLayout 將按鈕固定在底部
        bottom_layout = AnchorLayout(anchor_x='center', anchor_y='bottom')
        button_layout = BoxLayout(orientation='horizontal', size_hint=(1, None), height=80, spacing=20)
        
        # 上一頁按鈕
        back_btn = Button(text="上一頁", font_size=24, size_hint=(0.5, 0.8), font_name="BiauKai")
        back_btn.bind(on_press=self.go_to_home)  
        button_layout.add_widget(back_btn)

        # 確認按鈕
        start_btn = Button(text="確認", font_size=24, size_hint=(0.5, 0.8), font_name="BiauKai")
        start_btn.bind(on_press=self.check_login)
        button_layout.add_widget(start_btn)
        
        bottom_layout.add_widget(button_layout)  # 將按鈕布局添加到底部布局中
        layout.add_widget(bottom_layout)  # 將底部布局添加到主布局中
        
        self.add_widget(layout)

    def go_to_home(self, instance):
        self.clear_inputs()  # 清空輸入框
        # 設置向右滑動過渡動畫
        self.manager.transition = SlideTransition(direction='right')
        self.manager.current = 'home'

    def check_login(self, instance):
        # 從輸入框獲取用戶輸入的帳號和密碼
        teacher_id = self.teacher_id_input.text
        password = self.password_input.text

        # 連接到MySQL資料庫並驗證登錄資訊
        try:
            conn = mysql.connector.connect(
                host="localhost",  # 資料庫主機地址
                user="root",       # 資料庫用戶名
                password="",  # 資料庫密碼
                database="learning sandbox"  # 資料庫名稱
            )
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM teachers WHERE teacher_id=%s AND password=%s", (teacher_id, password))
            result = cursor.fetchone()
            
            if result:
                # 登錄成功，跳轉到教師菜單頁面
                self.clear_inputs()  # 清空輸入框
                self.go_to_teacher_menu(teacher_id)
            else:
                # 登錄失敗，顯示錯誤提示
                self.show_error_popup("帳號或密碼錯誤，請重新輸入。")

            cursor.close()
            conn.close()
        except mysql.connector.Error as err:
            self.show_error_popup(f"資料庫錯誤: {err}")

    def show_error_popup(self, message):
        # 顯示錯誤提示框
        content = BoxLayout(orientation='vertical', padding=5)
        label = Label(text=message, font_size=24, font_name="BiauKai")
        content.add_widget(label)
        
        popup = Popup(title="", content=content, size_hint=(0.5, 0.2))
        popup.open()

    def go_to_teacher_menu(self, teacher_id):
        # 設置向左滑動過渡動畫
        self.manager.transition = SlideTransition(direction='left')
        # 傳遞 teacher_id 給下一個頁面
        teacher_menu_page = self.manager.get_screen('teacher_menu')
        teacher_menu_page.set_teacher_id(teacher_id)  # 設定 teacher_id
        self.manager.current = 'teacher_menu'

    def clear_inputs(self):
        # 清空輸入框
        self.teacher_id_input.text = ''
        self.password_input.text = ''
