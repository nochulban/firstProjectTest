# 필요한 라이브러리 불러오기
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
from datetime import datetime
import pymysql
import requests
import time

# Chrome 옵션 설정 (윈도우/리눅스에서도 헤드리스로 작동하게)
options = Options()
options.add_argument("--headless=new")  # 최신 헤드리스 모드 사용
options.add_argument("--disable-gpu")   # GPU 가속 비활성화
options.add_argument("--window-size=1920,1080")  # 창 크기 설정

# ChromeDriver 실행 (자동 다운로드 및 설치)
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# 추가 옵션 (로깅 최소화) 설정
options = webdriver.ChromeOptions()
options.add_experimental_option("excludeSwitches", ["enable-logging"])

# User-Agent 설정 (차단 우회용)
headers = {"User-Agent": "Mozilla/5.0"}

# (불필요) browser 객체 따로 만들었지만 실제로 사용 안 함
browser = webdriver.Chrome(options=options)  # 이건 사실상 의미 없음

# ========== 데이터베이스 연결 설정 ==========

db_config = {
    'host': '',         # DB 서버 주소 (ex: 'localhost')
    'user': '',         # DB 사용자 이름
    'password': '',     # DB 비밀번호
    'database': '',     # 사용할 데이터베이스명
    'charset': '',      # 문자 인코딩 (ex: 'utf8mb4')
    'cursorclass': pymysql.cursors.DictCursor  # 결과를 딕셔너리 형태로 반환
}

# 데이터베이스 연결 시도
try:
    connection = pymysql.connect(**db_config)
    print("데이터베이스 연결 성공!")
except pymysql.MySQLError as e:
    print("에러 발생:", e)    

# ============================================

# 크롤링 시작
page = 1
print(f"\n[📄 GrayhatWarfare 버킷 목록 크롤링 시작]\n")

while True:
    print(f"📄 페이지 {page} ------------------------------")
    
    # 현재 페이지 URL 생성
    base_url = "https://buckets.grayhatwarfare.com/buckets?type=aws&page=" + str(page)
    driver.get(base_url)
    time.sleep(10)  # 페이지 로딩 대기 (10초는 꽤 김, 최적화 가능)

    try:
        # 테이블의 모든 행(row) 가져오기
        rows = driver.find_elements(By.CSS_SELECTOR, "table.table tbody tr")
        for row in rows:
            cols = row.find_elements(By.TAG_NAME, "td")
            if len(cols) >= 3:
                # 2번째 컬럼: 버킷 이름 링크
                # 3번째 컬럼: 파일 수 링크
                name_tag = cols[1].find_element(By.TAG_NAME, "a")
                count_tag = cols[2].find_element(By.TAG_NAME, "a")

                name = name_tag.text.strip()
                count = count_tag.text.strip()
                url = name_tag.get_attribute("href")

                # 실제 연결 테스트를 위해 https URL 생성
                httpsName = "https://" + name
                print(f"✅ Test {httpsName}")

                # 해당 버킷 URL로 GET 요청
                response = requests.get(httpsName, headers=headers, timeout=8, stream=True, verify=False)

                # 연결 성공(200 OK)
                if response.status_code == 200:
                    print(f"✅ 연결 가능: {httpsName}")
                    try:
                        with connection.cursor() as cursor:
                            insert_query = """INSERT INTO project_ncb.buckets_test 
                                (status_code, connection_state, collected_at, source, file_count, bucket_url)
                                VALUES (%s, %s, %s, %s, %s, %s)"""
                            data = (response.status_code, '정상', datetime.now().strftime('%Y.%m.%d - %H:%M:%S'), 'grayhat', count, httpsName)
                            cursor.execute(insert_query, data)
                            connection.commit()
                            print("연결 정상 삽입")
                    except pymysql.MySQLError as e:
                        print("에러 발생:", e)

                # 연결 실패 (예: 403, 404 등)
                else:
                    print(f"⚠️ 연결 실패 ({response.status_code}): {url}")
                    try:
                        with connection.cursor() as cursor:
                            insert_query = """INSERT INTO project_ncb.buckets_test 
                                (status_code, connection_state, collected_at, source, file_count, bucket_url)
                                VALUES (%s, %s, %s, %s, %s, %s)"""
                            data = (response.status_code, '정상', datetime.now().strftime('%Y.%m.%d - %H:%M:%S'), 'grayhat', count, httpsName)
                            cursor.execute(insert_query, data)
                            connection.commit()
                            print("연결 실패 삽입")
                    except pymysql.MySQLError as e:
                        print("에러 발생:", e)

                # 버킷 이름과 파일 수 출력
                print(f"🪣 {name} | 📂 파일 수: {count} | 🔗 {url}")

    except Exception as e:
        print(f"❌ 페이지 {page} 크롤링 중 오류 발생: {e}")
        # break 대신 계속 진행함

    # (여기 문제 있음) httpsName에 대해 또 요청 보내고 있음 -> 위에서 이미 했는데 중복 요청임
    response = requests.get(httpsName)
    print(f"[{base_url}] 응답 상태 코드: {response.status_code}")

    page += 1  # 다음 페이지로 이동

    # (주석 처리된) 다음 페이지 버튼 이동 코드
    # try:
    #     next_button = driver.find_element(By.CSS_SELECTOR, 'a.page-link > i.fa.fa-angle-right')
    #     next_button.find_element(By.XPATH, '..').click()
    #     page += 1
    #     time.sleep(2)
    # except NoSuchElementException:
    #     print("\n✅ 마지막 페이지입니다. 크롤링 완료!")
    #     break
    # except Exception as e:
    #     print(f"❌ 다음 페이지로 이동 중 오류 발생: {e}")
    #     break

# 크롤링 종료 후 드라이버 닫기
driver.quit()
