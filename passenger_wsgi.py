import os
import sys

# Add the project directory to sys.path
sys.path.insert(0, os.path.dirname(__file__))

# Set the Django settings module
os.environ['DJANGO_SETTINGS_MODULE'] = 'ubmis_project.settings'

# Import the Django WSGI application
from ubmis_project.wsgi import application
