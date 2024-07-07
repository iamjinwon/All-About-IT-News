import os
import subprocess
import getpass

def run_command(command):
    result = subprocess.run(command, shell=True, check=True)
    if result.returncode != 0:
        raise Exception(f"Command failed: {command}")

def create_env_file():
    db_name = input("Enter your database name: ")
    db_user = input("Enter your database user: ")
    db_password = getpass.getpass("Enter your database password: ")
    db_host = input("Enter your database host (default: localhost): ") or "localhost"
    db_port = input("Enter your database port (default: 3306): ") or "3306"
    openai_api_key = input("Enter your OpenAI API key: ")

    with open(".env", "w") as f:
        f.write(f"DB_NAME={db_name}\n")
        f.write(f"DB_USER={db_user}\n")
        f.write(f"DB_PASSWORD={db_password}\n")
        f.write(f"DB_HOST={db_host}\n")
        f.write(f"DB_PORT={db_port}\n")
        f.write(f"OPENAI_API_KEY={openai_api_key}\n")

def main():
    # Install MySQL server and client
    run_command("sudo apt-get install -y mysql-server")
    run_command("sudo mysql_secure_installation")

    run_command("sudo apt-get install -y pkg-config libmysqlclient-dev")
    run_command("sudo apt-get install -y build-essential")
    run_command("sudo apt-get install -y python3-dev")

    # Create .env file
    create_env_file()

    # Django migrations
    run_command("python manage.py makemigrations")
    run_command("python manage.py migrate")

    print("Setup complete. You can now run the server using `python manage.py runserver`.")

if __name__ == "__main__":
    main()
