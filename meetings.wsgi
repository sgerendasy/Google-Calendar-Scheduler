import os
import sys


activate_this = 'env/bin/activate'
with open(activate_this) as file_:
    exec(file_.read(), dict(__file__=activate_this))


from proj10-scheduler.flask_main import app as application