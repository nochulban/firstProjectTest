# 필요한 라이브러리 임포트
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
import time

# ========== Chrome 드라이버 설정 ==========
options = Options()
options.add_argument("--headless=new")    # 헤드리스 모드 (브라우저 창을 띄우지 않음)
options.add_argument("--disable-gpu")     # GPU 비활성화 (호환성 향상)
options.add_argument("--window-size=1920,1080")  # 윈도우 사이즈 설정 (웹 요소 깨짐 방지)

# 크롬 드라이버 실행 (자동 설치 및 최신 버전 사용)
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# (주의) 옵션 새로 생성 및 드라이버 중복 실행
options = webdriver.ChromeOptions()
options.add_experimental_option("excludeSwitches", ["enable-logging"])  # 콘솔 경고 줄이기
browser = webdriver.Chrome(options=options)  # 이 browser 객체는 사용되지 않음 (driver만 쓰고 있음)

# ============================================

# ========== 크롤링 시작 ==========
page = 1  # 시작 페이지 번호
print(f"\n[📄 GrayhatWarfare 버킷 목록 크롤링 시작]\n")

while True:
    print(f"📄 페이지 {page} ------------------------------")
    
    # 크롤링할 페이지 URL 생성
    base_url = "https://buckets.grayhatwarfare.com/buckets?type=aws&page=" + str(page)
    driver.get(base_url)  # 페이지 접속
    time.sleep(2)  # 페이지 로딩 대기

    try:
        # 테이블의 모든 행(tr) 가져오기
        rows = driver.find_elements(By.CSS_SELECTOR, "table.table tbody tr")
        for row in rows:
            cols = row.find_elements(By.TAG_NAME, "td")  # 각 행의 열(td) 가져오기
            if len(cols) >= 3:
                # 이름과 파일 수 컬럼의 링크(a 태그) 가져오기
                name_tag = cols[1].find_element(By.TAG_NAME, "a")
                count_tag = cols[2].find_element(By.TAG_NAME, "a")

                name = name_tag.text.strip()  # 버킷 이름
                count = count_tag.text.strip()  # 파일 수
                url = name_tag.get_attribute("href")  # 버킷 URL

                # 결과 출력
                print(f"🪣 {name} | 📂 파일 수: {count} | 🔗 {url}")

    except Exception as e:
        # 크롤링 중 오류 발생 시 출력하고 종료
        print(f"❌ 페이지 {page} 크롤링 중 오류 발생: {e}")
        break

    page += 1  # 다음 페이지로 넘어가기

    # ========== (주석 처리된) 다음 페이지 버튼 이동 코드 ==========
    # try:
    #     next_button = driver.find_element(By.CSS_SELECTOR, 'a.page-link > i.fa.fa-angle-right')
    #     next_button.find_element(By.XPATH, '..').click()  # 다음 버튼 클릭
    #     page += 1
    #     time.sleep(2)
    # except NoSuchElementException:
    #     print("\n✅ 마지막 페이지입니다. 크롤링 완료!")
    #     break
    # except Exception as e:
    #     print(f"❌ 다음 페이지로 이동 중 오류 발생: {e}")
    #     break
# ============================================

# 크롤링 완료 후 드라이버 종료
driver.quit()
