import os
import sys

def main():
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.dev")  # Nếu muốn phát triển dùng `dev.py`
    # os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.prod")  # Nếu chạy ở môi trường sản xuất
    from django.core.management import execute_from_command_line
    execute_from_command_line(sys.argv)

if __name__ == "__main__":
    main()