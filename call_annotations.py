import subprocess
import time
from selenium_test import browser_driver
import requests

url = "http://127.0.0.1:5000/static/gui.html?tree=example"

def start_flask():
    script_name = "annotations.py"
    subprocess.Popen(['nohup', 'python', 'annotations.py'],
                #  stdout=open('/dev/null', 'w'),
                #  stderr=open('logfile.log', 'a'),
                #  preexec_fn=os.setpgrp
                 )
    return 

def end_flask():
    requests.get('http://localhost:5000/shutdown')
    return

start_flask()

browser_driver(url)

time.sleep(0.5)

#print("quit")
end_flask()