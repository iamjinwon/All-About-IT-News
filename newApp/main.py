import sys
import logging
from crawling import crawling
from featured_articles import update_crucial_articles
from summarize_gpt import summarize_articles
from html_send_email import send_email_with_attachment
import argparse
from apscheduler.schedulers.blocking import BlockingScheduler

def setup_logging():
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def main(crawl=True, update=True, summarize=True, send_email=True):
    """
    Description:
        IT 뉴스의 Crawling을 실시한 후 중요한 기사를 식별하고, GPT API를 사용하여 Summarize 하는 함수
    Return: 
        crawling, update_crucial_articles, summarize_articles, send_email_with_attachment 함수를 실행
    """
    try:
        if crawl:
            logging.info("크롤링 프로세스를 시작합니다.") 
            crawling()
        if update:
            logging.info("중요 기사를 식별하는 프로세스를 시작합니다.")
            update_crucial_articles()
        if summarize:
            logging.info("GPT를 활용한 요약을 시작합니다.")
            summarize_articles()
        if send_email:
            logging.info("HTML 이메일을 생성하고 발송합니다.")
            send_email_with_attachment()
    except Exception as e:
        logging.error(f"오류가 발생했습니다: {e}")
        sys.exit(1)

# def stop_scheduler(scheduler):
#     def shutdown():
#         logging.info("스케줄러를 종료합니다.")
#         scheduler.shutdown()
#     threading.Thread(target=shutdown).start()

def schedule_jobs():
    scheduler = BlockingScheduler(timezone="Asia/Seoul")
    scheduler.add_job(main, 'cron', hour=15, minute=27)
    # scheduler.add_job(lambda: stop_scheduler(scheduler), 'cron', hour=18, minute=1)
    logging.info("스케줄러가 설정되었습니다. 매일 오후 3시 29분에 작업이 실행됩니다.")
    scheduler.start()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="크롤링과 GPT 요약 및 이메일 전송 활성화 프로세스 실행")
    parser.add_argument('--no-crawl', dest='crawl', action='store_false', help="크롤링 비활성화")
    parser.add_argument('--no-update', dest='update', action='store_false', help="중요 기사 식별 비활성화")
    parser.add_argument('--no-summarize', dest='summarize', action='store_false', help="GPT 요약 비활성화")
    parser.add_argument('--no-email', dest='send_email', action='store_false', help="이메일 전송 비활성화")
    args = parser.parse_args()

    setup_logging()
    schedule_jobs()
