#!/usr/bin/env python
import os
from os.path import abspath, dirname
import sys

if __name__ == "__main__":
    project_dir = abspath(dirname(dirname(__file__)))
    sys.path.insert(0, project_dir)
    os.environ['DJANGO_SETTINGS_MODULE'] = "bookingCalPython.settings"    

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)