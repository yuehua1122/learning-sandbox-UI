import tkinter as tk
from tkinter import font as tkfont
import pyshark
import asyncio
import nest_asyncio
import dns.resolver
import time
import mysql.connector  
from collections import defaultdict
import threading

# 設置完整的域名和對應的名稱
all_domains = [
    {"domain": "chatgpt.com", "name": "ChatGPT"},
    {"domain": "claude.ai", "name": "Claude"},
    {"domain": "codeium.com", "name": "Codeium"},
    {"domain": "studio.ai21.com", "name": "AI21 Labs"},
    {"domain": "copilot.cloud.microsoft", "name": "Copilot"},
    {"domain": "www.messenger.com", "name": "Messenger"},
    {"domain": "uts-front.line-apps.com", "name": "LINE"},
]

# 連接資料庫
db_connection = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",  
    database="learning sandbox"
)

# 從資料庫取得 restricted_websites
def get_restricted_websites_from_db(exam_code):
    cursor = db_connection.cursor()
    query = f"SELECT restricted_websites FROM exams WHERE exam_code = '{exam_code}'"
    cursor.execute(query)
    result = cursor.fetchone()
    cursor.close()

    if result:
        return result[0].split(",")  # 分隔成域名列表
    return []

# 將資料庫中的域名與 all_domains 做比對，並生成新的 restricted_domains
def get_selected_domains_from_db(restricted_websites_from_db):
    selected_domains = {}
    for site in restricted_websites_from_db:
        for domain_info in all_domains:
            if domain_info["domain"] == site.strip():
                selected_domains[domain_info["domain"]] = domain_info["name"]
    return selected_domains

# 獲取所有目標域名的 IP 位置
def get_target_ips(domains):
    target_ips = {}
    resolver = dns.resolver.Resolver()
    resolver.nameservers = ['8.8.8.8', '8.8.4.4']
    resolver.lifetime = 10

    for domain, violation_name in domains.items():
        try:
            answers_ipv4 = resolver.resolve(domain, 'A')
            for rdata in answers_ipv4:
                target_ips[rdata.to_text()] = violation_name
        except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN, dns.resolver.Timeout):
            continue
        except Exception as e:
            continue

    return target_ips


# 讓視窗居中顯示
def center_window(window, width=450, height=370):
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()

    # 計算視窗的 X, Y 座標，保持視窗居中
    x = int((screen_width / 2) - (width / 2))
    y = int((screen_height / 2) - (height / 2))
    window.geometry(f'{width}x{height}+{x}+{y}')


# GUI 彈窗
def show_violation_alert(violation_name):
    root = tk.Tk()
    root.withdraw()

    alert = tk.Toplevel()
    center_window(alert)
    alert.overrideredirect(True)
    bg_color = "#F0F0F0"


    custom_font = tkfont.Font(family="BiauKai", size=14)
    bold_font = tkfont.Font(family="BiauKai", size=16, weight="bold")
    use_font = tkfont.Font(family="BiauKai", size=17, weight="bold")
    big_font = tkfont.Font(family="BiauKai", size=22, weight="bold")
    big_warning_font = tkfont.Font(size=44, weight="bold")  # 大一點的警告符號

    # 設定 Frame 與視窗的背景顏色一致
    alert.config(bg=bg_color)
    frame = tk.Frame(alert, bg=bg_color)
    frame.pack(pady=20, fill="both", expand=True)

    # 警告符號和文字
    warning_label = tk.Label(frame, text="⚠️", font=big_warning_font, fg="#FFD306", bg=bg_color)  # 大一點的警告符號
    warning_label.pack(pady=9)

    warning_text = tk.Label(frame, text="🚨  警告  🚨", font=big_font, fg="#FF0A0A", bg=bg_color)
    warning_text.pack(pady=8)

    # 添加警告訊息 
    message_1 = tk.Label(frame, text="根據【考試規則】的規定", font=bold_font, fg="#000000", bg=bg_color)
    message_1.pack(pady=5)

    message_2 = tk.Label(frame, text="請不要使用", font=use_font, fg="#FF0A0A", bg=bg_color)
    message_2.pack(pady=4)

    violation_label = tk.Label(frame, text=f"{violation_name} 這個禁用網站", font=bold_font, fg="#000000", bg=bg_color)
    violation_label.pack(pady=4)


    confirm_button = tk.Button(alert, text="確認", font=custom_font, command=alert.destroy, width=5, height=2, bg="#FFFFFF", fg="#272727")
    confirm_button.pack(pady=6)

    alert.lift()
    alert.attributes('-topmost', True)
    alert.mainloop()

# 開啟新執行緒顯示警告視窗
def run_gui(violation_name):
    threading.Thread(target=show_violation_alert, args=(violation_name,), daemon=True).start()

# 根據 IP 獲取違規名稱
def get_violation_name_by_ip(ip):
    return target_ips.get(ip, "Unknown")

def alert(packet):
    if 'IP' in packet and 'TCP' in packet:
        ip_src = packet.ip.src
        ip_dst = packet.ip.dst

        violation_name = get_violation_name_by_ip(ip_dst)
        if violation_name != "Unknown":
            current_time = time.time()
            violation_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(current_time))
            last_violation = violation_summary[ip_src][violation_name][-1] if violation_summary[ip_src][violation_name] else None

            if not last_violation or (current_time - last_violation['end_time']) > 600:
                violation_summary[ip_src][violation_name].append({
                    "start_time": violation_time,
                    "end_time": current_time
                })
                run_gui(violation_name)
            else:
                last_violation['end_time'] = current_time

# 從資料庫取得老師選擇的域名
exam_code = 'JER395'  # 設定考試代碼
restricted_websites_from_db = get_restricted_websites_from_db(exam_code)

# 生成老師選擇的域名
restricted_domains = get_selected_domains_from_db(restricted_websites_from_db)

# 根據老師選擇的域名進行監控
target_ips = get_target_ips(restricted_domains)
print(f"Target IPs for monitoring: {target_ips}")

# 設置事件循環
loop = asyncio.get_event_loop()
nest_asyncio.apply(loop)

# 創建違規摘要
violation_summary = defaultdict(lambda: defaultdict(list))

# 初始化封包捕獲實例
capture = pyshark.LiveCapture(interface='Wi-Fi')

# 捕獲封包
print("開始捕獲封包...")

try:
    loop.run_until_complete(capture.apply_on_packets(alert))
except KeyboardInterrupt:
    print("捕獲停止")
finally:
    print("捕獲已結束")

    with open('violation_log.txt', 'w', encoding='utf-8') as f:
        for ip_src, violations in violation_summary.items():
            f.write(f"IP 位置: {ip_src}\n")
            print(f"IP 位置: {ip_src}")
            for violation_name, times in violations.items():
                for violation in times:
                    start_time = violation["start_time"]
                    end_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(violation["end_time"]))
                    if start_time and end_time:
                        f.write(f"違規名稱: {violation_name}, 違規行為的時段: {start_time} 到 {end_time}\n")
                        print(f"違規名稱: {violation_name}, 違規行為的時段: {start_time} 到 {end_time}\n")
