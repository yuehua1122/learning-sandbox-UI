import eel
import mysql.connector

# 初始化 Eel 並設定 web 資料夾為前端目錄
eel.init('web')

# 與資料庫建立連線
def connect_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="learning sandbox"
    )

# 定義回到首頁的 Eel 函數
@eel.expose
def go_to_home():
    eel.goToHome()

# 檢查考試代碼是否存在
@eel.expose
def check_exam_code(exam_code):
    conn = connect_db()
    cursor = conn.cursor()
    query = "SELECT * FROM exams WHERE exam_code = %s"
    cursor.execute(query, (exam_code,))
    result = cursor.fetchone()
    cursor.close()
    conn.close()

    if result:
        return 'valid'
    else:
        return 'invalid'

# 檢查學生是否參加該考試
@eel.expose
def check_student_exam(student_id, exam_code):
    conn = connect_db()
    cursor = conn.cursor()
    query = "SELECT * FROM student_exams WHERE student_id = %s AND exam_code = %s"
    cursor.execute(query, (student_id, exam_code))
    result = cursor.fetchone()
    cursor.close()
    conn.close()

    if result:
        return 'valid'
    else:
        return 'invalid'

@eel.expose
def get_exam_time_and_buttons(exam_code , student_id):
    conn = connect_db()
    cursor = conn.cursor()

    # 查詢 exams 表格中的 start_time 和 end_time
    exam_query = "SELECT start_time, end_time FROM exams WHERE exam_code = %s"
    cursor.execute(exam_query, (exam_code,))
    exam_result = cursor.fetchone()
    exam_start_time, exam_end_time = exam_result if exam_result else (None, None)

    # 查詢 student_exams 表格中的 start_time 和 end_time
    student_query = "SELECT start_time, end_time FROM student_exams WHERE exam_code = %s AND student_id = %s"
    cursor.execute(student_query, (exam_code, student_id))
    student_result = cursor.fetchone()
    student_start_time, student_end_time = student_result if student_result else (None, None)

    # 查詢 student_screen_image 表格中的 end_time 和 content
    screen_query = """
    SELECT end_time, content FROM student_screen_image 
    WHERE exam_code = %s AND student_id = %s AND content IS NOT NULL AND content != ''
    """
    cursor.execute(screen_query, (exam_code, student_id))
    screen_data = cursor.fetchall()

    cursor.close()
    conn.close()

    # 構造返回給前端的數據
    if exam_start_time and exam_end_time and student_start_time and student_end_time:
        return {
            'exam_start_time': str(exam_start_time),  # 確保轉換為字符串
            'exam_end_time': str(exam_end_time),
            'student_start_time': str(student_start_time),
            'student_end_time': str(student_end_time),
            'screen_data': [{'end_time': str(row[0]), 'content': row[1]} for row in screen_data]
        }
    else:
        return {'error': '無法獲取考試或學生數據'}

@eel.expose
def get_student_performance(exam_code, student_id, timestamp):
    conn = connect_db()
    cursor = conn.cursor()

    # 查詢 student_program_attainment 中對應的 sub-question 和成績
    query = """
    SELECT sub_question, {timestamp_column} 
    FROM student_program_attainment
    WHERE exam_code = %s AND student_id = %s
    """
    # 將 timestamp_column 動態替換成實際的時間欄位名稱
    query = query.replace("{timestamp_column}", timestamp)
    
    cursor.execute(query, (exam_code, student_id))
    results = cursor.fetchall()

    cursor.close()
    conn.close()

    # 返回成績數據給前端
    performance_data = [{'sub_question': row[0], 'score': row[1]} for row in results]
    return performance_data
