import re
from kivy.clock import Clock
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.core.text import LabelBase
from kivy.uix.anchorlayout import AnchorLayout
import webbrowser
import os
import subprocess
import time
import datetime
import mysql.connector

# 註冊粉圓體字體
LabelBase.register(name="BiauKai", fn_regular="font/粉圓體.ttf")

class RecordingInProgressPage(Screen):
    def __init__(self, file_path, student_id, exam_code, **kwargs):
        super(RecordingInProgressPage, self).__init__(**kwargs)
        self.file_path = file_path  # 保存文件路徑
        self.student_id = student_id  # 保存學生ID
        self.exam_code = exam_code  # 保存考試代碼
        self.ten_minute_warning_shown = False  # 標誌是否已經顯示過剩餘10分鐘的提醒
        self.is_countdown_running = False  # 防止重複生成倒計時視窗
        self.exam_check_event = None  # 保存定時事件

        # 初始化計時器和檢查時間
        self.end_time = None
        self.duration = None
        self.start_time = datetime.datetime.now()

        # 獲取考試的結束時間和持續時間
        self.get_exam_info()

        layout = BoxLayout(orientation='vertical', padding=50, spacing=30)

        # 顯示 "螢幕錄製中，祝考試順利" 的標籤，使用粉圓體字體
        label = Label(text="螢幕錄製中，祝考試順利", font_size=48, font_name="BiauKai")
        layout.add_widget(label)

        # 中心對齊的題目下載部分，位於標題下方
        download_layout = AnchorLayout(size_hint_y=None, height=40, pos_hint={'center_x': 0.4})
        download_content = BoxLayout(orientation='horizontal', spacing=10, size_hint_x=None)
        download_label = Label(text="題目下載 :", font_size=24, font_name="BiauKai", size_hint_x=None, width=130)
        download_content.add_widget(download_label)

        # 顯示文件名稱並設置按鈕可供點擊下載
        download_link = Button(text="說明書.pdf", font_size=24, font_name="BiauKai", size_hint_x=None, width=220, background_color=(0, 0, 0, 0), color=(1, 0, 0, 1), underline=True)
        download_link.bind(on_press=self.download_file)
        download_content.add_widget(download_link)

        download_layout.add_widget(download_content)
        layout.add_widget(download_layout)
        
        # 在題目下載下方添加提示按鈕
        tip_button_layout = AnchorLayout(anchor_x='center', anchor_y='center')
        tip_button = Button(text="提示", font_size=24, size_hint=(0.1, 0.3), font_name="BiauKai")
        tip_button_layout.add_widget(tip_button)
        layout.add_widget(tip_button_layout)

        # 底部結束錄製按鈕
        bottom_layout = AnchorLayout(anchor_x='center', anchor_y='bottom')
        end_btn = Button(text="結束錄製", font_size=24, size_hint=(0.6, 0.4), font_name="BiauKai")
        end_btn.bind(on_press=self.show_confirmation)  # 綁定結束錄製的確認框
        bottom_layout.add_widget(end_btn)

        layout.add_widget(bottom_layout)

        self.add_widget(layout)

        # 每秒檢查一次考試是否應該結束
        self.exam_check_event = Clock.schedule_interval(self.check_exam_time, 1)

    def get_exam_info(self):
        # 從資料庫中獲取考試的結束時間和持續時間
        try:
            conn = mysql.connector.connect(
                host="localhost",            # 資料庫主機地址
                user="root",                 # 資料庫用戶名
                password="",                 # 資料庫密碼
                database="learning sandbox"  # 資料庫名稱
            )
            cursor = conn.cursor()

            # 查詢考試結束時間和持續時間
            cursor.execute("""
                SELECT end_time, duration FROM exams WHERE exam_code = %s
            """, (self.exam_code,))
            result = cursor.fetchone()

            if result:
                self.end_time = result[0]  # 資料庫中的 end_time
                # 使用正則表達式去除 'min' 或 '分鐘'，獲取持續時間
                self.duration = int(re.sub(r'(min|分鐘)', '', result[1])) 

            conn.close()

        except mysql.connector.Error as err:
            print(f"資料庫錯誤: {err}")

    def check_exam_time(self, dt):
        # 檢查考試是否應該結束
        current_time = datetime.datetime.now()

        # 計算考試開始時間加上持續時間的截止時間
        duration_end_time = self.start_time + datetime.timedelta(minutes=self.duration)

        # 當剩餘10分鐘時顯示警告
        ten_minutes_before_end = min(self.end_time, duration_end_time) - datetime.timedelta(minutes=10)
        if current_time >= ten_minutes_before_end and current_time < min(self.end_time, duration_end_time) and not self.ten_minute_warning_shown:
            self.show_notification("考試剩餘10分鐘")  # 顯示警告通知
            self.ten_minute_warning_shown = True  # 標誌已顯示過

        # 如果時間已過，顯示倒計時提醒，然後強制結束錄製
        if (current_time >= self.end_time or current_time >= duration_end_time) and not self.is_countdown_running:
            self.show_countdown_and_end()

    def show_countdown_and_end(self):
        # 防止重複生成倒計時視窗
        self.is_countdown_running = True

        # 顯示十秒倒計時彈出框
        self.countdown_seconds = 10
        self.countdown_label = Label(text=f"剩餘 {self.countdown_seconds} 秒", font_size=24, font_name="BiauKai")
        self.countdown_popup = Popup(
            title="強制結束倒計時",
            title_font="BiauKai",
            content=self.countdown_label,  # 直接更新Label的文本內容
            size_hint=(0.5, 0.3),
            auto_dismiss=False  # 禁止手動關閉
        )
        self.countdown_popup.open()
        self.countdown_popup._window.raise_window()  # 置頂顯示視窗

        # 每秒更新倒計時
        self.countdown_event = Clock.schedule_interval(self.update_countdown, 1)

    def update_countdown(self, dt):
        # 更新倒計時
        self.countdown_seconds -= 1
        if self.countdown_seconds <= 0:
            self.countdown_popup.dismiss()  # 倒計時結束後關閉彈出框
            Clock.unschedule(self.countdown_event)  # 停止倒計時
            self.end_recording_forced()  # 強制結束錄製
            return False  # 停止倒計時調度
        else:
            self.countdown_label.text = f"剩餘 {self.countdown_seconds} 秒"  # 只更新內容
            return True  # 繼續倒計時

    def show_notification(self, message):
        # 顯示提醒通知並將窗口置頂
        popup = Popup(
            title="提醒",
            title_font="BiauKai",
            content=Label(text=message, font_size=24, font_name="BiauKai"),
            size_hint=(0.5, 0.3),
        )
        popup.open()
        popup._window.raise_window()  # 置頂顯示視窗

    def show_confirmation(self, instance):
        # 顯示確認結束錄製的彈出框
        content = BoxLayout(orientation='vertical', padding=20, spacing=20)
        msg = Label(text="確定要結束錄製嗎?", font_size=24, font_name="BiauKai")
        content.add_widget(msg)

        # 取消和確認按鈕
        buttons = BoxLayout(spacing=20)
        cancel_btn = Button(text="取消", font_size=18, font_name="BiauKai")
        confirm_btn = Button(text="確認", font_size=18, font_name="BiauKai")

        buttons.add_widget(cancel_btn)
        buttons.add_widget(confirm_btn)

        content.add_widget(buttons)

        # 彈出框設置
        popup = Popup(title='', content=content, size_hint=(0.3, 0.3))
        cancel_btn.bind(on_press=popup.dismiss)  # 取消關閉彈出框
        confirm_btn.bind(on_press=lambda x: self.end_recording(popup))  # 確認結束錄製

        popup.open()

    def download_file(self, instance):
        # 打開下載的PDF文件
        if os.path.exists(self.file_path):
            webbrowser.open(os.path.abspath(self.file_path))

    def end_recording(self, popup):
        # 正常結束考試錄製
        popup.dismiss()  # 關閉彈出框
        self.end_recording_forced()  # 強制結束錄製

    def end_recording_forced(self):
        # 取消定時檢查，防止重複結束
        if self.exam_check_event:
            Clock.unschedule(self.exam_check_event)
        
        # 取消倒計時事件，防止重複執行強制結束
        if hasattr(self, 'countdown_event'):
            Clock.unschedule(self.countdown_event)

        # 更新資料庫中的結束時間，並強制結束錄製
        end_time = time.strftime('%Y-%m-%d %H:%M:%S')
        try:
            conn = mysql.connector.connect(
                host="localhost",            # 資料庫主機地址
                user="root",                 # 資料庫用戶名
                password="",                 # 資料庫密碼
                database="learning sandbox"  # 資料庫名稱
            )
            cursor = conn.cursor()

            # 更新學生考試的結束時間
            cursor.execute("""
                UPDATE student_exams
                SET end_time = %s
                WHERE student_id = %s AND exam_code = %s
            """, (end_time, self.student_id, self.exam_code))

            conn.commit()

        except mysql.connector.Error as err:
            print(f"資料庫錯誤: {err}")
        finally:
            if conn:
                conn.close()

        # 切換到錄製結束頁面
        self.manager.current = 'recording_end'

        # 執行 analyze.py 檔案
        try:
            subprocess.run(['python', 'function/analyze.py'], check=True)
        except subprocess.CalledProcessError as e:
            print(f"執行 analyze.py 時發生錯誤: {e}")