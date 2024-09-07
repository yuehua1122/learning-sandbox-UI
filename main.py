from kivy.app import App
from kivy.uix.screenmanager import ScreenManager
from home_page import HomePage
from student.student_login import StudentLoginPage
from student.recording_end_page import RecordingEndPage
from teacher.add_exam_page import AddExamPage
from teacher.modify_exam_page import ModifyExamPage
from teacher.teacher_login import TeacherLoginPage
from teacher.teacher_menu import TeacherMenuPage
from teacher.upload_exam_page import UploadExamPage
from kivy.core.window import Window
from kivy.uix.image import Image
from kivy.uix.floatlayout import FloatLayout

class MyApp(App):
    def build(self):
        layout = FloatLayout()      
        bg_image = Image(source='img/background.jpg', allow_stretch=True, keep_ratio=False, size_hint=(1, 1))
        layout.add_widget(bg_image)        
        self.title = "學習沙盒"
        Window.size = (1250, 750)        
        sm = ScreenManager()
        sm.add_widget(HomePage(name='home'))
        sm.add_widget(StudentLoginPage(name='student'))
        sm.add_widget(RecordingEndPage(name='recording_end'))
        sm.add_widget(TeacherLoginPage(name='teacher'))
        sm.add_widget(TeacherMenuPage(name='teacher_menu'))
        sm.add_widget(UploadExamPage(name='upload'))
        sm.add_widget(AddExamPage(name='addexam'))
        sm.add_widget(ModifyExamPage(name='modifyexam'))
        layout.add_widget(sm)  
        return layout
    
if __name__ == '__main__':
    MyApp().run()