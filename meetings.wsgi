import os
import sys


activate_this = 'env/bin/activate'
with open(activate_this) as file_:
    exec(file_.read(), dict(__file__=activate_this))

sys.path.insert(0, os.path.join(os.path.dirname(os.path.realpath(__file__)), '../..'))

sys.path.append('/mnt/c/Users/email/Desktop/UO/cs322/proj10-scheduler/')

from proj10-scheduler.flask_main import app as application