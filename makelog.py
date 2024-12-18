import logging

# 로그 설정
logging.basicConfig(filename="app.log", level=logging.INFO, format="%(asctime)s - %(message)s")

# 로그 작성
logging.info("This is an info log")
logging.warning("This is a warning log")
logging.error("This is an error log")
