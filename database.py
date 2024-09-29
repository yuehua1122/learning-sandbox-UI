import datetime
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

# 取得考試時間及相關按鈕資訊
@eel.expose
def get_exam_time_and_buttons(exam_code , student_id, is_for_website=False):
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

    # 根據是否查詢網站內容，修改 SQL 查詢邏輯
    if is_for_website:
        screen_query = """
        SELECT end_time, website FROM student_screen_image 
        WHERE exam_code = %s AND student_id = %s AND content = ''
        """
    else:
        screen_query = """
        SELECT end_time, content FROM student_screen_image 
        WHERE exam_code = %s AND student_id = %s AND content != '獲取到的內容為空' AND content != ''
        """
    cursor.execute(screen_query, (exam_code, student_id))
    screen_data = cursor.fetchall()

    cursor.close()
    conn.close()

    # 構造返回給前端的數據
    if exam_start_time and exam_end_time and student_start_time and student_end_time:
        if is_for_website:
            return {
                'exam_start_time': str(exam_start_time),
                'exam_end_time': str(exam_end_time),
                'student_start_time': str(student_start_time),
                'student_end_time': str(student_end_time),
                'screen_data': [{'end_time': str(row[0]), 'website': row[1]} for row in screen_data]
            }
        else:
            return {
                'exam_start_time': str(exam_start_time),
                'exam_end_time': str(exam_end_time),
                'student_start_time': str(student_start_time),
                'student_end_time': str(student_end_time),
                'screen_data': [{'end_time': str(row[0]), 'content': row[1]} for row in screen_data]
            }
    else:
        return {'error': '無法獲取考試或學生數據'}

# 取得學生的成績數據
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

# 取得考試數據
@eel.expose
def get_exam_data(exam_code, student_id):
    conn = connect_db()
    cursor = conn.cursor()

    # 查詢特定的 exam_code 和 student_id 的數據
    query = '''
        SELECT sub_question, total_time
        FROM student_program_attainment
        WHERE exam_code = %s AND student_id = %s
    '''
    cursor.execute(query, (exam_code, student_id))

    data = cursor.fetchall()
    conn.close()

    # 將數據轉換為字典列表，並將 total_time 轉換為字串
    result = []
    for row in data:
        sub_question = row[0]
        total_time = row[1]

        # 檢查 total_time 是否為 datetime.time 對象
        if isinstance(total_time, datetime.time):
            # 將 datetime.time 對象轉換為字串
            total_time_str = total_time.strftime('%H:%M:%S')
        else:
            total_time_str = str(total_time)  # 如果不是 datetime.time 對象，直接轉換為字串

        result.append({'sub_question': sub_question, 'total_time': total_time_str})

    return result

# **添加的 get_attainment_data 函數**
@eel.expose
def get_attainment_data(exam_code, student_id):
    conn = connect_db()
    cursor = conn.cursor(dictionary=True)

    try:
        # 取得資料表的所有欄位名稱
        cursor.execute("SHOW COLUMNS FROM student_program_attainment")
        columns_info = cursor.fetchall()
        column_names = [col['Field'] for col in columns_info]

        # 排除非時間欄位，包括 'id'
        exclude_columns = ('id', 'exam_code', 'student_id', 'sub_question', 'total_time')
        time_columns = [col for col in column_names if col not in exclude_columns]

        # 為每個時間欄位名稱添加反引號
        time_columns_escaped = [f'`{col}`' for col in time_columns]

        # 構建 SQL 查詢
        sql = f"""
            SELECT sub_question, {', '.join(time_columns_escaped)}
            FROM student_program_attainment
            WHERE exam_code = %s AND student_id = %s
        """

        # 執行查詢
        cursor.execute(sql, (exam_code, student_id))
        rows = cursor.fetchall()

        # 構建結果列表
        attainment_data = []
        for row in rows:
            data_dict = {'sub_question': row['sub_question']}
            for col_name in time_columns:
                # 確保從 row 中取得正確的值
                data_dict[col_name] = row.get(col_name, 0)
            attainment_data.append(data_dict)

        return attainment_data
    except Exception as e:
        print(f"Error in get_attainment_data: {e}")
        return None
    finally:
        cursor.close()
        conn.close()

@eel.expose
def get_design_specifications(exam_code, student_id):
    conn = connect_db()
    cursor = conn.cursor(dictionary=True)

    try:
        # 查詢 student_thinking 表格
        query = """
        SELECT score, thinking_process, violation_count
        FROM student_thinking
        WHERE exam_code = %s AND student_id = %s
        """
        cursor.execute(query, (exam_code, student_id))
        result = cursor.fetchone()

        if result:
            return {
                'score': result['score'],
                'thinking_process': result['thinking_process'],
                'violation_count': result['violation_count']
            }
        else:
            return {'error': '沒有找到相關的設計規格資料'}
    except Exception as e:
        print(f"Error in get_design_specifications: {e}")
        return {'error': '資料庫查詢錯誤'}
    finally:
        cursor.close()
        conn.close()
