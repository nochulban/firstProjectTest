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

# ========== Chrome 드라이버 설정 ==========
options = Options()
options.add_argument("--headless=new")    # 최신 방식의 헤드리스 모드 사용
options.add_argument("--disable-gpu")     # GPU 가속 비활성화
options.add_argument("--window-size=1920,1080")  # 창 크기 설정

# ChromeDriver 실행 (webdriver-manager로 설치)
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# 추가 Chrome 옵션 (로깅 줄이기)
options = webdriver.ChromeOptions()
options.add_experimental_option("excludeSwitches", ["enable-logging"])

# HTTP 요청 시 사용할 User-Agent 설정 (요청 차단 우회용)
headers = {"User-Agent": "Mozilla/5.0"}

# (사용되지 않지만 생성된) browser 객체
browser = webdriver.Chrome(options=options)

# ===========================================

# ========== DB 연결 설정 ==========
# DB 접속 정보 (IP, 포트, 사용자명, 비밀번호, 데이터베이스명, 문자셋 설정)
db_config = {
    'host': '211.188.61.145',
    'user': 'ncb',
    'password': 'spzmfzoa2025!@#',
    'database': 'project_ncb',
    'charset': 'utf8mb4',
    'cursorclass': pymysql.cursors.DictCursor
}

# 데이터베이스 연결 시도
try:
    connection = pymysql.connect(**db_config)
    print("데이터베이스 연결 성공!")
except pymysql.MySQLError as e:
    print("에러 발생:", e)

# ===========================================

# 크롤링 시작
page = 1
print(f"\n[📄 GrayhatWarfare 버킷 목록 크롤링 시작]\n")

while True:
    print(f"📄 페이지 {page} ------------------------------")

    # 크롤링할 현재 페이지 URL 설정
    base_url = "https://buckets.grayhatwarfare.com/buckets?type=aws&page=" + str(page)
    driver.get(base_url)  # 페이지 접속
    time.sleep(10)        # 페이지 로딩 대기 (10초)

    try:
        # 테이블의 모든 행(tr) 가져오기
        rows = driver.find_elements(By.CSS_SELECTOR, "table.table tbody tr")
        for row in rows:
            cols = row.find_elements(By.TAG_NAME, "td")  # 각 행의 열(td) 가져오기
            if len(cols) >= 3:
                # 2번째, 3번째 컬럼에서 a 태그 찾기
                name_tag = cols[1].find_element(By.TAG_NAME, "a")
                count_tag = cols[2].find_element(By.TAG_NAME, "a")

                # 버킷 이름과 파일 수 텍스트 추출
                name = name_tag.text.strip()
                count = count_tag.text.strip()
                url = name_tag.get_attribute("href")

                # 연결 테스트할 버킷 URL 생성
                httpsName = "https://" + name
                print(f"✅ Test {"https://" + name}")

                # 버킷에 대해 HTTP 요청
                response = requests.get(httpsName, headers=headers, timeout=8, stream=True, verify=False)
                
                # 응답 상태에 따라 분기
                if response.status_code == 200:
                    print(f"✅ 연결 가능: {httpsName}")
                    try:
                        with connection.cursor() as cursor:
                            # 연결 성공한 버킷 정보를 DB에 삽입
                            insert_query = """INSERT INTO project_ncb.buckets_test 
                                (status_code, connection_state, collected_at, source, file_count, bucket_url)
                                VALUES (%s, %s, %s, %s, %s, %s)"""
                            data = (response.status_code, '정상', datetime.now().strftime('%Y.%m.%d - %H:%M:%S'), 'grayhat', count, httpsName)
                            cursor.execute(insert_query, data)
                            connection.commit()
                            print("연결 정상 삽입")
                    except pymysql.MySQLError as e:
                        print("에러 발생:", e)

                else:
                    print(f"⚠️ 연결 실패 ({response.status_code}): {url}")
                    try:
                        with connection.cursor() as cursor:
                            # 연결 실패한 버킷 정보를 DB에 삽입
                            insert_query = """INSERT INTO project_ncb.buckets_test 
                                (status_code, connection_state, collected_at, source, file_count, bucket_url)
                                VALUES (%s, %s, %s, %s, %s, %s)"""
                            data = (response.status_code, '정상', datetime.now().strftime('%Y.%m.%d - %H:%M:%S'), 'grayhat', count, httpsName)
                            cursor.execute(insert_query, data)
                            connection.commit()
                            print("연결 실패 삽입")
                    except pymysql.MySQLError as e:
                        print("에러 발생:", e)

                # 버킷 정보 출력
                print(f"🪣 {name} | 📂 파일 수: {count} | 🔗 {url}")

    except Exception as e:
        # 페이지 크롤링 도중 오류 발생 시 출력
        print(f"❌ 페이지 {page} 크롤링 중 오류 발생: {e}")
        # break 주석 처리되어 있어 다음 페이지로 넘어감

    # (중복 요청) 마지막에 httpsName에 대해 또 요청 보내고 상태코드 출력
    response = requests.get(httpsName)
    print(f"[{base_url}] 응답 상태 코드: {response.status_code}")

    # 다음 페이지로 이동
    page += 1

    # ========== (주석 처리된) 다음 페이지 버튼 이동 방법 ==========
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

# 크롤링 완료 후 드라이버 종료
driver.quit()
