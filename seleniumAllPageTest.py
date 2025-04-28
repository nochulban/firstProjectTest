from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
import time

# 크롬 옵션 설정 (윈도우에서도 헤드리스 모드로 작동)
options = Options()
options.add_argument("--headless=new")  # 최신 헤드리스 모드 사용
options.add_argument("--disable-gpu")   # GPU 비활성화 (호환성 향상)
options.add_argument("--window-size=1920,1080")  # 창 크기 지정 (안 하면 요소 못 찾는 경우 방지)

# 크롬 드라이버 실행 (webdriver-manager로 자동 설치)
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# (불필요한 중복) 새로운 옵션 객체 생성 및 드라이버 다시 실행하려고 하는 코드 —> 사실 여기부터는 필요 없음
options = webdriver.ChromeOptions()
options.add_experimental_option("excludeSwitches", ["enable-logging"])  # 콘솔 로그 줄이기 설정
browser = webdriver.Chrome(options=options)  # 새로 만든 browser 객체 (하지만 위에 driver로 이미 실행했음)

# ============ (여기까지 셋업) ============

# 크롤링 시작 출력
page = 1
print(f"\n[📄 GrayhatWarfare 버킷 목록 크롤링 시작]\n")

while True:
    print(f"📄 페이지 {page} ------------------------------")
    
    # 현재 페이지 URL 설정
    base_url = "https://buckets.grayhatwarfare.com/buckets?type=aws&page=" + str(page)
    driver.get(base_url)  # 페이지 열기
    time.sleep(2)         # 로딩 대기 (2초)

    try:
        # 테이블의 각 행(row) 찾기
        rows = driver.find_elements(By.CSS_SELECTOR, "table.table tbody tr")
        for row in rows:
            # 각 행에서 컬럼(td) 가져오기
            cols = row.find_elements(By.TAG_NAME, "td")
            if len(cols) >= 3:
                # 이름과 파일 수가 있는 컬럼에서 링크(a 태그) 추출
                name_tag = cols[1].find_element(By.TAG_NAME, "a")
                count_tag = cols[2].find_element(By.TAG_NAME, "a")

                name = name_tag.text.strip()     # 버킷 이름
                count = count_tag.text.strip()   # 파일 수
                url = name_tag.get_attribute("href")  # 버킷 URL

                # 버킷 정보 출력
                print(f"🪣 {name} | 📂 파일 수: {count} | 🔗 {url}")
    except Exception as e:
        # 크롤링 도중 에러 발생 시 출력하고 종료
        print(f"❌ 페이지 {page} 크롤링 중 오류 발생: {e}")
        break

    page += 1  # 다음 페이지로 이동

    # (주석처리된 부분) 다음 페이지 버튼을 클릭해서 이동하는 로직
    # try:
    #     next_button = driver.find_element(By.CSS_SELECTOR, 'a.page-link > i.fa.fa-angle-right')
    #     next_button.find_element(By.XPATH, '..').click()  # 아이콘의 부모 a 태그 클릭
    #     page += 1
    #     time.sleep(2)
    # except NoSuchElementException:
    #     # 다음 버튼 없으면 마지막 페이지로 간주하고 종료
    #     print("\n✅ 마지막 페이지입니다. 크롤링 완료!")
    #     break
    # except Exception as e:
    #     # 이동 중 알 수 없는 오류 발생 시 종료
    #     print(f"❌ 다음 페이지로 이동 중 오류 발생: {e}")
    #     break

# 크롤링 종료 후 드라이버 닫기
driver.quit()
