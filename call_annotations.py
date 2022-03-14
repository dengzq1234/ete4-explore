import subprocess
import time
url = "http://127.0.0.1:5000/static/gui.html?tree=example"
def start_flask():
    script_name = "annotations.py"
    subprocess.Popen(['nohup', 'python', 'annotations.py'],
                #  stdout=open('/dev/null', 'w'),
                #  stderr=open('logfile.log', 'a'),
                #  preexec_fn=os.setpgrp
                 )

start_flask()

from selenium_test import browser_driver
browser_driver(url)

#time.sleep(2)
import requests
requests.get('http://127.0.0.1:5000/shutdown')