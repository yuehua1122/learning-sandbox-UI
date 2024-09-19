import openai
import csv
import os
import time
import mysql.connector
from mysql.connector import Error
import re
from datetime import datetime, timedelta

# 設定 OpenAI API 金鑰
openai.api_key = 'your api key'

def read_file(file_path):
    """
    讀取指定文件並返回其內容
    :param file_path: 文件路徑
    :return: 文件內容
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"文件未找到: {file_path}")
    
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()

def visual_information_analysis(behavior_trace_file, problem_description, grading_criteria):
    """
    每個小題在不同時間點的達成度分析
    """
    prompt = f"""Please analyze the following trajectory file:\n{behavior_trace_file}\n\n
                In comparison to the question:\n{problem_description}\n\n
                And the grading criteria:\n{grading_criteria}\n\n
                Complete the following behavior analysis tasks:
                Generate a CSV-formatted data with with the following columns:
                - sub-question
                - 00:00:30
                - 00:01:00
                - 00:01:30
                - 00:02:00
                - 00:02:30
                - 00:03:00
                - 00:03:30
                ...

                The rows should contain student information and the percentages as progress over time for the given exam. For example, each row has data in percentages representing the progress made by a student in intervals of 30 seconds. 

                Only output the CSV-formatted data, do not output any other text!
                """

    for _ in range(3):  # 重試次數0
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are a programming assistant."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1500
            )
            return response.choices[0].message['content'].strip()
        except openai.OpenAIError as e:
            print(f"API Error: {e}")
            time.sleep(5)  # 等待一段時間後重試
    raise Exception("Failed to get response after 3 attempts")

# 解析 GPT API 的回應並保存成 CSV 文件
def save_csvfile(visual_information, csv_filename):
    # 將 visual_information 按行分割成列表
    lines = visual_information.splitlines()
    
    # 刪除第一行
    if len(lines) > 1:
        lines = lines[1:-1]

    # 將處理後的內容重新組合成字符串
    visual_information = "\n".join(lines)

    # 將輸出轉換為 CSV 文件
    csv_data = []
    for line in visual_information.split('\n'):
        csv_data.append(line.split(','))

     # 保存到 CSV 文件
    with open(csv_filename, mode='w', newline='', encoding='utf-8-sig') as file:
        writer = csv.writer(file)
        writer.writerows(csv_data)

# 讀取文件並生成表格 A 和 B
def generate_visual_analysis_and_save(log_file, problem_file, grading_file):
    try:
        log檔 = read_file(log_file)
        題目檔案 = read_file(problem_file)
        評分標準及各題配分檔案 = read_file(grading_file)
    except FileNotFoundError as e:
        print(e)
        exit(1)

    # 進行視覺化分析並保存表格A
    visual_information = visual_information_analysis(log檔, 題目檔案, 評分標準及各題配分檔案)
    save_csvfile(visual_information, '表格A.csv')
    print("表格A已成功保存")

    # 生成表格B
    generate_table_B(log檔)

# 生成表格 B 的方法
def generate_table_B(log檔):
    # 定義正則表達式來匹配時間和條件，新增 "結束錄製 - 檔案:" 到 window_pattern
    window_pattern = re.compile(r'(視窗:|定時快照 - 檔案:|執行 - 檔案:|結束錄製 - 檔案:)')
    time_pattern = re.compile(r'(\d{2}:\d{2}:\d{2})')

    # 保存表格B的資料
    table_b_data = []

    # 暫存上一個結束時間，以確保時間接續
    previous_end_time = None

    # 函數：將時間字串轉換為 datetime 物件
    def time_to_datetime(time_str):
        return datetime.strptime(time_str, '%H:%M:%S')

    # 函數：將 datetime 物件轉換為時間字串
    def datetime_to_time_str(time_obj):
        return time_obj.strftime('%H:%M:%S')

    # 處理每一行，抓取時間與內容，生成表格B
    lines = log檔.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i]
        time_match = time_pattern.search(line)
        if time_match and window_pattern.search(line):
            # 提取時間和文字
            time_str = time_match.group(1)
            result = window_pattern.split(line)[-1].strip()
            result = result.replace(']', '').replace('●', '').split('-')[0].strip()

            # 如果是第一行，初始化 previous_end_time
            if previous_end_time is None:
                start_time = time_str
                previous_end_time = time_str
            else:
                # 確保時間接續，將上一次的結束時間作為這次的開始時間
                start_time = datetime_to_time_str(time_to_datetime(previous_end_time) + timedelta(seconds=1))

            # 當前的時間是結束時間
            end_time = time_str

            # 如果 end_time 小於 start_time，將 start_time 設為 end_time
            if time_to_datetime(end_time) < time_to_datetime(start_time):
                start_time = end_time

            # 初始化 content
            content = ""

            # 如果 window 包含 "定時快照 - 檔案:"、"執行 - 檔案:" 或 "結束錄製 - 檔案:"，則收集下一行到 "End of Code Snapshot"
            if "定時快照 - 檔案:" in line or "執行 - 檔案:" in line or "結束錄製 - 檔案:" in line:
                content_lines = []
                i += 1  # 跳到下一行
                while i < len(lines) and "--- End of Code Snapshot ---" not in lines[i]:
                    content_lines.append(lines[i].strip())
                    i += 1  # 繼續讀取到 End of Code Snapshot
                content = "\n".join(content_lines)  # 將多行合併為一個字串

            # 將當前時間區間和 window 記錄下來，並加上 content
            table_b_data.append([start_time, end_time, result, content])

            # 更新 previous_end_time
            previous_end_time = end_time
        i += 1  # 處理下一行

    # 將結果寫入表格B
    csv_filename_b = 'table_B.csv'
    with open(csv_filename_b, mode='w', newline='', encoding='utf-8-sig') as file_b:
        writer_b = csv.writer(file_b)
        writer_b.writerow(['start_time', 'end_time', 'window', 'content'])  # 標題包含 content
        writer_b.writerows(table_b_data)

    print(f'表格B已成功寫入 {csv_filename_b}')

# 連結資料庫並插入表格A和表格B
def insert_into_db_A(file_path, insert_script, db_table):
    try:
        connection = mysql.connector.connect(
                host="localhost",
                user="root",
                password="",
                database="learning sandbox"
        )
 
        if connection.is_connected():
            db_info = connection.get_server_info()
            print(f"成功連接到 MySQL 伺服器，版本: {db_info}")

            cursor = connection.cursor()

            with open(file_path, encoding='utf-8') as f:
                f_csv = csv.reader(f)
                next(f_csv)  # 跳過 CSV 的標題行（如果有標題）

                for index, row in enumerate(f_csv):
                    row = [x.strip() for x in row]  # 去掉每一個值的前後空格

                    # 如果欄位數少於 21，補齊 None
                    row_length = 21
                    if len(row) < row_length:
                        row.extend([None] * (row_length - len(row)))

                    try:
                        cursor.execute(insert_script, tuple(row))
                        connection.commit()
                        print(f"Inserted Count: {index + 1}")
                    except Error as e:
                        connection.rollback()
                        print(f"插入失敗，第 {index + 1} 行: {e}")

            cursor.close()
 
    except Error as e:
        print(f"連接失敗: {e}")

    finally:
        if connection.is_connected():
            connection.close()
            print("MySQL 連接已關閉")

def insert_into_db_B(file_path, insert_script, db_table):
    try:
        connection = mysql.connector.connect(
                host="localhost",
                user="root",
                password="",
                database="learning sandbox"
        )
 
        if connection.is_connected():
            db_info = connection.get_server_info()
            print(f"成功連接到 MySQL 伺服器，版本: {db_info}")

            cursor = connection.cursor()

            with open(file_path, encoding='utf-8') as f:
                f_csv = csv.reader(f)
                next(f_csv)  # 跳過 CSV 的標題行（如果有標題）

                for index, row in enumerate(f_csv):
                    row = [x.strip() for x in row]  # 去掉每一個值的前後空格
                        
                    try:
                        cursor.execute(insert_script, tuple(row))
                        connection.commit()
                        print(f"Inserted Count: {index + 1}")
                    except Error as e:
                        connection.rollback()
                        print(f"插入失敗，第 {index + 1} 行: {e}")

            cursor.close()
 
    except Error as e:
        print(f"連接失敗: {e}")

    finally:
        if connection.is_connected():
            connection.close()
            print("MySQL 連接已關閉")

# 主程式入口
if __name__ == "__main__":
    # 指定文件所在的資料夾
    folder_path = '分析文件'
    
    # 生成表格A和B
    generate_visual_analysis_and_save(
        os.path.join(folder_path, 'operation_log_0904.txt'),
        os.path.join(folder_path, '題目檔案_0904.txt'),
        os.path.join(folder_path, '評分標準及各題配分檔案_0904.txt')
    )

    # 插入表格A
    script_A = """INSERT INTO `student_program_attainment`(
                     `sub-question`, `00:00:30`, `00:01:00`, `00:01:30`, `00:02:00`, `00:02:30`, `00:03:00`, 
                     `00:03:30`, `00:04:00`, `00:04:30`, `00:05:00`, `00:05:30`, `00:06:00`, `00:06:30`, 
                     `00:07:00`, `00:07:30`, `00:08:00`, `00:08:30`, `00:09:00`, `00:09:30`, `00:10:00`)                    
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
    insert_into_db_A('表格A.csv', script_A, 'student_program_attainment_try')

    # 插入表格B
    script_B = """INSERT INTO `student_screen_image`(
                     `start_time`, `end_time`, `window`, `content`)                    
                    VALUES (%s, %s, %s, %s)"""
    insert_into_db_B('table_B.csv', script_B, 'student_screen_image')
