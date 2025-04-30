# 필요한 라이브러리 불러오기
import pymysql                      # MySQL 데이터베이스 연결용
import boto3                        # AWS S3 접근을 위한 라이브러리
from hashlib import sha256          # 파일명을 해싱하기 위한 라이브러리
from datetime import datetime       # 현재 시간 기록을 위한 라이브러리

#bucket_url = 'https://example-bucket.s3-region.amazonaws.com'
#bucket_url = 'example-bucket'

# 파일 확장자 추출 함수
def extract_extension(filename):
    return filename.split('.')[-1] if '.' in filename else ''

# S3 버킷에서 파일 목록 가져오기 함수
def get_s3_file_list(bucket_url):
    # S3 클라이언트 생성 (자격 증명 필요)
    s3_client = boto3.client(
        's3',
        aws_access_key_id = 'YOUR_AWS_ACCESS_KEY',                # AWS Access Key 입력
        aws_secret_access_key = 'YOUR_AWS_SECRET_KEY',            # AWS Secret Key 입력
        region_name = 'YOUR_REGION'                               # 리전 (예: ap-northeast-2)
    )
    
    # 버킷 이름을 URL에서 추출 (예: https://bucket-name.s3.region.amazonaws.com)
    bucket_name = bucket_url.split('//')[1].split('/')[0].split('.')[0]
    
    # S3에서 파일 목록 요청
    result = s3_client.list_objects_v2(Bucket=bucket_name)
    
    # 파일 목록 반환 (없으면 빈 리스트)
    if 'Contents' in result:
        return [content['Key'] for content in result['Contents']]
    else:
        return []

# ========== MySQL 데이터베이스 연결 ==========
conn = None
try:
    conn = pymysql.connect(
        host = 'YOUR_DB_HOST',           # DB 서버 주소
        user = 'YOUR_DB_USER',           # DB 사용자 이름
        password ='YOUR_DB_PASSWORD',    # DB 비밀번호
        database = 'YOUR_DB_NAME',       # 사용할 데이터베이스 이름
        charset='utf8mb4',               # 문자 인코딩
        autocommit=True                  # 자동 커밋 설정
    )

    with conn.cursor() as cursor:
        # buckets_test 테이블에서 모든 bucket_url 가져오기
        select_sql = """
            SELECT bucket_url FROM buckets_test
        """
        cursor.execute(select_sql)
        rows = cursor.fetchall()  # 결과 가져오기

        # documents 테이블에 삽입할 INSERT 쿼리 정의
        insert_sql = """
            INSERT INTO documents (
                file_name,
                url,
                extension,
                hash,
                date,
                bucket_url,
                file_size
            ) VALUES (%s, %s, %s, %s, %s, %s, %s)
        """

        # 각 bucket_url에 대해 반복 처리
        for row in rows:
            bucket_url = row[0]

            # 해당 버킷에서 파일 목록 가져오기
            file_list = get_s3_file_list(bucket_url)

            # 각 파일에 대해 DB에 정보 저장
            for file_name in file_list:
                extension = extract_extension(file_name)  # 확장자 추출
                file_hash = sha256(file_name.encode('utf-8')).hexdigest()  # 파일명 해싱
                url = f"{bucket_url}/{file_name}"  # 전체 URL 생성
                file_size = 0  # (필요 시 나중에 파일 사이즈 구현 가능)

                collected_at = datetime.now()  # 현재 시간 기록

                data = (
                    file_name,
                    url,
                    extension,
                    file_hash,
                    collected_at,
                    bucket_url,
                    file_size
                )

                cursor.execute(insert_sql, data)  # DB에 삽입

        print("✅ 모든 S3 파일 목록을 documents 테이블에 삽입 완료!")

# MySQL 관련 에러 발생 시 출력
except pymysql.MySQLError as e:
    print("❌ MySQL 에러:", e)

# 그 외 일반적인 에러 발생 시 출력
except Exception as e:
    print("❌ 일반 에러:", e)

# DB 연결 종료
finally:
    if conn:
        conn.close()
        print("🔒 DB 연결 종료.")
