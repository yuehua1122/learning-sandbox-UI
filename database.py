import datetime
import eel
import mysql.connector
from collections import defaultdict

import requests

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

@eel.expose
def get_extra_points(exam_code, student_id):
    conn = connect_db()
    cursor = conn.cursor(dictionary=True)
    try:
        query = """
        SELECT end_time, extra_points
        FROM student_screen_image
        WHERE exam_code = %s AND student_id = %s
        """
        cursor.execute(query, (exam_code, student_id))
        results = cursor.fetchall()
        # 將 end_time 轉換為字串格式
        for row in results:
            row['end_time'] = str(row['end_time'])
        return results
    except Exception as e:
        print(f"Error in get_extra_points: {e}")
        return []
    finally:
        cursor.close()
        conn.close()

@eel.expose
def update_extra_points(exam_code, student_id, end_time, extra_points):
    conn = connect_db()
    cursor = conn.cursor()
    try:
        query = """
        UPDATE student_screen_image
        SET extra_points = %s
        WHERE exam_code = %s AND student_id = %s AND end_time = %s
        """
        cursor.execute(query, (extra_points, exam_code, student_id, end_time))
        conn.commit()
        return {'success': True}
    except Exception as e:
        print(f"Error in update_extra_points: {e}")
        return {'success': False, 'error': str(e)}
    finally:
        cursor.close()
        conn.close()

# 從 student_thinking 資料表中取得分數
@eel.expose
def get_scores(exam_code):
    conn = connect_db()
    cursor = conn.cursor()
    query = "SELECT score FROM student_thinking WHERE exam_code = %s"
    cursor.execute(query, (exam_code,))
    scores = [row[0] for row in cursor.fetchall()]
    cursor.close()
    conn.close()
    return scores

# 從 student_program_attainment 資料表中取得解題規格與花費時間的數據
@eel.expose
def get_design_chart_data(exam_code):
    conn = connect_db()
    cursor = conn.cursor()
    query = "SELECT sub_question, total_time FROM student_program_attainment WHERE exam_code = %s"
    cursor.execute(query, (exam_code,))
    data = cursor.fetchall()
    cursor.close()
    conn.close()

    # 取得所有的 sub_question，並去除重複項目
    sub_questions = sorted(set([row[0] for row in data]))

    # 初始化每個區間的數據列表
    lowRange = []
    midRange = []
    highRange = []

    for sub_question in sub_questions:
        # 取得該 sub_question 的所有 total_time
        times = [row[1] for row in data if row[0] == sub_question]

        # 处理 total_time 可能为 None 的情况，并转换为分钟数
        times_in_minutes = []
        for t in times:
            if t is not None:
                minutes = t.total_seconds() / 60  # 将 timedelta 转换为分钟数
                times_in_minutes.append(minutes)
            else:
                # 如果 total_time 为 None，可以选择忽略或设为 0
                times_in_minutes.append(0)

        # 計算每個區間的人數
        low = sum(1 for t in times_in_minutes if t <= 30)
        mid = sum(1 for t in times_in_minutes if 30 < t <= 60)
        high = sum(1 for t in times_in_minutes if t > 60)

        lowRange.append(low)
        midRange.append(mid)
        highRange.append(high)

    # 返回結果
    return {
        'labels': sub_questions,
        'lowRange': lowRange,
        'midRange': midRange,
        'highRange': highRange
    }

# 取得查詢網站次數圖表的數據
@eel.expose
def get_website_chart_data(exam_code):
    conn = connect_db()
    cursor = conn.cursor()

    # 從 student_screen_image 資料表中取得 student_id 和 website，根據 exam_code 篩選
    query = "SELECT student_id, website FROM student_screen_image WHERE exam_code = %s"
    cursor.execute(query, (exam_code,))
    data = cursor.fetchall()

    cursor.close()
    conn.close()

    # 計算每個學生的查詢次數
    student_query_counts = defaultdict(int)
    for student_id, website in data:
        if website:  # 確保 website 不為 None
            student_query_counts[student_id] += 1

    # 取得學生的分數
    conn = connect_db()
    cursor = conn.cursor()

    student_scores = {}
    for student_id in student_query_counts.keys():
        query = "SELECT score FROM student_thinking WHERE exam_code = %s AND student_id = %s"
        cursor.execute(query, (exam_code, student_id))
        result = cursor.fetchone()
        if result:
            score = result[0]
            student_scores[student_id] = score
        else:
            # 如果沒有找到分數，設定為 None 或其他預設值
            student_scores[student_id] = None

    cursor.close()
    conn.close()

    # 確定最大查詢次數，設置圖表的標籤
    max_query_count = max(student_query_counts.values(), default=0)
    interval_size = 5
    num_intervals = (max_query_count + interval_size - 1) // interval_size  # 天花板除法

    labels = [f'{(i+1)*interval_size}次以下' for i in range(num_intervals)]

    # 初始化數據陣列
    lowRange = [0] * num_intervals
    midRange = [0] * num_intervals
    highRange = [0] * num_intervals

    # 將學生的查詢次數和分數分類到對應的區間
    for student_id, query_count in student_query_counts.items():
        index = (query_count - 1) // interval_size  # 計算對應的區間索引

        if index >= num_intervals:
            index = num_intervals - 1  # 確保索引不超出範圍

        score = student_scores.get(student_id)
        if score is not None:
            if 0 <= score <= 59:
                lowRange[index] += 1
            elif 60 <= score <= 79:
                midRange[index] += 1
            elif 80 <= score <= 100:
                highRange[index] += 1
            else:
                # 處理意外的分數值
                pass
        else:
            # 處理沒有分數的學生
            pass

    # 返回結果
    return {
        'labels': labels,
        'lowRange': lowRange,
        'midRange': midRange,
        'highRange': highRange
    }

# 獲取完成度圖表的數據
@eel.expose
def get_completion_data(exam_code):
    conn = connect_db()
    cursor = conn.cursor()

    # 獲取所有的 sub_question，並去除重複項目
    query = "SELECT DISTINCT sub_question FROM student_program_attainment WHERE exam_code = %s"
    cursor.execute(query, (exam_code,))
    sub_questions = [row[0] for row in cursor.fetchall()]
    sub_questions.sort()  # 將題號進行排序

    # 定義時間點列表
    time_points = ['00:00:00', '00:10:00', '00:20:00', '00:30:00']
    time_titles = ['第0分鐘', '第10分鐘', '第20分鐘', '第30分鐘']

    # 初始化每個時間點的完成度數據結構
    completion_data = []
    for time_point in time_points:
        data = {
            'time': time_point,
            'low': [0] * len(sub_questions),
            'medium': [0] * len(sub_questions),
            'high': [0] * len(sub_questions)
        }
        completion_data.append(data)

    # 獲取所有學生的 student_id
    query = "SELECT DISTINCT student_id FROM student_program_attainment WHERE exam_code = %s"
    cursor.execute(query, (exam_code,))
    student_ids = [row[0] for row in cursor.fetchall()]

    # 檢查時間欄位是否存在
    cursor.execute("SHOW COLUMNS FROM student_program_attainment")
    columns = [row[0] for row in cursor.fetchall()]

    # 遍歷每個學生的數據
    for student_id in student_ids:
        # 動態構建可用的時間欄位列表
        available_time_points = [tp for tp in time_points if tp in columns]

        # 如果時間欄位存在，則查詢；否則，將完成度視為 0（低完成度）
        if available_time_points:
            placeholders = ', '.join([f"`{tp}`" for tp in available_time_points])
            query = f"""
                SELECT sub_question, {placeholders}
                FROM student_program_attainment
                WHERE exam_code = %s AND student_id = %s
            """
            cursor.execute(query, (exam_code, student_id))
            records = cursor.fetchall()

            for record in records:
                sub_question = record[0]
                completion_values = record[1:]  # 可用時間點的完成度值

                # 找到 sub_question 的索引
                idx = sub_questions.index(sub_question)

                # 初始化索引變量
                completion_idx = 0

                for i, time_point in enumerate(time_points):
                    if time_point in available_time_points:
                        # 時間點存在，使用實際的完成度值
                        completion = completion_values[completion_idx]
                        completion_idx += 1
                    else:
                        # 時間點不存在，視為低完成度
                        completion = 0

                    if completion is None:
                        # 如果沒有對應的時間點數據，視為低完成度
                        completion = 0

                    # 分類到對應的完成度區間
                    if 0 <= completion <= 40:
                        completion_data[i]['low'][idx] += 1
                    elif 41 <= completion <= 70:
                        completion_data[i]['medium'][idx] += 1
                    elif 71 <= completion <= 100:
                        completion_data[i]['high'][idx] += 1
                    else:
                        # 處理異常值或無效數據
                        pass
        else:
            # 所有時間欄位都不存在，將所有時間點的完成度設為低完成度
            for i in range(len(time_points)):
                for idx in range(len(sub_questions)):
                    completion_data[i]['low'][idx] += 1

    cursor.close()
    conn.close()

    # 返回結果
    return {
        'sub_questions': sub_questions,
        'completion_data': completion_data
    }

@eel.expose
def get_wordcloud_image(exam_code):
    conn = connect_db()
    cursor = conn.cursor()

    # 根據 exam_code 從 student_data 資料表中取得 wordcloud 欄位的資料
    query = "SELECT wordcloud FROM student_data WHERE exam_code = %s"
    cursor.execute(query, (exam_code,))
    result = cursor.fetchone()

    cursor.close()
    conn.close()

    if result and result[0]:
        # 將 BLOB 資料轉換為 Base64 字串
        import base64
        image_data = base64.b64encode(result[0]).decode('utf-8')
        return image_data
    else:
        # 如果沒有圖片，返回 None 或空字串
        return None

# 上傳並生成 Heatmap 的 Python 程式
@eel.expose
def generate_heatmap():
    try:
        filename = 'web/txt/test.txt'  # 您的矩陣文件
        upload_url = 'http://amp.pharm.mssm.edu/clustergrammer/matrix_upload/'

        # 上傳文件到 Clustergrammer
        with open(filename, 'rb') as f:
            r = requests.post(upload_url, files={'file': f})

        # 返回視覺化結果的 URL
        result_url = r.text
        return result_url  # 回傳結果 URL 給前端

    except Exception as e:
        print(f"Error: {e}")
        return None  # 回傳 None 表示發生錯誤

@eel.expose
def get_student_hints(exam_code, student_id):
    db = connect_db()
    cursor = db.cursor(dictionary=True)
    query = """
        SELECT sub_question, code, request
        FROM student_hints
        WHERE exam_code = %s AND student_id = %s
    """
    cursor.execute(query, (exam_code, student_id))
    results = cursor.fetchall()
    cursor.close()
    db.close()
    return results

@eel.expose
def update_hint_extra_point(exam_code, student_id, sub_question, extra_point):
    try:
        db = connect_db()
        cursor = db.cursor()
        query = """
            UPDATE student_hints
            SET extra_point = %s
            WHERE exam_code = %s AND student_id = %s AND sub_question = %s
        """
        cursor.execute(query, (extra_point, exam_code, student_id, sub_question))
        db.commit()
        cursor.close()
        db.close()
        return {'success': True}
    except Exception as e:
        print(f"Error updating extra_point: {e}")
        return {'success': False, 'error': str(e)}
