from kivy.uix.screenmanager import Screen, SlideTransition
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.core.text import LabelBase
from kivy.uix.anchorlayout import AnchorLayout

# 註冊粉圓體字體
LabelBase.register(name="BiauKai", fn_regular="font/粉圓體.ttf")

class RecordingEndPage(Screen):
    def __init__(self, **kwargs):
        super(RecordingEndPage, self).__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=50, spacing=20)
        
        # 使用粉圓體顯示中文文字
        label = Label(text="錄製結束，考試結束", font_size=48, font_name="BiauKai")
        layout.add_widget(label)
        
        # 使用 AnchorLayout 來固定回到首頁的按鈕在底部
        bottom_layout = AnchorLayout(anchor_x='center', anchor_y='bottom')
        home_button = Button(text="回到首頁", font_size=24, size_hint=(0.5, 0.2), font_name="BiauKai")
        home_button.bind(on_press=self.go_to_home)  # 假設首頁的名稱為 'home'
        bottom_layout.add_widget(home_button)
        
        layout.add_widget(bottom_layout)
        
        self.add_widget(layout)
        
    def go_to_home(self, instance):
        # 設置向右滑動過渡動畫
        self.manager.transition = SlideTransition(direction='right')
        self.manager.current = 'home'
