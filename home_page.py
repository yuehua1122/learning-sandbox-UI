from kivy.uix.screenmanager import Screen, SlideTransition
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.core.text import LabelBase

# 註冊粉圓體字體
LabelBase.register(name="BiauKai", fn_regular="font/粉圓體.ttf")

class HomePage(Screen):
    def __init__(self, **kwargs):
        super(HomePage, self).__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=50, spacing=20)
        
        # 使用粉圓體顯示中文文字
        label = Label(text="歡迎來到AI抓碼\n\n請選擇身分", font_size=50, font_name="BiauKai", halign="center")
        layout.add_widget(label)
        
        student_btn = Button(text="學生", font_size=24, size_hint=(0.6, 0.2), pos_hint={'center_x': 0.5}, font_name="BiauKai")
        student_btn.bind(on_press=self.go_student)
        layout.add_widget(student_btn)

        teacher_btn = Button(text="老師", font_size=24, size_hint=(0.6, 0.2), pos_hint={'center_x': 0.5}, font_name="BiauKai")
        teacher_btn.bind(on_press=self.go_teacher)
        layout.add_widget(teacher_btn)  
        
        self.add_widget(layout)
        
    def go_student(self, instance):
        # 設置向右滑動過渡動畫
        self.manager.transition = SlideTransition(direction='left')
        self.manager.current = 'student'
        
    def go_teacher(self, instance):
        # 設置向右滑動過渡動畫
        self.manager.transition = SlideTransition(direction='left')
        self.manager.current = 'teacher'
