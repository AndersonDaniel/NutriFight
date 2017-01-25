from data import application
import os

APP_ROOT = os.path.dirname(os.path.abspath(__file__))

if __name__ == '__main__':
    # Run!
    application.run('0.0.0.0')
