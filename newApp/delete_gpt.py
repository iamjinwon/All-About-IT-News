import os
import django
import sys

# 현재 작업 디렉토리를 프로젝트 루트 디렉토리로 설정
current_path = os.path.dirname(os.path.abspath(__file__))
project_path = os.path.join(current_path, '..')
sys.path.append(project_path)
os.chdir(project_path)

# Django settings 설정
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'newProject.settings')
django.setup()

from newApp.models import Gpt

def delete_all_gpts():
    Gpt.objects.all().delete()
    print("All Gpt records have been deleted.")

if __name__ == "__main__":
    delete_all_gpts()
