from flask import Flask, render_template, jsonify
from flask_sqlalchemy import SQLAlchemy
import psycopg2
import psycopg2.extras
import os
from urllib.parse import quote

app = Flask(__name__, template_folder="templates")  # ✅ 確保 templates 目錄存在

# ✅ 設定 PostgreSQL 連線資訊（加入 debug 訊息）
DATABASE_URL = os.getenv("DATABASE_URL")

# 🔹 確保環境變數存在
if not DATABASE_URL:
    raise ValueError("❌ 環境變數 DATABASE_URL 未設定！")

# 🔹 如果密碼內有特殊字元，則進行 URL 編碼（避免解碼錯誤）
if "@" in DATABASE_URL:
    user_info, host_info = DATABASE_URL.split("@")
    user_info = user_info.split("//")[-1]  # 取得 "user:password"
    encoded_user_info = ":".join([quote(part) for part in user_info.split(":")])  # 編碼 `user:password`
    DATABASE_URL = f"postgresql://{encoded_user_info}@{host_info}"  # **❌ 移除 `?sslmode=require`**

print(f"📌 目前的 DATABASE_URL: {DATABASE_URL}")  # ✅ 檢查環境變數

# 🔹 確保 SQLAlchemy 正確運作
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# ✅ 定義 SQLAlchemy Model
class Student(db.Model):
    __tablename__ = 'students'
    account = db.Column(db.String, primary_key=True)
    name = db.Column(db.String, nullable=False)
    gender = db.Column(db.String, nullable=False)

# ✅ 建立資料庫連線（psycopg2 版本，加入錯誤處理）
def get_db_connection():
    try:
        print("🔍 嘗試連接資料庫...")
        conn = psycopg2.connect(DATABASE_URL, sslmode="require")  # ✅ **這裡加上 `sslmode=require`**
        print("✅ 成功連接到資料庫！")
        return conn
    except UnicodeDecodeError as e:
        print(f"❌ 資料庫連線錯誤（UnicodeDecodeError）: {str(e)}")
        return None
    except Exception as e:
        print(f"❌ 資料庫連線錯誤: {str(e)}")
        return None

@app.route('/')
def home():
    return render_template("index.html")  # ✅ 確保 templates/index.html 存在

@app.route('/get_course_data', methods=['GET'])
def get_course_data():
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "❌ 連線資料庫失敗，請檢查環境變數！"}), 500

    try:
        with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
            cursor.execute("SELECT account, name, gender FROM students")  # ✅ 確保這張表存在！
            students = [dict(row) for row in cursor.fetchall()]  # ✅ 轉換為字典

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

        return jsonify(course_data)  # ✅ 直接回傳 JSON

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






















