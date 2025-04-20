from flask import Flask, render_template, jsonify
from flask_sqlalchemy import SQLAlchemy
import psycopg2
import psycopg2.extras
import os
from urllib.parse import urlparse, urlunparse, parse_qs, urlencode

# ✅ 初始化 Flask
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

# ✅ 讀取 DATABASE_URL 環境變數
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

# ✅ 初始化 SQLAlchemy
db = SQLAlchemy(app)

# ✅ 定義 SQLAlchemy Model（非必要，但保留）
class Student(db.Model):
    __tablename__ = 'students'  # 資料表名稱
    account = db.Column(db.String, primary_key=True)
    name = db.Column(db.String, nullable=False)
    gender = db.Column(db.String, nullable=False)

# ✅ 建立 psycopg2 資料庫連線（for 查詢 API）
def get_db_connection():
    try:
        print("🔍 嘗試連接資料庫...")
        conn = psycopg2.connect(DATABASE_URL)  # URL 已經含 sslmode=require
        print("✅ 成功連接到資料庫！")
        return conn
    except Exception as e:
        print(f"❌ 資料庫連線錯誤: {str(e)}")
        return None

# ✅ 首頁路由
@app.route('/')
def home():
    return render_template("index.html")  # 確保 templates/index.html 存在

# ✅ 課程資訊與學生資料 API
@app.route('/get_course_data', methods=['GET'])
def get_course_data():
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "❌ 連線資料庫失敗，請檢查環境變數！"}), 500

    try:
        with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
            # 查詢學生名單
            cursor.execute("SELECT student_id AS account, name, gender FROM students")
            students = [dict(row) for row in cursor.fetchall()]

            # 課程資訊
            course_data = {
                "teacher": "鄭進興",
                "course_name": "企業資訊網路",
                "email": "jscheng@nkust.edu.tw",
                "description": (
                    "教導學生瞭解網際網路運作原理，建立 TCP/IP 網際網路通信協定之整體概念。"
                    "訓練學生熟悉區域網路、網路設備之規劃與操作。"
                    "使學生瞭解企業網路架構規劃及建置實務，"
                    "培養學生具備企業網路管理技能，"
                    "進未來未進入工作職場，能勝任企業網路正確建置之本職學能。"
                ),
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
            cursor.execute("SELECT 1")  # 單純測試
            result = cursor.fetchone()
        return jsonify({"message": "✅ 成功連接到資料庫", "result": result})

    except psycopg2.Error as e:
        print(f"❌ 測試查詢錯誤: {str(e)}")
        return jsonify({"error": str(e)}), 500

    finally:
        conn.close()

# ✅ 健康檢查路由（Render Health Check 使用）
@app.route('/health')
def health():
    return "OK", 200

# ✅ 啟動 Flask 應用（for local 測試）
if __name__ == '__main__':
    port = int(os.getenv("PORT", 5000))  # Render / Heroku 動態 port
    app.run(host="0.0.0.0", port=port, debug=True)


@app.route('/init_db')
def init_db():
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "❌ 無法連接資料庫"}), 500

    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS students (
                    id SERIAL PRIMARY KEY,
                    student_id VARCHAR(20) NOT NULL,
                    name VARCHAR(100) NOT NULL,
                    gender VARCHAR(10) NOT NULL,
                    email VARCHAR(100),
                    class VARCHAR(50)
                );
            """)

            # ⚠️ 簡化測試資料（避免卡住）
            cursor.execute("""
                INSERT INTO students (student_id, name, gender, email, class) VALUES
                ('C111118201', '張又允', '女', '', ''),
                ('C111118202', '黃子軒', '男', '', ''),
                ('C111118203', '李志明', '男', '', '')
                ON CONFLICT DO NOTHING;
            """)

            conn.commit()
        return jsonify({"message": "✅ 資料表建立並匯入資料成功"})
    except Exception as e:
        return jsonify({"error": str(e)})
    finally:
        conn.close()






















