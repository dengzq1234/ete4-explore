from selenium import webdriver
from selenium.common import exceptions # selenium异常模块
from selenium.webdriver.common.action_chains import ActionChains
import time
def browser_driver(url):
    options = webdriver.FirefoxOptions()
    options.add_argument('--headless')
    options.set_preference("browser.download.folderList", 2)
    options.set_preference("browser.download.manager.showWhenStarting", False)
    options.set_preference("browser.download.dir", "/home/deng/Projects/ete4/hackathon/metadata_annotation")

    browser_driver = webdriver.Firefox(
            executable_path=r"/home/deng/FireFox/geckodriver",  # 这里必须要是绝对路径
            # windows是.exe文件 xxx/xxx/geckodriver.exe, xxx/xxx/firefox.exe
            # linux直接是xxx/xxx/geckodriver, xxx/xxx/firefox
            #firefox_binary=r"/home/deng/FireFox/firefox",
            options=options)
    try:
        #url = r'https://www.google.com/
        browser_driver.get(url)
        #print ('当前爬取的网页url为:{0}'.format(browser_driver.current_url)) 
        #print(browser_driver.find_element_by_id('div_tree').get_attribute('innerHTML'))
        time.sleep(0.5)
        actions = ActionChains(browser_driver)
        actions.send_keys('d')
        actions.perform()
        print("downloaded")

        # click from control panel
        # time.sleep(3)
        # element = browser_driver.find_element_by_class_name('sidenav-open')
        # element.click()
        # download_button = browser_driver.find_element_by_id('sidenav').find_element_by_xpath('//button[normalize-space()="Download"]')
        # download_button.click()
        # if download_button.is_displayed():
        #     svg_button = browser_driver.find_element_by_id('sidenav').find_element_by_xpath('//button[normalize-space()="svg"]')
        #     svg_button.click()
        # newick_button.location_once_scrolled_into_view
        # newick_button.click()
        #print(browser_driver.find_element_by_id('sidenav').find_element_by_xpath('//button[normalize-space()="newick"]').tag_name)
        #print(browser_driver.find_element_by_xpath('//button[normalize-space()="Control panel"]').text)
        #print(browser_driver.find_elements_by_class_name('tp-btnv_b')[0])
        #print ('当前爬取网页内容为：\n {0}'.format(browser_driver.find_element_by_id('json').text))

    finally:
        time.sleep(0.5)
        #browser_driver.quit()

if __name__ == '__main__':
    #url = r'http://127.0.0.1:5000/trees/0/newick'
    url = r'http://127.0.0.1:5000/static/gui.html?tree=example'
    browser_driver(url)