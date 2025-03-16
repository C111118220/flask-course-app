from flask import Flask, render_template, jsonify
from flask_sqlalchemy import SQLAlchemy
import psycopg2
import psycopg2.extras
import os
from urllib.parse import urlparse, urlunparse, parse_qs, urlencode

# 初始化 Flask
app = Flask(__name__, template_folder="templates")  # 確保 templates 目錄存在

# ✅ 處理 DATABASE_URL，保證帶上 sslmode=require
def ensure_sslmode(url):
    parsed = urlparse(url)
    query = parse_qs(parsed.query)

    # 如果沒有帶 sslmode，則自動補上
    if "sslmode" not in query:
        query["sslmode"] = "require"

    new_query = urlencode(query, doseq=True)
    return urlunparse(parsed._replace(query=new_query))

# 讀取 DATABASE_URL 環境變數
DATABASE_URL = os.getenv("DATABASE_URL")

# ✅ 如果沒設定就直接報錯
if not DATABASE_URL:
    raise ValueError("❌ 環境變數 DATABASE_URL 未設定！")

# ✅ 保證 sslmode=require
DATABASE_URL = ensure_sslmode(DATABASE_URL)

print(f"📌 最終 DATABASE_URL: {DATABASE_URL}")

# ✅ 設定 SQLAlchemy 連線
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# 初始化 SQLAlchemy
db = SQLAlchemy(app)

# ✅ 定義 SQLAlchemy Model
class Student(db.Model):
    __tablename__ = 'students'  # 表名
    account = db.Column(db.String, primary_key=True)
    name = db.Column(db.String, nullable=False)
    gender = db.Column(db.String, nullable=False)

# ✅ 建立 psycopg2 資料庫連線（for 查詢 API）
def get_db_connection():
    try:
        print("🔍 嘗試連接資料庫...")
        conn = psycopg2.connect(DATABASE_URL)  # URL 已經含 sslmode=require，不用額外加
        print("✅ 成功連接到資料庫！")
        return conn
    except Exception as e:
        print(f"❌ 資料庫連線錯誤: {str(e)}")
        return None

# ✅ 首頁路由
@app.route('/')
def home():
    return render_template("index.html")  # 確保 templates/index.html 存在

# ✅ 取得課程與學生資料 API
@app.route('/get_course_data', methods=['GET'])
def get_course_data():
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "❌ 連線資料庫失敗，請檢查環境變數！"}), 500

    try:
        with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
            # 確認 students 表存在，欄位正確
            cursor.execute("SELECT student_id AS account, name, gender FROM students")
            students = [dict(row) for row in cursor.fetchall()]

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

        return jsonify(course_data)

    except Exception as e:
        print(f"❌ 資料庫查詢錯誤: {str(e)}")
        return jsonify({"error": f"❌ 資料庫查詢錯誤: {str(e)}"}), 500

    finally:
        conn.close()  # 關閉連線

# ✅ 測試資料庫連線 API
@app.route('/test_db')
def test_db():
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "❌ 無法連接到資料庫，請檢查 DATABASE_URL"}), 500

    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT 1")  # 單純測試連線
            result = cursor.fetchone()
        return jsonify({"message": "✅ 成功連接到資料庫", "result": result})
    except psycopg2.Error as e:
        print(f"❌ 測試查詢錯誤: {str(e)}")
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()

# ✅ 啟動 Flask 應用
if __name__ == '__main__':
    port = int(os.getenv("PORT", 5000))  # 支援 Heroku / Render 動態 port
    app.run(host="0.0.0.0", port=port, debug=True)























