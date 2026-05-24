#!/usr/bin/env python
import os
import sys


def main():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ezware.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Không import được Django. Kiểm tra lại đã cài đặt chưa hoặc đã kích hoạt venv chưa?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
