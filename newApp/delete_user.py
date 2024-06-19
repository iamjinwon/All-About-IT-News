import os
import django
import sys

current_path = os.path.dirname(os.path.abspath(__file__))
project_path = os.path.join(current_path, '..')
sys.path.append(project_path)
os.chdir(project_path)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'newProject.settings')
django.setup()

from newApp.models import User

def delete_all_User():
    User.objects.all().delete()
    print("All news records have been deleted.")

if __name__ == "__main__":
    delete_all_User()