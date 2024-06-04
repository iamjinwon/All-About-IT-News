import sys
import logging
from crawling import crawling
from summarize_gpt import activate_gpt
import argparse
from apscheduler.schedulers.blocking import BlockingScheduler
import threading

def setup_logging():
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def main(crawl=True, activate=True):
    """
    Description:
        IT 뉴스의 Crawling을 실시한 후 GPT API를 사용하여 Summarize 해주는 함수
    Return: 
        crawling, activate_gpt 함수를 실행
    """
    try:
        if crawl:
            logging.info("크롤링 프로세스를 시작합니다.") 
            crawling()
        if activate:
            logging.info("GPT를 활용한 요약을 시작합니다.")
            activate_gpt()
    except Exception as e:
        logging.error(f"오류가 발생했습니다: {e}")
        sys.exit(1)

def stop_scheduler(scheduler):
    def shutdown():
        logging.info("스케줄러를 종료합니다.")
        scheduler.shutdown()
    threading.Thread(target=shutdown).start()

def schedule_jobs():
    scheduler = BlockingScheduler(timezone="Asia/Seoul")
    scheduler.add_job(main, 'cron', hour=4, minute=0)
    # scheduler.add_job(lambda: stop_scheduler(scheduler), 'cron', hour=18, minute=1)
    logging.info("스케줄러가 설정되었습니다. 매일 오전 4시에 작업이 실행됩니다.")
    scheduler.start()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="크롤링과 GPT 요약 활성화 프로세스 실행")
    parser.add_argument('--no-crawl', dest='crawl', action='store_false', help="크롤링 비활성화")
    parser.add_argument('--no-activate', dest='activate', action='store_false', help="GPT 요약 활성화 비활성화")
    args = parser.parse_args()

    setup_logging()
    # 스케줄러 작동 설정
    schedule_jobs() 