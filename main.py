import csv
import pandas as pd
from flask import render_template, Flask, request, jsonify, send_from_directory
from datetime import datetime
import MySQLdb
import subprocess

# import matplotlib.pyplot as plt
# import base64
# import io
#
#
# # 그래프를 생성하는 함수
# def generate_plot():
#     # 데이터를 기반으로 Matplotlib 그래프 생성
#     data = [5, 10, 15, 20, 25]
#     plt.figure(figsize=(8, 6))
#     plt.bar(range(len(data)), data)
#     plt.xlabel('X Label')
#     plt.ylabel('Y Label')
#     plt.title('Sample Bar Chart')
#
#     # 이미지를 메모리에 저장
#     buffer = io.BytesIO()
#     plt.savefig(buffer, format='png')
#     buffer.seek(0)
#
#     # 이미지를 Base64로 변환하여 반환
#     image_base64 = base64.b64encode(buffer.getvalue()).decode()
#     buffer.close()
#
#     return image_base64




app = Flask(__name__, template_folder='templates')
REACT_APP_BUILD_FOLDER = 'C:/react-news/build'  # 여기에 리액트 앱 빌드 폴더의 경로를 입력하세요
# MySQL 데이터베이스 연결 설정
conn = MySQLdb.connect(host="localhost", port=3306,
                       user="root", passwd="1234", db="project2")
cursor = conn.cursor()

# CSV 파일의 데이터를 MySQL 데이터베이스에 삽입하기 전에 중복 데이터 확인 및 초기화
def check_existing_data_seoul_eat(cursor):
    sql_query = "SELECT COUNT(*) FROM seoul_eat"
    cursor.execute(sql_query)
    result = cursor.fetchone()
    count = result[0]
    return count > 0  # True면 데이터가 이미 있음, False면 데이터가 없음

def check_existing_data_tbl_seoul3(cursor):
    sql_query = "SELECT COUNT(*) FROM tbl_seoul3"
    cursor.execute(sql_query)
    result = cursor.fetchone()
    count = result[0]
    return count > 0

def clear_table_seoul_eat(cursor):
    sql_query = "TRUNCATE TABLE seoul_eat"
    cursor.execute(sql_query)
    conn.commit()

def clear_table_tbl_seoul3(cursor):
    sql_query = "TRUNCATE TABLE tbl_seoul3"
    cursor.execute(sql_query)
    conn.commit()

def insert_data_from_csv_seoul_eat():
    with open('seouleat.csv', encoding='cp949') as csvfile:
        reader = csv.DictReader(csvfile, delimiter=',')
        for idx, row in enumerate(reader):
            sql_insert = 'INSERT INTO seoul_eat(city, menu, mainMenu, mainName, information, link) VALUES(%s, %s, %s, %s, %s, %s)'
            cursor.execute(sql_insert, (row['도시명'], row['음식종류'], row['대표메뉴'], row['식당상호'], row['추천사유'], row['링크']))
            conn.commit()

def insert_data_from_csv_tbl_seoul3():
    with open('seoulCulture.csv', encoding='cp949') as csvfile:
        reader = csv.DictReader(csvfile, delimiter=',')
        for idx, row in enumerate(reader):
            sql_insert = 'INSERT INTO tbl_seoul3(classification, region, festival, place, festival_place, age, pay, link, img) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s)'
            cursor.execute(sql_insert, (row['분류'], row['자치구'], row['공연/행사명'], row['장소'], row['기관명'], row['이용대상'], row['이용요금'], row['홈페이지주소'], row['대표이미지']))
            conn.commit()

# 데이터베이스 초기화 및 데이터 삽입
def initialize_database():
    data_exists_seoul_eat = check_existing_data_seoul_eat(cursor)
    if data_exists_seoul_eat:
        clear_table_seoul_eat(cursor)
    insert_data_from_csv_seoul_eat()

    data_exists_tbl_seoul3 = check_existing_data_tbl_seoul3(cursor)
    if data_exists_tbl_seoul3:
        clear_table_tbl_seoul3(cursor)
    insert_data_from_csv_tbl_seoul3()



# 초기화된 데이터베이스로 Flask 애플리케이션 실행
if __name__ == "__main__":
    initialize_database()  # 데이터베이스 초기화 및 CSV 데이터 삽입

    @app.route('/')
    def index():
        return render_template('index.html')


    # # Flask 애플리케이션에서 해당 이미지를 HTML에 삽입하는 부분
    # @app.route('/graph')
    # def show_graph():
    #     graph_image = generate_plot()  # 이미지 생성 함수 호출
    #     return render_template('graph.html', graph_image=graph_image)

    @app.route('/login')
    def login():
        return render_template('login.html')


    @app.route('/register')
    def register():
        return render_template('register.html')


    @app.route("/register", methods=['POST'])
    def j_member_post():
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        phone = request.form['phone']
        gender = request.form['gender']
        birthday_str = request.form['birthday']

        birthday_date = datetime.strptime(birthday_str, '%m/%d/%Y').date()
        print(name, email, password, phone, gender, birthday_str)
        try:
            birthday_date = datetime.strptime(birthday_str, '%m/%d/%Y').date()
        except ValueError as e:
            print(f"날짜 변환 오류: {e}")

        sql_insert = 'INSERT INTO usertbl(name, gender, email, phone, password, birthday) VALUES (%s, %s, %s, %s, %s, %s)'
        cursor.execute(sql_insert, (name, gender, email, phone, password, birthday_date))
        conn.commit()
        return render_template("index.html")

    @app.route('/seoultest')
    def seoultest():
        return render_template('seoultest.html')

    @app.route('/test')
    def test():
        return render_template('test.html')

    @app.route('/testfile')
    def testfile():
        return render_template('testfile.html')

    @app.route('/game')
    def game():
        return render_template('game.html')


    @app.route('/login', methods=['POST'])
    def login_post():
        # 폼에서 제출된 이메일 및 비밀번호 가져오기
        email = request.form['email']
        password_candidate = request.form['password']
        print(email, password_candidate)
        # 데이터베이스에서 사용자 조회
        cur = conn.cursor()
        result = cur.execute("SELECT * FROM usertbl WHERE email = %s", [email])
        print('result', result)
        if result > 0:
            # 사용자 정보 가져오기
            data = cur.fetchone()
            print(data)
            password_db = data[5]
            print('password', password_db)
            # 비밀번호 검증
            if (password_candidate == password_db):
                return render_template("index.html")
                alert("환영해요")
            else:
                return render_template('login.html')
        else:
            return render_template('login.html')

    @app.route('/start_react_server', methods=['GET'])
    def start_react_server():
        try:
            subprocess.Popen('cd /d C:\\react-news && npm start', shell=True)
            return jsonify({'message': 'React server started successfully!'})
        except Exception as e:
            return jsonify({'error': str(e)})


    @app.route('/react-news/test/src/<path:filename>')
    def react_news(filename):
        return send_from_directory('C:/react-news/test/src', filename)

    @app.route('/eat', methods=['GET'])
    def eat():
        query = request.args.get('query', '')

        sql_query = "SELECT * FROM seoul_eat"

        if query: 
            sql_query += f" WHERE city LIKE '%{query}%' OR menu LIKE '%{query}%' OR mainMenu LIKE '%{query}%' OR mainName LIKE '%{query}%' OR information LIKE '%{query}%' OR link LIKE '%{query}%'"

        try:
            cursor.execute(sql_query)
            data_list = cursor.fetchall()
        except Exception as e:
            print("에러 발생:", e)
            data_list = []

        items_per_page = 10  # 한 페이지에 보여줄 아이템 수
        page = request.args.get('page', 1, type=int)  # 현재 페이지 번호

        if data_list:  # 검색 결과가 있는 경우
            start_index = (page - 1) * items_per_page
            end_index = start_index + items_per_page
            paginated_data = data_list[start_index:end_index]

            num_pages = (len(data_list) - 1) // items_per_page + 1
        else:  # 검색 결과가 없는 경우
            paginated_data = []
            num_pages = 0

        return render_template('eat.html', data=paginated_data, num_pages=num_pages, current_page=page, query=query)



    @app.route('/helloseoul', methods=['GET'])
    def helloseoul():
        query = request.args.get('query', '')  # 검색어를 가져옴

        sql_query = "SELECT * FROM tbl_seoul3"

        if query:  # 검색어가 있는 경우
            sql_query += f" WHERE classification LIKE '%{query}%' OR region LIKE '%{query}%' OR festival LIKE '%{query}%' OR place LIKE '%{query}%' OR festival_place LIKE '%{query}%' OR age LIKE '%{query}%' OR age pay '%{query}%' OR link LIKE '%{query}%' OR img LIKE '%{query}%'"

        try:
            cursor.execute(sql_query)
            data_list = cursor.fetchall()
        except Exception as e:
            print("에러 발생:", e)  # 쿼리 실행 중 에러 출력 (디버깅용)
            data_list = []

        items_per_page = 10  # 한 페이지에 보여줄 아이템 수
        page = request.args.get('page', 1, type=int)  # 현재 페이지 번호

        if data_list:  # 검색 결과가 있는 경우
            start_index = (page - 1) * items_per_page
            end_index = start_index + items_per_page
            paginated_data = data_list[start_index:end_index]

            num_pages = (len(data_list) - 1) // items_per_page + 1
        else:  # 검색 결과가 없는 경우
            paginated_data = []
            num_pages = 0

        return render_template('helloseoul.html', data=paginated_data, num_pages=num_pages, current_page=page, query=query)



    app.run(host="0.0.0.0", port="5000", debug=True)