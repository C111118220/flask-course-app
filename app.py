from flask import Flask, render_template, jsonify
import psycopg2  # ✅ 改用 PostgreSQL
import psycopg2.extras  # ✅ 讓 cursor 回傳字典
import json
import os

app = Flask(__name__, template_folder="templates")  # ✅ 確保 templates 存在

# ✅ 建立資料庫連線（使用 Render 提供的 PostgreSQL）
def get_db_connection():
    try:
        DATABASE_URL = os.getenv("DATABASE_URL")
        if not DATABASE_URL:
            raise ValueError("❌ 環境變數 DATABASE_URL 未設定！")

        conn = psycopg2.connect(DATABASE_URL, sslmode='require')  # ✅ Render 需要 SSL
        return conn
    except Exception as e:
        print(f"❌ 資料庫連線錯誤: {str(e)}")
        return None

@app.route('/')
def home():
    return render_template("index.html")  # ✅ 確保 index.html 存在

@app.route('/get_course_data', methods=['GET'])
def get_course_data():
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "❌ 連線資料庫失敗，請檢查環境變數！"}), 500

    try:
        with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
            cursor.execute("SELECT account, name, gender FROM merged_data")  # ✅ 確保這張表存在！
            students = [dict(row) for row in cursor.fetchall()]  # ✅ 直接轉換為字典

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

        return jsonify(course_data)  # ✅ 直接用 jsonify 回傳 JSON

    except Exception as e:
        return jsonify({"error": f"❌ 資料庫查詢錯誤: {str(e)}"}), 500

    finally:
        conn.close()  # ✅ 確保關閉資料庫連線

# ✅ 新增測試資料庫連線的 API
@app.route('/test_db')
def test_db():
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "❌ 無法連接到資料庫，請檢查 DATABASE_URL"}), 500

    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT 1")  # 測試查詢
            result = cursor.fetchone()
        return jsonify({"message": "✅ 成功連接到資料庫", "result": result})
    except psycopg2.Error as e:
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)), debug=True)  # ✅ Render / Railway 會使用不同的 PORT




















