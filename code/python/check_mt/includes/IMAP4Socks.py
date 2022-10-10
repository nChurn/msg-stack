import imaplib, socket, datetime, re
import socks

def get_socks_socket(dest_pair, timeout=60, source_address=None, kwargs={}):

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

class MYIMAP4(imaplib.IMAP4):
    def __init__(self, host='', port=imaplib.IMAP4_PORT, socks_creds=None):

        # save socket credits for futher use
        self.socks_creds = socks_creds
        # print(f'host:{host}')

        super(MYIMAP4, self).__init__(host=host, port=port)


    def _create_socket(self):
        # Default value of IMAP4.host is '', but socket.getaddrinfo()
        # (which is used by socket.create_connection()) expects None
        # as a default value for host.
        host = None if not self.host else self.host
        # return socket.create_connection((host, self.port))

        if self.socks_creds is None:
            return socket.create_connection((host, self.port))
        else:
            # convert this mess to a set of variables suitable for socksify
            proxy_args = get_socks_socket((host, self.port), kwargs=self.socks_creds)

            return socks.create_connection(**proxy_args)

class MYIMAP4_SSL(imaplib.IMAP4_SSL):
    def __init__(self, host='', port=imaplib.IMAP4_SSL_PORT, keyfile=None,
                     certfile=None, ssl_context=None, socks_creds=None):

        # save socket credits for futher use
        self.socks_creds = socks_creds

        super(MYIMAP4_SSL, self).__init__(host=host, port=port, keyfile=keyfile,
                                            certfile=certfile, ssl_context=ssl_context)

    def _create_socket(self):
        # Default value of IMAP4.host is '', but socket.getaddrinfo()
        # (which is used by socket.create_connection()) expects None
        # as a default value for host.
        host = None if not self.host else self.host

        if self.socks_creds is None:
            sock = socket.create_connection((host, self.port))
        else:
            # convert this mess to a set of variables suitable for socksify
            proxy_args = get_socks_socket((host, self.port), kwargs=self.socks_creds)

            sock = socks.create_connection(**proxy_args)

        # sock = IMAP4._create_socket(self)
        return self.ssl_context.wrap_socket(sock,
                                            server_hostname=self.host)

