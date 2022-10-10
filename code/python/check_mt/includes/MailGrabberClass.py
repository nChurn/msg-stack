from multiprocessing import Lock, Process, Queue, current_process, Pipe
import datetime
import traceback
# network related
import getpass, poplib, imaplib, socks, socket

from includes.IMAP4Socks import MYIMAP4, MYIMAP4_SSL
from includes.POP3Socks import MYPOP3, MYPOP3_SSL
from includes.ProtocolErrors import retry_list, socket_errors, auth_error_list


# email parsers
import email # new statement
import json

from email.header import decode_header
from email.utils import parsedate_tz, mktime_tz, formatdate, getaddresses, parseaddr
import base64
import re
import time
import ssl
# https://stackoverflow.com/a/32150698
# some shitty mail servers stores data a bit incorrect
# set max line to 200kBytes
poplib._MAXLINE=204800

from includes.RootLogger import rootLogger


# valid_email_re = re.compile('([a-z0-9-._]*)\@([a-z0-9-._]*)\.([a-z]{2,5})', re.IGNORECASE )
# https://regex101.com/r/wRIVUy/1
valid_email_re = re.compile("^(?:[a-z0-9!#$%&'*+\/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+\/=?^_`{|}~-]+)*|\"(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21\x23-\x5b\x5d-\x7f ]|\\[\x01-\x09\x0b\x0c\x0e-\x7f ])*\")[\#\%\+\@](?:(?:[a-z0-9](?:[a-z0-9-_]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-_]*[a-z0-9])?|\[(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?|[a-z0-9-_]*[a-z0-9]:(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21-\x5a\x53-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])+)\])$", re.IGNORECASE)
extraxt_email_re = re.compile("(?:[a-z0-9!#$%&'*+\/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+\/=?^_`{|}~-]+)*|\"(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21\x23-\x5b\x5d-\x7f ]|\\[\x01-\x09\x0b\x0c\x0e-\x7f ])*\")[\#\%\+\@](?:(?:[a-z0-9](?:[a-z0-9-_]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-_]*[a-z0-9])?|\[(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?|[a-z0-9-_]*[a-z0-9]:(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21-\x5a\x53-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])+)\])", re.IGNORECASE)
valid_ctype_re = re.compile('text\/(plain|html)')
mail_folder_re = re.compile('(.+)\s((\"|\')(.)(\"|\'))\s((\"|\')?(.+)(\"|\')?)', re.IGNORECASE )
re_quotes_start = re.compile("^\".+$", re.IGNORECASE)
re_quotes_end = re.compile(".+\".+$", re.IGNORECASE)

skip_errors = ('expunged', 'no such message', 'message corrupted', 'unable to open that message', 'deleted', "can't open the message", 'no such blob')

class CommonMailProcessor():
    """docstring for CommonMailProcessor"""
    def __init__(self, account, socks_creds={}, ssl_context=None, prefix=''):
        self.account = account
        self.socks_creds = socks_creds
        self.server = None
        self.prefix = prefix
        self.ssl_context = ssl_context

    # get all emails
    def extractEmails(self, message):
        ret_list = []
        tos = message.get_all('to', [])
        ccs = message.get_all('cc', [])
        bcs = message.get_all('bcc', [])
        froms = message.get_all('from', [])
        resent_tos = message.get_all('resent-to', [])
        resent_ccs = message.get_all('resent-cc', [])

        # get addresses not always do it's job well, sometimes because email servers are dumb fuck shit or because authors are also lazy gays
        # all_mails = getaddresses(tos + ccs + bcs + froms + resent_tos + resent_ccs)

        # rootLogger.info(f"{self.prefix}extractEmails all_mails:{all_mails}")
        all_containers = tos + ccs + bcs + froms + resent_tos + resent_ccs
        # rootLogger.info(f"{self.prefix}extractEmails all_mails:{all_containers}")
        for container in all_containers:
            # we will get some string like: "hamamatu (hamamatu@tradetrust.co.jp)" <hamamatu@tradetrust.co.jp>,\r\n\t"sizuoka (sizuoka@tradetrust.co.jp)" <sizuoka@tradetrust.co.jp>, "numazu_i\r\n (numazu_i@tradetrust.co.jp)" <numazu_i@tradetrust.co.jp>, "numazu\r\n (numazu@tradetrust.co.jp)" <numazu@tradetrust.co.jp>
            # split by comma
            splitted = []
            try:
                # splitted = re.split('\,',container)
                # remove empty spaces
                splitted = [item.strip() for item in re.split('\,',container)]

                for index, item in enumerate(splitted):
                    # check if item has quotes, then move it to next item untill found another quotes
                    if re_quotes_start.match(item) and re_quotes_end.match(item) is None:
                        splitted[index+1] = f"{item}, {splitted[index+1]}"
                        # clear current item
                        splitted[index] = ""

                splitted = [item for item in splitted if len(item) > 0]

            except Exception as e:
                rootLogger.error(f"{self.prefix}extractEmails: can't split container:[{type(container)}]{container} ({e})")

            for item in splitted:
                # remove any whitespaces at the beginning and end of string
                item = item.strip()
                # skip empty strings
                if len(item) < 1:
                    continue
                # extract email, search for whitespace: "hamamatu (hamamatu@tradetrust.co.jp)" <hamamatu@tradetrust.co.jp>
                founds = re.findall(extraxt_email_re, item)
                if len(founds) == 0:
                    rootLogger.info(f"{self.prefix}extractEmails:No valid email in string:\n{item}\n{all_containers}")
                    continue

                email = founds[-1]

                # not sure if needed at all
                validated_mail = self.validateEmailAddress(email)
                if validated_mail is None:
                    rootLogger.info(f"{self.prefix}extractEmails:Invalid email:\n{item}")
                    rootLogger.info(f"{self.prefix}extractEmails:Invalid email detailed data:{container}")
                    continue

                holder = "".join(item.rsplit(email, 1)).replace('<>', "").replace("\"", "").replace("\'","").strip()
                record = {"holder": holder, "mail": validated_mail}

                # now attempt to translate holder's name if necesseary
                holder_decoded = decode_header(holder)[0]
                if holder_decoded[1] is not None:
                    try:
                        # remove quotes once again
                        # record['holder'] = holder_decoded[0].decode(holder_decoded[1]).replace("\"", "").replace("\'","").strip()
                        record['holder'] = holder_decoded[0].decode(holder_decoded[1], 'ignore').replace("\"", "").replace("\'","").strip()
                    except Exception as e:
                        # raise e
                        rootLogger.error(f"{prefix}extractEmails:Decode error:\n{e}\n{holder_decoded}")
                        record['holder'] = item[0]

                ret_list.append(record)

        return ret_list

    def getMailDateTime(self, message_headers, mail_dump=None):
        try:
            date_str = message_headers['Date']
            if date_str == '' or date_str is None:
                raise ValueError("date_str is empty or None")

            # https://stackoverflow.com/a/12160056
            time_tuple = parsedate_tz(date_str)

            if time_tuple is None:
                d = datetime.datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S %z')
            else:
                d = datetime.datetime(*(time_tuple[0:6]))

        except Exception as e:
            rootLogger.error(f"{self.prefix}getMailDateTime:{e}")
            if mail_dump is None:
                d = datetime.datetime.utcnow() - datetime.timedelta(hours=8)
            else:
                d = mail_dump.mail_date

        return d

    def getMailHeaders(self, message, must_have_headers = {"From": "", "To": "", "Subject": "", "Date": ""}):
        headers_dict = {}
        try:
            # items return tuples of header type
            for (hkey, hvalue) in message.items():
                headers_dict[str(hkey)] = str(hvalue)

        except Exception as e:
            rootLogger.error(f"{self.prefix}getMailHeaders:{e}")
            pass

        # must have headers processing
        for hd_key in headers_dict.keys():
            for mhh_key in must_have_headers:
                # check if DATE instead of Date etc
                # if mhh_key.lower() == hd_key.lower() and mhh_key != hd_key:
                if mhh_key.lower() == hd_key.lower():
                    # headers_dict[mhh_key] = headers_dict[hd_key]
                    must_have_headers[mhh_key] = headers_dict[hd_key]

        # now that must_have_headers are completely finnished, mowe theese keys to headers_dict
        for mhh_key in must_have_headers:
            headers_dict[mhh_key] = must_have_headers[mhh_key]

        return headers_dict

    def getMailBody(self, message, save_attaches=False):
        attachments = []
        filepath = ""
        body = ""

        no_name_counter = 1
        # process body
        if message.is_multipart():
            prev_ctype = ""
            for part in message.walk():
                ctype = part.get_content_type()
                cdispo = str(part.get('Content-Disposition'))
                cte = str(part.get('Content-Transfer-Encoding'))

                # skip any text/plain (txt) attachments
                if re.match(valid_ctype_re, ctype) and 'attachment' not in cdispo:
                    body_part = part.get_payload(decode=True)
                    if type(body_part) is bytes:
                        body_part = body_part.decode('utf8', 'ignore')

                    # override if we got html and previous was not
                    if "html" not in prev_ctype and "html" in ctype:
                        body = body_part
                    else:
                        body += body_part
                    prev_ctype = ctype
                    continue

                # download file
                filename = part.get_filename()
                if not(filename):
                    filename = "no-name-attach-%d" % no_name_counter
                    no_name_counter += 1

                filedata = part.get_payload(decode=False)
                attachments.append( {"filename": filename, "path": ""} )

        # not multipart - i.e. plain text, no attachments, keeping fingers crossed
        else:
            # determine if base64 etc -> set decoded to True
            body = message.get_payload(decode=True)

        # transform to string if needed
        if type(body) is bytes:
            body = body.decode('utf8', 'ignore')


        return (body, attachments)

    # make small validations for email addresses
    def validateEmailAddress(self, common_login, common_host=""):
        # rootLogger.info(type(common_login))
        common_login = common_login.strip().replace('"','').replace("'",'').replace('`','')
        # if email is allready valid, no reason for futher actions
        if re.match(valid_email_re, common_login) is not None:
            return common_login

        # check if we got some dumb fuck values instead of @ => #, %,+
        match = re.search(r'\S+(\#|\%|\+)\S+\.\S+', common_login)
        # avoid replacing # in holder_area
        if match is not None and "@" not in common_login:
            rootLogger.info(f"{self.prefix}Found shitty mail acc:" + common_login)
            common_login = re.sub(r'(\#|\%|\+)', '@', common_login)

        # also remove aly pop3. smtp. from address leaving only 1 and 2 domain levels for host
        if "@" not in common_login:
            if len(common_host) > 0:
                splitted = re.split(r'(smtp(\d+)?\.|pop(\d+)?\.|imap(\d+)?\.)', common_host)
                if len(splitted) > 0:
                    # save only 2nd level domain
                    spl = splitted[-1]
                    if len( spl ) > 1:
                        spl2 = ".".join(spl.split('.')[-2:])
                    else:
                        spl2 = spl[0]
                    common_login = f"{common_login}@{spl2}"
                else:
                    common_login = f"{common_login}@{common_host}"

            else:
                return None

        common_login = common_login.strip()

        # at last if we got login@ip instead of login@dom2.dom1 -> also skip
        if not re.match(valid_email_re, common_login):
            common_login = None

        return common_login


class POP3MailProcessor(CommonMailProcessor):
    """docstring for POP3MailProcessor"""
    def __init__(self, account, socks_creds={}, ssl_context=None, prefix='' ):
        super().__init__(account, socks_creds, ssl_context, prefix)
        self.mail_host = account.pop3_host
        self.mail_port = account.pop3_port
        self.mail_user = account.pop3_login
        self.mail_password = account.pop3_password
        self.force_ssl = account.imap_ssl
        rootLogger.info(f"{self.prefix}Inited {self.mail_user}:{self.mail_password}@{self.mail_host}:{self.mail_port}")

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, type, value, traceback):
        self.close()

    def connect(self):
        server = None
        rootLogger.info(f"{self.prefix}force_ssl is:{self.force_ssl}")

        # try:
        if self.force_ssl:
            if self.ssl_context is None:
                rootLogger.info(f"{self.prefix}Selected pure SSL/TLS connection")
                server = MYPOP3_SSL(host=self.mail_host,
                            port=self.mail_port,
                            timeout=60,
                            socks_creds=self.socks_creds)
            else:
                rootLogger.info(f"{self.prefix}Selected self signed SSL/TLS connection:{self.ssl_context}")
                server = MYPOP3_SSL(host=self.mail_host,
                            port=self.mail_port,
                            timeout=60,
                            socks_creds=self.socks_creds,
                            context=self.ssl_context)
        else:
            rootLogger.info(f"{self.prefix}Selected plain/text connection")
            server = MYPOP3(host=self.mail_host,
                            port=self.mail_port,
                            timeout=60,
                            socks_creds=self.socks_creds)

        server.user(self.mail_user)
        server.pass_(self.mail_password)
        self.server = server

    def close(self):
        if self.server is not None:
            try:
                self.server.quit()
            except Exception as e:
                rootLogger.error(f"{self.prefix}Error closing server:{e}")

    def getFolders(self):
        # need this anyway
        return ["INBOX"]

    def getMessagesList(self):
        (numMsgs, totalSize) = self.server.stat()
        rootLogger.info(f"{self.prefix}Total messages:{numMsgs} of total size:{totalSize}")
        return (numMsgs, totalSize, [])

    def getMessage(self, msg_num, headers_only=False, get_raw=False ):
        rootLogger.info(f"{self.prefix}Get message:{msg_num} headers_only:{headers_only}")
        message = None
        # try:
        if headers_only:
            (response, resp_body, octets) = self.server.top(msg_num, 0)
        else:
            (response, resp_body, octets) = self.server.retr(msg_num)

        if get_raw:
            message = resp_body
        else:
            message = email.message_from_bytes(b'\r\n'.join(resp_body))

        return message

    # actually Imap feature only, need just to emulate and make API same
    def selectFolder(self, folder_name):
        msg_list = self.getMessagesList()
        if len( msg_list ) > 0:
            rootLogger.info(f'msg_list:{msg_list}')
            return msg_list[0]
        else:
            return 0


class IMAPMailProcessor(CommonMailProcessor):
    """docstring for POP3MailProcessor"""
    def __init__(self, account, socks_creds={}, ssl_context=None, prefix='' ):
        super().__init__(account, socks_creds, ssl_context, prefix)
        self.mail_host = account.imap_host
        self.mail_port = account.imap_port
        self.mail_user = account.imap_login
        self.mail_password = account.imap_password
        self.force_ssl = account.imap_ssl
        rootLogger.info(f"{self.prefix}Inited {self.mail_user}:{self.mail_password}@{self.mail_host}:{self.mail_port}")

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, type, value, traceback):
        self.close()

    def connect(self):
        server = None
        rootLogger.info(f"{self.prefix}force_ssl is:{self.force_ssl}")

        if self.force_ssl:
            if self.ssl_context is None:
                rootLogger.info(f"{self.prefix}Selected pure SSL/TLS connection")
                server = MYIMAP4_SSL(host=self.mail_host,
                            port=self.mail_port,
                            socks_creds=self.socks_creds)
            else:
                rootLogger.info(f"{self.prefix}Selected self signed SSL/TLS connection:{self.ssl_context}")
                server = MYIMAP4_SSL(host=self.mail_host,
                            port=self.mail_port,
                            socks_creds=self.socks_creds,
                            ssl_context=self.ssl_context)
        else:
            rootLogger.info(f"{self.prefix}Selected plain/text connection")
            server = MYIMAP4(host=self.mail_host,
                            port=self.mail_port,
                            socks_creds=self.socks_creds)

        server.login(self.mail_user, self.mail_password)
        server.select('INBOX')

        self.server = server

    def close(self):
        if self.server is not None:
            try:
                self.server.logout()
            except Exception as e:
                rootLogger.error(f"{self.prefix} Error closing server:{e}")

    def parseMailFolder(self, data):
        match = re.match(mail_folder_re, data)
        if match is None:
            flags = None
            separator = None
            name = None
        else:
            all_groups = match.groups()
            # flags = match.group(1)
            flags = all_groups[0]
            separator = all_groups[3].replace('"', '')
            name = all_groups[-2].replace('"', '')

        return ( flags, separator, name )

    def getFolders(self):
        # List all mailboxes
        resp, data = self.server.list('""', '*')

        folders = []
        rootLogger.info(f"{self.prefix}.getFolders server.list:\n{self.prefix} resp:[{resp}]\n{self.prefix} data[{data}]")
        for data_item in data:
            flags, separator, name = self.parseMailFolder( data_item.decode('utf-8', 'ignore') )
            if name is not None:
                folders.append(name)
        return folders

    def getMessagesList(self):
        typ, data = self.server.search(None, 'ALL')
        numMsgs = 0
        try:
            numMsgs = int(data[0].split()[-1].decode('utf-8'))
        except Exception as e:
            # raise e
            rootLogger.error(f"{self.prefix} Can't get numMsgs from account:")
            rootLogger.error(data)
        return (numMsgs, 0, [])

    def getMessage(self, msg_num, headers_only=False, get_raw=False ):
        rootLogger.info(f"{self.prefix}Get message:%d headers_only:%r" % (msg_num, headers_only))
        message = None
        msg_num = str.encode(str(msg_num))

        if headers_only:
            typ, data = self.server.fetch(msg_num, '(RFC822.HEADER)')
        else:
            typ, data = self.server.fetch(msg_num, '(RFC822)')

        if type(data[0]) is not list and type(data[0]) is not tuple:
            rootLogger.info(f"{self.prefix}Get message unexpected error: data[0] is {data[0]}")
            # ex = Exception(str(data[0].decode('utf-8', 'ignore')))
            ex = Exception(data[0])
            raise ex

        # i guess this is better variant because if byte sequences will be more than one - we rist go get into deep shit
        if get_raw:
            message = data
        else:
            message = email.message_from_bytes(b''.join(data[0][1:]))

        return message


        # actually Imap feature only

    def selectFolder(self, folder_name):
        try:
            rv, data = self.server.select(f'"{folder_name}"')
            if rv == 'OK':
                if len(data)>0:
                    numMsgs = int(data[0].decode('utf-8', 'ignore'))
                    return numMsgs
                else:
                    return 0
            else:
                rootLogger.error(f"{self.prefix}selectFolder[{folder_name}] rv:{rv}, data:{data}")
                return 0
        except Exception as e:
            rootLogger.error(str(e))
            return 0


import requests
import urllib.parse
from bs4 import BeautifulSoup as soup
import random

from email.parser import HeaderParser
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

class WEBMailProcessor(CommonMailProcessor):
    """docstring for WEBMailProcessor"""

    my_session = None

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

    headers = {
        # 'User-Agent': random.choice(ua_strings),
        'Pragma': 'no-cache',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept': 'gzip, deflate, br',
    }

    # proxies dict for requests
    proxies = {}

    # will contan requests object in case of successfull login
    inner_page = None

    # folders list
    folders = []

    # list of all mail urls for current folder
    mail_urls = []

    # debug value, better variant is 999999
    max_page = 3

    def __init__(self, account, socks_creds={}, ssl_context=None, prefix='' ):
        super().__init__(account, socks_creds, ssl_context, prefix)
        self.mail_host = account.web_url
        self.mail_user = account.web_login
        self.mail_password = account.web_password

        rootLogger.info(f"{self.prefix}Inited {self.mail_user}:{self.mail_password}@{self.mail_host}")

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, type, value, traceback):
        self.close()


    def connect(self):
        # prepare proxies dict
        self.setProxies()

        # assign local variable for ease of use
        url = self.mail_host

        # create session
        self.my_session = requests.Session()
        my_session = self.my_session

        # update headers
        self.headers['User-Agent'] = random.choice(self.ua_strings)

        # get login page
        login_page = my_session.get(self.mail_host, allow_redirects=True, headers=self.headers, proxies=self.proxies)

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

        # get login page from proper url
        login_page2 = my_session.get(new_url, allow_redirects=True, headers=self.headers, proxies=self.proxies)

        # process page to extract few necesseary items
        my_soup = soup(login_page2.text, features="html.parser")

        destination = ''
        try:
            destination = my_soup.find('input', {'name': 'destination'}).get('value')
        except:
            rootLogger.error(f"{self.prefix} connect: destination:{e}")
            pass

        # just cookies i set manually according to request analisys
        my_session.cookies.set('cookieTest', '1')
        my_session.cookies.set('PBack', '0')
        my_session.cookies.set('tzid', 'Eastern Standard Time')

        payload = {
            'destination': destination,
            'flags': '1', # 0 - full version (better for email send), 1 - lite version (better for grabbing)
            'forcedownlevel': '0',
            'trusted': '0',
            'username': self.mail_user,
            'password': self.mail_password,
            'isUtf8': '1'
        }

        inner_page = my_session.post(url, data=payload, allow_redirects=True, headers=self.headers, proxies=self.proxies)

        # check if we are at inner page, else raise Auth error
        my_soup = soup(inner_page.text, features="html.parser")
        if len(my_soup.select('a#lo')) < 1:
            raise Exception('Auth error, incorrect user or password')

        self.inner_page = inner_page

    def setProxies(self):
        # might be user:password@host:port or just host:port
        sock_string = 'socks5://'

        for key in ('user', 'login'):
            if key in self.socks_creds:
                sock_string += self.socks_creds[key]

        if 'password' in self.socks_creds:
            sock_string += f":{self.socks_creds['password']}"

        # if we got credentials
        if sock_string != 'socks5://':
            sock_string += '@'

        sock_string += f"{self.socks_creds['host']}:{self.socks_creds['port']}"

        self.proxies.update({
            'http': sock_string,
            'https': sock_string
        })

    def close(self):
        if self.my_session is not None:
            try:
                self.inner_page = None
                self.my_session.close()
            except Exception as e:
                rootLogger.error(f"{self.prefix}Error closing server:{e}")

    def getFolders(self):
        my_session = self.my_session

        my_soup = soup(self.inner_page.text, features="html.parser")

        # generate url params:
        # https://autodiscover.bgcbc.org/owa/?ae=StartPage&id=LgAAAADNUv7o/RDXSI8oW9t2bdUdAQDKBdsUeOgMRY90RD16PTAtAAAAAQNJAAAB&slUsng=0&pg=1
        # https://autodiscover.bgcbc.org/owa/?ae=StartPage&id=LgAAAADNUv7o/RDXSI8oW9t2bdUdAQDKBdsUeOgMRY90RD16PTAtAAAAAQNJAAAB&slUsng=0&pg=1
        all_folders_url = self.inner_page.url

        a_sAe = "StartPage";
        a_sT = "";
        a_sFldId = "";
        a_sPg = "1";
        a_iSlUsng = 0;

        for line in self.inner_page.text.splitlines():
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

        all_folders_page = my_session.post(all_folders_url, data=payload, allow_redirects=True, headers=self.headers, proxies=self.proxies)

        my_soup = soup(all_folders_page.text, features="html.parser")

        folders = []
        for option in my_soup.select("select#selbrfld option"):
            # rootLogger.info(item.get_text())
            f_title = option.get('title')
            f_id = option.get('value')
            folders.append({f_title:f_id, 'name': f_title, 'id': f_id})

        self.folders = folders

        # return only names
        return [item['name'] for item in self.folders]


    def selectFolder(self, folder_name):
        my_session = self.my_session

        all_folders_url = self.inner_page.url

        # find folder by name
        my_folder = None
        for folder in self.folders:
            if folder['name'] == folder_name:
                my_folder = folder

        if my_folder is None:
            raise Exception(f"Folder '{folder_name}' selection error. No such folder in list.")

        folder_url = all_folders_url.split('/owa')[0] + f'/owa?ae=Folder&t={my_folder["id"]}'
        folder_page = my_session.get(folder_url, allow_redirects=True, headers=self.headers, proxies=self.proxies)

        # search last page of folder
        pages = 1

        my_soup = soup(folder_page.text, features="html.parser")

        for link in my_soup.select("a#lnkLstPg"):
            page_data = link.get('onclick')
            # rootLogger.info(f"page_data:{page_data}")
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
        pages = min(self.max_page, pages)

        mail_urls = []
        for page_num in range(1, pages+1):
            rootLogger.info(f'Start parse {page_num} page..')

            # generate proper url
            folder_nth_page_url = f"{folder_url}&pg={page_num}"

            # get nth page
            folder_nth_page = my_session.get(folder_nth_page_url, allow_redirects=True, headers=self.headers, proxies=self.proxies)

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

                # rootLogger.info(f"mail_url: {mail_url}")
                # rootLogger.info(f"mail_headers_url: {mail_headers_url}")

                mail_urls.append({'id':msg_id
                    ,'header':mail_headers_url
                    ,'body':mail_url
                })

        self.mail_urls = mail_urls

        return len(self.mail_urls)

    def getMessage(self, msg_num, headers_only=False, get_raw=False ):
        my_session = self.my_session
        mail_urls = self.mail_urls

        # decrease by one for ease of use
        msg_num = msg_num - 1

        # Make GET request to get headers from textarea
        mail_headers_url = mail_urls[msg_num]['header']

        mail_headers_page = my_session.get(mail_headers_url, allow_redirects=True, headers=self.headers, proxies=self.proxies)
        my_soup = soup(mail_headers_page.text, features="html.parser")
        headers_raw = my_soup.select('textarea')[0].encode_contents()

        # create header object for futher ease of use
        # rootLogger.info(f"{self.prefix} headers_raw.decode('utf-8'):{headers_raw.decode('utf-8')}")
        headers_raw_str = headers_raw.decode('utf-8')
        h = HeaderParser().parsestr(text=headers_raw_str)
        msg = MIMEMultipart()
        msg.set_charset("utf-8")
        # update all headers for message item
        for k,v in h.items():
            if str(k).lower() not in ('Content-Type', 'Content-Transfer-Encoding'):
                msg[str(k)] = str(v)

        # save message id
        msg.add_header('Outlook-Inner-Id', mail_urls[msg_num]['id'])

        # Make GET request to get body content
        if not headers_only:
            mail_body_url = mail_urls[msg_num]['body']

            mail_body_page = my_session.get(mail_body_url, allow_redirects=True, headers=self.headers, proxies=self.proxies)
            my_soup = soup(mail_body_page.text, features="html.parser")
            body_raw = my_soup.select('td.bdy div.bdy')[0].encode_contents()

            body_tpl = f'<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">\r\n<html xmlns="http://www.w3.org/1999/xhtml">\r\n<head>\r\n<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />\r\n<title>{msg["Subject"]}</title>\r\n</head>\r\n</head>\r\n<body>{body_raw.decode("utf-8")}</body>\r\n</html>'
            # append body
            msg.attach(MIMEText(body_tpl, 'html', 'utf-8'))

        return msg

# class WEBMailProcessor(CommonMailProcessor):
#     """docstring for POP3MailProcessor"""
#     def __init__(self, account, socks_creds={}, ssl_context=None, prefix='' ):
#         super().__init__(account, socks_creds, ssl_context, prefix)
#         self.mail_host = account.web_url
#         self.mail_user = account.web_login
#         self.mail_password = account.web_password

#         rootLogger.info(f"{self.prefix}Inited {self.mail_user}:{self.mail_password}@{self.mail_host}")

#     def __enter__(self):
#         self.connect()
#         return self

#     def __exit__(self, type, value, traceback):
#         self.close()

#     def connect(self):
#         server = None
#         rootLogger.info(f"{self.prefix}force_ssl is False")

#         # crates session for webacc
#         # override original port with my custom shit
#         server = WebMailClass(socks_address=self.socks_creds['host'], socks_port=27471, prefix=self.prefix)

#         try:
#             server.StartSession(webmail_login=self.mail_user, webmail_password=self.mail_password, webmail_url=self.mail_host, grabber_mode=True)
#         except Exception as e:
#             server = None
#             raise e

#         self.server = server

#     def close(self):
#         if self.server is not None and self.server.driver is not None:
#             try:
#                 self.server.driver.quit()
#             except Exception as e:
#                 rootLogger.error(f"{self.prefix}Error closing server:{e}")

#         # need this anyway

#     def getFolders(self):
#         return self.server.getFolders()

#     def getMessage(self, msg_num, headers_only=False, get_raw=False ):
#         rootLogger.info(f"{self.prefix}Get message:{msg_num} headers_only:{headers_only}")
#         message = None
#         # try:
#         if headers_only:
#             (response, resp_body, octets) = self.server.top(msg_num, 0)
#         else:
#             (response, resp_body, octets) = self.server.retr(msg_num)

#         if get_raw:
#             message = resp_body
#         else:
#             message = email.message_from_bytes(b'\r\n'.join(resp_body))

#         return message

#     # actually Imap feature only, need just to emulate and make API same
#     def selectFolder(self, folder_name):
#         return self.server.selectFolder(folder_name)

