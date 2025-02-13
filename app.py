from flask import Flask, render_template, jsonify
import pymysql
import json

app = Flask(__name__, template_folder="templates")  # ✅ 指定 templates 資料夾

# ✅ 建立資料庫連線
def get_db_connection():
    conn = pymysql.connect(
        host="localhost",        
        user="root",             
        password="12345678",     
        database="faq_db",       
        cursorclass=pymysql.cursors.DictCursor,
        charset='utf8mb4'       
    )
    
    with conn.cursor() as cursor:
        cursor.execute("SET NAMES utf8mb4;")
        cursor.execute("SET CHARACTER SET utf8mb4;")
        cursor.execute("SET character_set_connection=utf8mb4;")
    
    return conn

@app.route('/')
def home():
    return render_template("index.html")  # ✅ 確保載入前端頁面

@app.route('/get_course_data', methods=['GET'])
def get_course_data():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT account, name, gender FROM merged_data")
        students = cursor.fetchall()

        course_data = {
            "teacher": "鄭進興",
            "course_name": "企業資訊網路",
            "description": "教導學生了解網際網路運作原理，建立 TCP/IP 網際網路通信協定之整體概念。訓練學生熟悉區域網路、網路設備之規劃與作設定，從概念中掌握企業網路規劃及建置實務。培養學生具備企業網路管理技能，奠定未來進入工作職場擔任網管工程師之本職學能。",
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
        return jsonify({"error": f"資料庫錯誤: {str(e)}"}), 500

    finally:
        cursor.close()
        conn.close()

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)














