#!/usr/bin/env python
# coding: utf-8

# In[ ]:

# from WebMailClass import WebMailClass
# from pyvirtualdisplay import Display


import re
import requests
import urllib.parse
import time
from bs4 import BeautifulSoup as soup
import random

from email.parser import HeaderParser
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


ua_strings = [
# EDGE
'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.140 Safari/537.36 Edge/17.17134',
'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.140 Safari/537.36 Edge/18.17763',
'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.132 Safari/537.36 Edg/80.0.361.66',
'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36 Edge/18.18363',
'Mozilla/5.0 (Windows NT 6.2; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36 Edge/15.15063',
'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/46.0.2486.0 Safari/537.36 Edge/13.10586',
'Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36 Edge/16.16299',
# CHROME
'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36',
'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.157 Safari/537.36',
'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36',
'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36',
'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.117 Safari/537.36',
'Mozilla/5.0 (Windows NT 6.2; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36',
'Mozilla/5.0 (Windows NT 6.2; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36',
# FIREFOX


]


#WebMailClass Usage:
#for example we have url and http_data
url='https://mail.pintoconstruction.com/owa/auth.owa'
logs_data='destination=https%3A%2F%2Fmail.pintoconstruction.com%2FOWA%2F&flags=0&forcedownlevel=0&trusted=0&username=irene.forlenza&password=irene&isUtf8=1'

socks_address='104.217.62.119'
socks_port=27471

#first method parse it:
# client, login, password = WebMailClass(socks_address,socks_port).LogsParser(logs_data,url)
# print(client, login, password)
#if your socks are OK output must be (True, 'irene.forlenza', 'irene')
#_________________________________
#next method -StartSession
#ATTENTION

#If you need to create sessionfor grabbing -  please  set True last argument - it turns on light version (easy to parse)
#url from logs



# ======================================================================
# LOGIN Part, create session
# ======================================================================

login = 'russell'
password = '5tgb6yhnBGT%NHY^'
url = 'https://remote.aegiforensics.com/owa/auth.owa'


login = 'rouellette'
password = '747123$'
url = 'https://autodiscover.bgcbc.org/owa/auth.owa'

headers = {
    # 'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:56.0) Gecko/20100101 Firefox/56.0 Waterfox/56.3',
    'User-Agent': random.choice(ua_strings),
    'Pragma': 'no-cache',
    'Cache-Control': 'no-cache',
    'Connection': 'keep-alive',
    'Accept-Language': 'en-US,en;q=0.5',
    'Accept': 'gzip, deflate, br',
}

proxies = {
    "http":"socks5://mechatron:MpvHdrApWq7YRgrFnBpduJQvrMcxsDE2@192.95.57.203:1550",
    "https":"socks5://mechatron:MpvHdrApWq7YRgrFnBpduJQvrMcxsDE2@192.95.57.203:1550"
}

my_session = requests.Session()

print("loading login page")
login_page = my_session.get(url, allow_redirects=True, headers=headers, proxies=proxies)


print("extracting login url values")
# extract some variables for proper url generations
a_sUrl = ''
a_sLgn = ''
for line in login_page.text.splitlines():
    if 'var a_sUrl' in line:
        spl = line.split('=')
        spl.pop(0)
        a_sUrl = '='.join(spl).replace("\"", '').replace("'",'').replace(';','').strip()

    if 'var a_sLgn' in line:
        spl = line.split('=')
        spl.pop(0)
        a_sLgn = '='.join(spl).replace("\"", '').replace("'",'').replace(';','').strip()

# generate proper url
new_url = login_page.url.split('logon.aspx')[0] + a_sLgn + a_sUrl

print("loading real login page")
# get login page from proper url
login_page2 = my_session.get(new_url, allow_redirects=True, headers=headers, proxies=proxies)

# process page to extract few necesseary items
my_soup = soup(login_page2.text, features="html.parser")

destination = ''
try:
    destination = my_soup.find('input', {'name': 'destination'}).get('value')
except:
    print(f"[E] destination:{e}")
    pass

# print(f"destination:{destination}")


# just cookies i set manually according to request analisys
my_session.cookies.set('cookieTest', '1')
my_session.cookies.set('PBack', '0')
my_session.cookies.set('tzid', 'Eastern Standard Time')

payload = {
    'destination': destination,
    'flags': '1', # 0 - full version (better for email send), 1 - lite version (better for grabbing)
    'forcedownlevel': '0',
    'trusted': '0',
    'username': login,
    'password': password,
    'isUtf8': '1'
}

print("send auth request")
inner_page = my_session.post(url, data=payload, allow_redirects=True, headers=headers, proxies=proxies)
# print(f"post answer:\r\n{inner_page.text}")


# ======================================================================
# Make POST request to view all folders in select->option tags
# ======================================================================
my_soup = soup(inner_page.text, features="html.parser")

if len(my_soup.select('a#lo')) < 1:
    raise Exception('Auth error, incorrect user or password')

# generate url params:
# https://autodiscover.bgcbc.org/owa/?ae=StartPage&id=LgAAAADNUv7o/RDXSI8oW9t2bdUdAQDKBdsUeOgMRY90RD16PTAtAAAAAQNJAAAB&slUsng=0&pg=1
# https://autodiscover.bgcbc.org/owa/?ae=StartPage&id=LgAAAADNUv7o/RDXSI8oW9t2bdUdAQDKBdsUeOgMRY90RD16PTAtAAAAAQNJAAAB&slUsng=0&pg=1
all_folders_url = inner_page.url

a_sAe = "StartPage";
a_sT = "";
a_sFldId = "";
a_sPg = "1";
a_iSlUsng = 0;

for line in inner_page.text.splitlines():
    if 'var a_sAe' in line:
        spl = line.split('=')
        spl.pop(0)
        a_sAe = '='.join(spl).replace("\"", '').replace("'",'').replace(';','').strip()

    elif 'var a_sT' in line:
        spl = line.split('=')
        spl.pop(0)
        a_sT = '='.join(spl).replace("\"", '').replace("'",'').replace(';','').strip()

    elif 'var a_sFldId' in line:
        spl = line.split('=')
        spl.pop(0)
        a_sFldId = '='.join(spl).replace("\"", '').replace("'",'').replace(';','').strip()

    elif 'var a_sPg' in line:
        spl = line.split('=')
        spl.pop(0)
        a_sPg = '='.join(spl).replace("\"", '').replace("'",'').replace(';','').strip()

    elif 'var a_iSlUsng' in line:
        spl = line.split('=')
        spl.pop(0)
        a_iSlUsng = '='.join(spl).replace("\"", '').replace("'",'').replace(';','').strip()


all_folders_url = f"{all_folders_url}?ae={a_sAe}&id={a_sFldId}&slUsng={a_iSlUsng}&pg={a_sPg}"
if a_sT:
    all_folders_url += f"&t={a_sT}"

payload = {
    'hidpnst': my_soup.find('input', {'name': 'hidpnst'}).get('value'),
    'hidactbrfld': '1',
    # 'hidmtgmsg': my_soup.find('input', {'name': 'hidmtgmsg'}).get('value'),
    'hidcmdpst': '',
    'hidcid': '',
    'hidso': '',
    'hidpid': my_soup.find('input', {'name': 'hidpid'}).get('value'),
    'hidcanary': my_soup.find('input', {'name': 'hidcanary'}).get('value'),
}

# print(f"all_folders_url:{all_folders_url}")
# print(f"payload:{payload}")

print("show all folders request")
all_folders_page = my_session.post(all_folders_url, data=payload, allow_redirects=True, headers=headers, proxies=proxies)

# print(f"all_folders_page:\r\n{all_folders_page.text}")

my_soup = soup(all_folders_page.text, features="html.parser")

folders = []
for option in my_soup.select("select#selbrfld option"):
    # print(item.get_text())
    f_title = option.get('title')
    f_id = option.get('value')
    folders.append({f_title:f_id, 'name': f_title, 'id': f_id})
    # print(f"option[{f_title}]: {f_id}")

# ======================================================================
# Make GET request to view all pages of certain folder
# ======================================================================
print(f"show folder:{folders[0]}")

folder_url = all_folders_url.split('/owa')[0] + f'/owa?ae=Folder&t={folders[0]["id"]}'
folder_page = my_session.get(folder_url, allow_redirects=True, headers=headers, proxies=proxies)

# search last page of folder
pages = 1

my_soup = soup(folder_page.text, features="html.parser")

for link in my_soup.select("a#lnkLstPg"):
    page_data = link.get('onclick')
    print(f"page_data:{page_data}")
    pages_arr = re.findall('\d+', page_data)
    if len(pages_arr):
        pages = int(pages_arr[0])


# canary stays same for all pages during current session i guess
url_get_header_params_dict = {
   'oeh':'1',
   'ns':'ReadMessage',
   'ev':'LMD',
   'canary': my_soup.find('input', {'name': 'hidcanary'}).get('value'),
}

url_get_header_params = ""
for key, val_raw in url_get_header_params_dict.items():
    # process value proper encoding
    # val = re.sub('/', '%2f', val_raw)
    # val = val.replace("+","%2b")

    val = re.sub('/', '%252f', val_raw)
    val = val.replace("+","%252b")
    url_get_header_params += f"&{key}={val}"

# generate all urls for current page
# FIXME: remove as soon as testing is done
pages = 1

mail_urls = []
for page_num in range(1, pages+1):
    print(f'Start parse {page_num} page..')

    # generate proper url
    folder_nth_page_url = f"{folder_url}&pg={page_num}"

    # get nth page
    folder_nth_page = my_session.get(folder_nth_page_url, allow_redirects=True, headers=headers, proxies=proxies)

    # parse page
    my_soup = soup(folder_nth_page.text, features="html.parser")

    for input_tag in my_soup.select('table.lvw input[name=chkmsg]'):
        msg_id = input_tag.get('value')

        msg_id_fmt_body = re.sub('/', '%2f', msg_id)
        msg_id_fmt_body = msg_id_fmt_body.replace("+","%2b")
        mail_url = folder_nth_page_url.split('/owa')[0] + f"/owa/?ae=Item&t=IPM.Note&id={msg_id_fmt_body}"

        msg_id_fmt_head = re.sub('/', '%252f', msg_id)
        msg_id_fmt_head = msg_id_fmt_head.replace("+","%252b")
        mail_headers_url = folder_nth_page_url.split(f'/owa')[0] + f'/owa/ev.owa?Id=id%3d{msg_id_fmt_head}{url_get_header_params}'

        # print(f"mail_url: {mail_url}")
        # print(f"mail_headers_url: {mail_headers_url}")

        mail_urls.append({'id':msg_id
            ,'header':mail_headers_url
            ,'body':mail_url
        })


# ======================================================================
# Make GET request to get headers from textarea
# ======================================================================
mail_headers_url = mail_urls[0]['header']

print(f'get headers for first mail')
mail_headers_page = my_session.get(mail_headers_url, allow_redirects=True, headers=headers, proxies=proxies)
my_soup = soup(mail_headers_page.text, features="html.parser")
headers_raw = my_soup.select('textarea')[0].encode_contents()

print(f"headers_raw:{headers_raw}")

# ======================================================================
# Make GET request to get body content
# ======================================================================
mail_body_url = mail_urls[0]['body']

print(f'get body for first mail')
mail_body_page = my_session.get(mail_body_url, allow_redirects=True, headers=headers, proxies=proxies)
my_soup = soup(mail_body_page.text, features="html.parser")
body_raw = my_soup.select('td.bdy div.bdy')[0].encode_contents()


# print(f"body_raw:{body_raw}")

# ======================================================================
# Generate email object for futher parsing
# ======================================================================

print(f'generate message')
# create header object for futher ease of use
headers_raw_str = headers_raw.decode('utf-8')
h = HeaderParser().parsestr(text=headers_raw_str)
msg = MIMEMultipart()
msg.set_charset("utf-8")
# update all headers for message item
for k,v in h.items():
    if str(k).lower() not in ('Content-Type', 'Content-Transfer-Encoding'):
        msg[str(k)] = str(v)

body_tpl = f'<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">\r\n<html xmlns="http://www.w3.org/1999/xhtml">\r\n<head>\r\n<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />\r\n<title>{msg["Subject"]}</title>\r\n</head>\r\n</head>\r\n<body>{body_raw.decode("utf-8")}</body>\r\n</html>'
# append body
msg.attach(MIMEText(body_tpl, 'html', 'utf-8'))

print(f'formed message:\r\b{msg.as_string()}')
# import email

# body_raw_postfix = b'</body>\r\n</html>'
# msg = email.message_from_bytes(headers_raw + body_raw_prefix + body_raw + body_raw_postfix)


# write message
# https://autodiscover.bgcbc.org/owa/?ae=Item&a=New&t=IPM.Note&cc=MTQuMy4zOTkuMCxlbi1VUyw0Mjk0OTY3Mjk1LEhUTUwsMCww&pspid=_1586450266382_189004436


# reply url:
# id="bRgAAAADNUv7o/RDXSI8oW9t2bdUdBwDKBdsUeOgMRY90RD16PTAtAAAAAQNJAACVKImFHe+SRqAp+1jSmrWUAAFjvJKjAAAJ"
# https://autodiscover.bgcbc.org/owa/?ae=PreFormAction&a=Reply&t=IPM.Note&id=RgAAAADNUv7o%2fRDXSI8oW9t2bdUdBwDKBdsUeOgMRY90RD16PTAtAAAAAQNJAACVKImFHe%2bSRqAp%2b1jSmrWUAAFjvJKjAAAJ&pspid=_1586775476163_540497660
# new message
# https://autodiscover.bgcbc.org/owa/?ae=Item&a=New&t=IPM.Note&cc=MTQuMy4zOTkuMCxlbi1VUyw0Mjk0OTY3Mjk1LEhUTUwsMCww&pspid=_1586775476163_540497666

# # #Let's start to grab emails

# session=WebMailClass(socks_address, socks_port).StartSession(login, password, url, True)
# mails=WebMailClass(socks_address, socks_port).WebMailGrabber(session)

# # #mails = [{id:id,body:body,header:header}]


# If you need to send an answer - set False grabber mode put body answer and id and attachment path
# session = WebMailClass(socks_address, socks_port).StartSession(login, password, url ,False)
# WebMailClass(socks_address, socks_port).SendEmail(
#     driver=session,
#     letter_id=None,
#     answer_body='my milkshake brings all the boys in the yard',
#     report_flag=False,
#     remove_sent_flag=True,
#     attachment=None,
#     subject=None,
#     send_to=None
#     # session,'RgAAAAAQerHOjuyBRr2HcvxEqbzFBwDW+5uMZs37Q5oumjN9rvtWAAAAEeLVAACZXIgohX82T40iCFX4jLugAAeK2krvAAAJ','ok',True,True,attachment=False
# )



