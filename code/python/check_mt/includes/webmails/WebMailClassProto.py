#!/usr/bin/env python
# coding: utf-8

# In[1]:


from pyvirtualdisplay import Display
import urllib.request
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
from selenium.webdriver.chrome.options import Options
import re
import requests
import socks
import socket
from urllib.parse import urlparse
import asyncio
from concurrent.futures import ThreadPoolExecutor
from timeit import default_timer
import os
import nest_asyncio
from bs4 import BeautifulSoup as soup

#important shit for async funcs
nest_asyncio.apply()
display = Display(visible=0, size=(1440, 900))

class WebMailClass():

    def __init__(self,socks_address,socks_port):
        self.socks_address=socks_address
        self.socks_port=socks_port
        if not display.is_started:
            display.start()


    def LogsParser(self, logs_data, logs_url):
        return False, None, None

    def StartSession(self, webmail_login, webmail_password, webmail_url,grabber_mode):
        url_parsed = webmail_url
        profile = webdriver.FirefoxProfile()
        profile.set_preference("network.proxy.type", 1)
        profile.set_preference("network.proxy.socks", self.socks_address)
        profile.set_preference("network.proxy.socks_port", self.socks_port)
        profile.set_preference("network.proxy.socks_version", 5)
        profile.update_preferences()

        #start browsing and open url
        driver = webdriver.Firefox(firefox_profile=profile)
        timeout=30
        driver.get(url_parsed)
        time.sleep(5)
        try:
            element_present = EC.presence_of_element_located((By.NAME, 'username'))
            WebDriverWait(driver, timeout).until(element_present)
        except TimeoutException:
            print("Timed out waiting for page to load")
        return driver

    def fetch(self,session, urls):
        pass

    #funcs makes async fetch func apply
    async def get_data_asynchronous(self,norm_session, urls_headers):
        pass

    def WebMailGrabber(self, driver):
        self.hdrs=[]
        return self.hdrs

    #disable conversation view - cause it obscures scrapping
    def view_conversation_disabler(self,driver):
        pass

    def alerts_closer(self,driver):
        pass

    #send email method
    def SendEmail(self,driver, letter_id,answer_body,report_flag,remove_sent_flag,attachment):
        pass
