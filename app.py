from flask import Flask, render_template, jsonify
import pymysql
import json
import os  # ✅ 讀取環境變數

app = Flask(__name__, template_folder="templates")  # ✅ 指定 templates 資料夾

# ✅ 建立資料庫連線（使用 Railway 環境變數）
def get_db_connection():
    try:
        conn = pymysql.connect(
            host=os.getenv("DB_HOST", "localhost"),
            user=os.getenv("DB_USER", "root"),
            password=os.getenv("DB_PASSWORD", "12345678"),
            database=os.getenv("DB_NAME", "faq_db"),
            port=int(os.getenv("DB_PORT", 3306)),  # ✅ Railway 可能使用不同 Port
            cursorclass=pymysql.cursors.DictCursor,
            charset='utf8mb4'
        )
        with conn.cursor() as cursor:
            cursor.execute("SET NAMES utf8mb4;")
            cursor.execute("SET CHARACTER SET utf8mb4;")
            cursor.execute("SET character_set_connection=utf8mb4;")
        return conn
    except pymysql.MySQLError as e:
        print(f"❌ 資料庫連線錯誤: {str(e)}")  # ✅ 顯示錯誤日誌
        return None

@app.route('/')
def home():
    return render_template("index.html")  # ✅ 確保載入前端頁面

@app.route('/get_course_data', methods=['GET'])
def get_course_data():
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "❌ 連線資料庫失敗，請檢查環境變數！"}), 500

    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT account, name, gender FROM merged_data")
            students = cursor.fetchall()

        course_data = {
            "teacher": "鄭進興",
            "course_name": "企業資訊網路",
            "description": "教導學生了解網際網路運作原理，建立 TCP/IP 網際網路通信協定之整體概念...",
            "class": "資管系三乙",
            "grading": "平時考試: 30% | 期中考試: 30% | 期末考試: 40%",
            "credits": 3.0,
            "hours": 3.0,
            "schedule": "星期一 6-8 節",
            "location": "C218",
            "students": students
        }

        json_data = json.dumps(course_data, ensure_ascii=False)
        response = app.response_class(json_data, content_type="application/json; charset=utf-8")
        return response

    except pymysql.MySQLError as e:
        return jsonify({"error": f"❌ 資料庫查詢錯誤: {str(e)}"}), 500

    finally:
        conn.close()  # ✅ 確保關閉資料庫連線

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)), debug=True)  # ✅ Railway 可能使用不同的 PORT

















