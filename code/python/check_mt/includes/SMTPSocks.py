import smtplib, socket, datetime, re
import socks

# monkey patching socks to use IPv4 only, since PySocks not support for IPv6
old_getaddrinfo = socket.getaddrinfo
def new_getaddrinfo(*args, **kwargs):
    responses = old_getaddrinfo(*args, **kwargs)
    return [response
            for response in responses
            if response[0] == socket.AF_INET]

socket.getaddrinfo = new_getaddrinfo

def get_socks_socket(dest_pair, timeout=600, source_address=None, kwargs={}):

    # print(f"kwargs:{kwargs}")

    data = {
        'dest_pair': dest_pair,
        'timeout':timeout,
        'source_address':None,
        'proxy_type':socks.SOCKS5,
        'proxy_addr':None,
        'proxy_port':None,
        'proxy_rdns':True,
        'proxy_username':None,
        'proxy_password':None,
        'socket_options':None
    }

    for key in ('user', 'login'):
        if key in kwargs:
            data['proxy_username'] = kwargs[key]

    if 'password' in kwargs:
        data['proxy_password'] = kwargs['password']

    if 'port' in kwargs:
        data['proxy_port'] = kwargs['port']

    if 'host' in kwargs:
        data['proxy_addr'] = kwargs['host']

    # print(f"get_socks_socket return data:{data}")

    return data

# try to override few methods from classes
# actually now it is only one method - debug print
class MYSMTP(smtplib.SMTP):
    def __init__(self, host='', port=0, local_hostname=None,
                # timeout=socket._GLOBAL_DEFAULT_TIMEOUT,
                timeout=60,
                source_address=None,
                socks_creds=None
                ):
        self.debug_log = []

        # save socket credits for futher use
        self.socks_creds = socks_creds

        # self.debuglevel = 2

        # super().__init__(host, port, local_hostname, timeout, source_address)
        super(MYSMTP, self).__init__(
            host=host,
            port=port,
            local_hostname=local_hostname,
            timeout=timeout,
            source_address=source_address)

    def _get_socket(self, host, port, timeout):
        # This makes it simpler for SMTP_SSL to use the SMTP connect code
        # and just alter the socket connection bit.
        if self.debuglevel > 0:
            self._print_debug('connect: to', (host, port), self.source_address)

        if self.socks_creds is None:
            return socket.create_connection((host, port), timeout,
                                            self.source_address)
        else:
            # convert this mess to a set of variables suitable for socksify
            proxy_args = get_socks_socket((host, port), timeout,
                                            self.source_address, self.socks_creds)

            # proxy_sock = socks.socksocket()
            return socks.create_connection(**proxy_args)

    def _print_debug(self, *args):
        log_str = ""
        if self.debuglevel > 1:
            log_str += "["+str(datetime.datetime.now().time())+"]: "

        for count, thing in enumerate(args):
            try:
                str_part = str(thing.decode("utf-8"))
            except Exception as e:
                str_part = str(thing)

            # skip log for body
            search = re.search('Content-Type: multipart/mixed;',str_part)
            if search is not None:
                log_str += "[multipart message body]"
                continue

            log_str += str_part

        self.debug_log.append(log_str)

    def get_log(self):
        return self.debug_log

class MYSMTP_SSL(smtplib.SMTP_SSL):
    def __init__(self, host='', port=0, local_hostname=None,
                keyfile=None, certfile=None,
                # timeout=socket._GLOBAL_DEFAULT_TIMEOUT,
                timeout=60,
                source_address=None,
                context=None,
                socks_creds=None):
        self.debug_log = []

        # save socket credits for futher use
        self.socks_creds = socks_creds

        # super.__init__(host, port, local_hostname, keyfile, certfile, timeout, source_address, context)
        super(MYSMTP_SSL, self).__init__(
            host=host,
            port=port,
            local_hostname=local_hostname,
            keyfile=keyfile,
            certfile=certfile,
            timeout=timeout,
            source_address=source_address,
            context=context)

    def _get_socket(self, host, port, timeout):
            if self.debuglevel > 0:
                self._print_debug('connect:', (host, port))

            # new_socket = socket.create_connection((host, port), timeout,
            #         self.source_address)
            if self.socks_creds is None:
                new_socket = socket.create_connection((host, port), timeout,
                                                self.source_address)
            else:
                # convert this mess to a set of variables suitable for socksify
                proxy_args = get_socks_socket((host, port), timeout,
                                                self.source_address, self.socks_creds)

                # proxy_sock = socks.socksocket()
                new_socket = socks.create_connection(**proxy_args)

            new_socket = self.context.wrap_socket(new_socket,
                                                  server_hostname=self._host)
            return new_socket

    def _print_debug(self, *args):
        log_str = ""
        if self.debuglevel > 1:
            log_str += "["+str(datetime.datetime.now().time())+"]: "

        for count, thing in enumerate(args):
            try:
                str_part = str(thing.decode("utf-8"))
            except Exception as e:
                str_part = str(thing)

            # skip log for body
            search = re.search('Content-Type: multipart/mixed;',str_part)
            if search is not None:
                log_str += "[multipart message body]"
                continue

            log_str += str_part

        self.debug_log.append(log_str)

    def get_log(self):
        return self.debug_log

def print_ts(my_str, my_prefix = "Manager"):
    # my_now = datetime.datetime.now()
    # print(my_now.strftime('%d-%m-%Y %H:%M:%S [httptest]') + my_str)

    ts = str(datetime.datetime.now())
    log = "[%s]%s: %s " % (ts, my_prefix, str(my_str))
    print(log)


retry_list = ("COUNTRY IS BLACKLISTED", "connections from", "Server shutting down", "Access is not permitted from your IP", "try again later", "[SYS/TEMP]", "Try again", "daily sending limits for this IP") #"temporary error"
socket_errors = ("Socket error", "Connection closed unexpectedly", "Connection reset by peer", "broken pipe", "TTL expired", "Host unreachable", "Connection refused")
auth_error_list = ("[auth", "auth", "username", "password", "login", "credentials", 'ncorrect authentication', 'not permitted to send messages', 'too many failed logins')
send_limit_list = ('exceeded the configured limit', 'messages amount exceeded')
force_ssl_list = ('Plaintext authentication disallowed',)
wrong_ssl_list = ('WRONG_VERSION_NUMBER', 'wrong version number', '_ssl.c:')
