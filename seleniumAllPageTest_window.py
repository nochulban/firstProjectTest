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

# Chrome 옵션 설정 (Windows에서도 헤드리스로 작동)
options = Options()
options.add_argument("--headless=new")  # 최신 방식의 헤드리스 모드
options.add_argument("--disable-gpu")
options.add_argument("--window-size=1920,1080")

# 크롬 드라이버 실행
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
options = webdriver.ChromeOptions()
options.add_experimental_option("excludeSwitches", ["enable-logging"])
headers = {"User-Agent": "Mozilla/5.0"}  # 요청 차단 우회용 헤더
browser = webdriver.Chrome(options=options)

# base_url = "https://buckets.grayhatwarfare.com/buckets?type=aws"
# driver.get(base_url)
# time.sleep(2)


#DB Connection Setting
db_config = {
    'host': '',         # 예: 'localhost'
    'user': '',     # 예: 'root'
    'password': '', # 예: 'password'
    'database': '',   # 스키마 이름
    'charset': '',
    'cursorclass': pymysql.cursors.DictCursor
}


try:
    connection = pymysql.connect(**db_config)
    print("데이터베이스 연결 성공!")
except pymysql.MySQLError as e:
    print("에러 발생:", e)    


page = 1
print(f"\n[📄 GrayhatWarfare 버킷 목록 크롤링 시작]\n")

while True:
    print(f"📄 페이지 {page} ------------------------------")
    
    base_url = "https://buckets.grayhatwarfare.com/buckets?type=aws&page=" + str(page)
    driver.get(base_url)
    time.sleep(10)


    try:
        rows = driver.find_elements(By.CSS_SELECTOR, "table.table tbody tr")
        for row in rows:
            cols = row.find_elements(By.TAG_NAME, "td")
            if len(cols) >= 3:
                name_tag = cols[1].find_element(By.TAG_NAME, "a")
                count_tag = cols[2].find_element(By.TAG_NAME, "a")

                name = name_tag.text.strip()
                count = count_tag.text.strip()
                url = name_tag.get_attribute("href")

                httpsName = "https://" + name
                print(f"✅ Test {"https://" + name}")
                #print(f"✅ Test " + url)

                response = requests.get(httpsName, headers=headers, timeout=8, stream=True, verify=False)
                
                if response.status_code == 200:
                    print(f"✅ 연결 가능: {httpsName}")
                    try:
                        with connection.cursor() as cursor:
                            insert_query = """INSERT INTO project_ncb.buckets_test (status_code, connection_state, collected_at, source, file_count, bucket_url)VALUES (%s, %s, %s, %s, %s, %s)"""
                            data = (response.status_code, '정상', datetime.now().strftime('%Y.%m.%d - %H:%M:%S'),'grayhat', count, httpsName )
                            cursor.execute(insert_query, data)
                            connection.commit()
                            print("연결 정상 삽입")
                    
                    except pymysql.MySQLError as e:
                        print("에러 발생:", e)
                
                else:
                    print(f"⚠️ 연결 실패 ({response.status_code}): {url}")
                    try:
                        with connection.cursor() as cursor:
                            insert_query = """INSERT INTO project_ncb.buckets_test (status_code, connection_state, collected_at, source, file_count, bucket_url)VALUES (%s, %s, %s, %s, %s, %s)"""
                            data = (response.status_code, '정상', datetime.now().strftime('%Y.%m.%d - %H:%M:%S'),'grayhat', count, httpsName )
                            cursor.execute(insert_query, data)
                            connection.commit()
                            print("연결 실패 삽입")
                            
                    except pymysql.MySQLError as e:
                        print("에러 발생:", e)
                print(f"🪣 {name} | 📂 파일 수: {count} | 🔗 {url}")
    
    
    except Exception as e:
        print(f"❌ 페이지 {page} 크롤링 중 오류 발생: {e}")
        #break
    response = requests.get(httpsName)
    print(f"[{base_url}] 응답 상태 코드: {response.status_code}")
    page += 1


    # 다음 페이지 버튼 확인 (fa-angle-right 아이콘 사용)
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

driver.quit()
