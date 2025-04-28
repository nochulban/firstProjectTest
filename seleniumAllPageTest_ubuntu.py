from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
import requests
import time

# Chrome 옵션 설정 (Windows에서도 헤드리스로 작동)
options = Options()
options.add_argument("--headless=new")  # 최신 헤드리스 모드
options.add_argument("--disable-gpu")    # GPU 비활성화
options.add_argument("--window-size=1920,1080")  # 창 크기 설정

# 서비스 경로 설정 (※ 여기는 주의: '/opt/ncb/google-chrome/google-chrome/'은 크롬 브라우저 경로이지 chromedriver 경로 아님)
service = Service(executable_path='/opt/ncb/google-chrome/google-chrome/')  # (잘못된 경로. 보통은 chromedriver 위치를 지정해야 함)

# 다시 Chrome 옵션 추가 (조금 정리 필요)
chrome_options = Options()
chrome_options.add_argument("--headless")           # 헤드리스 모드
chrome_options.add_argument('--no-sandbox')          # 샌드박스 비활성화 (리눅스 환경 권장 설정)
chrome_options.add_argument('--disable-dev-shm-usage')  # 공유 메모리 문제 방지

# 실제 드라이버 실행 (※ options 변수만 적용됨, chrome_options 적용 안 됨 주의!)
driver = webdriver.Chrome(service=Service("/usr/bin/chromedriver"), options=options)

# 추가 옵션: 콘솔 경고 줄이기 (※ 여기서 또 options를 새로 정의함 -> 비효율, 정리 필요)
options = webdriver.ChromeOptions()
options.add_experimental_option("excludeSwitches", ["enable-logging"])

# (※ 주석 처리된 browser 객체는 사용하지 않음)
# browser = webdriver.Chrome(options=options)

# ================= 크롤링 시작 =================

page = 1  # 시작 페이지
print(f"\n[📄 GrayhatWarfare 버킷 목록 크롤링 시작]\n")

while True:
    print(f"📄 페이지 {page} ------------------------------")
    
    # 현재 페이지 URL 생성
    base_url = "https://buckets.grayhatwarfare.com/buckets?type=aws&page=" + str(page)
    driver.get(base_url)  # 해당 페이지로 이동

    time.sleep(3)  # 페이지 로딩 대기 (더 안전하게 하려면 WebDriverWait 추천)

    # (원래 계획은 WebDriverWait으로 요소 등장 대기 -> 현재는 주석처리됨)
    # WebDriverWait(driver, 10).until(
    #    EC.presence_of_element_located((By.CSS_SELECTOR, "table.table tbody tr"))
    # )

    try:
        # 테이블의 각 row(tr) 선택
        rows = driver.find_elements(By.CSS_SELECTOR, "table.table tbody tr")
        for row in rows:
            cols = row.find_elements(By.TAG_NAME, "td")  # 각 행의 열(td) 찾기
            if len(cols) >= 3:
                # 2번째, 3번째 컬럼의 링크(a 태그) 가져오기
                name_tag = cols[1].find_element(By.TAG_NAME, "a")
                count_tag = cols[2].find_element(By.TAG_NAME, "a")

                # 버킷 이름, 파일 수, 링크 추출
                name = name_tag.text.strip()
                count = count_tag.text.strip()
                url = name_tag.get_attribute("href")

                # 결과 출력
                print(f"🪣 {name} | 📂 파일 수: {count} | 🔗 {url}")

    except Exception as e:
        # 크롤링 도중 에러 발생 시 출력하고 반복문 종료
        print(f"❌ 페이지 {page} 크롤링 중 오류 발생: {e}")
        break

    # 현재 페이지 URL로 HTTP 응답 상태 확인
    response = requests.get(base_url)
    print(f"[{base_url}] 응답 상태 코드: {response.status_code}")

    page += 1  # 다음 페이지로

    # (주석처리된 부분) 버튼 클릭 방식으로 다음 페이지 이동하는 코드
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

# 크롤링 완료 후 브라우저 종료
driver.quit()
