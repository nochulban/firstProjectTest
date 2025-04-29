# 필요한 라이브러리 불러오기
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
import time

# ========== Chrome 드라이버 설정 ==========
options = Options()
options.add_argument("--headless=new")    # 최신 방식의 헤드리스 모드 사용 (브라우저 창 안 띄움)
options.add_argument("--disable-gpu")     # GPU 가속 비활성화 (호환성 향상)
options.add_argument("--window-size=1920,1080")  # 창 크기 설정 (웹 요소 안깨지게)

# ChromeDriver 실행 (webdriver-manager로 자동 설치)
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# 추가 Chrome 옵션 설정 (로깅 줄이기)
options = webdriver.ChromeOptions()
options.add_experimental_option("excludeSwitches", ["enable-logging"])

# (사용되지 않는) 추가 브라우저 객체 생성 (browser)
browser = webdriver.Chrome(options=options)  # ※ 실제로는 driver만 사용하고 있음

# ========== 크롤링 시작 ==========
page = 1  # 시작 페이지 설정
print(f"\n[📄 GrayhatWarfare 버킷 목록 크롤링 시작]\n")

while True:
    print(f"📄 페이지 {page} ------------------------------")
    
    # 현재 페이지 URL 생성
    base_url = "https://buckets.grayhatwarfare.com/buckets?type=aws&page=" + str(page)
    driver.get(base_url)  # 해당 페이지 접속
    time.sleep(2)         # 페이지 로딩 대기 (2초)

    try:
        # 테이블 안의 모든 행(tr) 가져오기
        rows = driver.find_elements(By.CSS_SELECTOR, "table.table tbody tr")
        for row in rows:
            cols = row.find_elements(By.TAG_NAME, "td")  # 각 행의 열(td) 가져오기
            if len(cols) >= 3:
                # 버킷 이름과 파일 수가 있는 컬럼 가져오기
                name_tag = cols[1].find_element(By.TAG_NAME, "a")
                count_tag = cols[2].find_element(By.TAG_NAME, "a")

                # 텍스트와 링크 추출
                name = name_tag.text.strip()  # 버킷 이름
                count = count_tag.text.strip()  # 파일 수
                url = name_tag.get_attribute("href")  # 버킷 URL

                # 결과 출력
                print(f"🪣 {name} | 📂 파일 수: {count} | 🔗 {url}")

    except Exception as e:
        # 페이지 크롤링 도중 에러 발생시 출력 후 종료
        print(f"❌ 페이지 {page} 크롤링 중 오류 발생: {e}")
        break

    # 다음 페이지 번호 증가
    page += 1

    # ========== (주석 처리된) 다음 페이지 이동 방법 ==========
    # 다음 버튼(→) 클릭해서 이동하려는 시도
    # try:
    #     next_button = driver.find_element(By.CSS_SELECTOR, 'a.page-link > i.fa.fa-angle-right')
    #     next_button.find_element(By.XPATH, '..').click()  # 아이콘의 부모 요소(a 태그) 클릭
    #     page += 1
    #     time.sleep(2)
    # except NoSuchElementException:
    #     # 다음 페이지 없으면 크롤링 종료
    #     print("\n✅ 마지막 페이지입니다. 크롤링 완료!")
    #     break
    # except Exception as e:
    #     # 다음 페이지 이동 중 다른 오류 발생시 종료
    #     print(f"❌ 다음 페이지로 이동 중 오류 발생: {e}")
    #     break

# 크롤링 종료 후 드라이버 닫기
driver.quit()
