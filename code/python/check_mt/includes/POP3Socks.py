import poplib, socket, datetime, re
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


class MYPOP3(poplib.POP3):
    def __init__(self, host, port=poplib.POP3_PORT,
                 timeout=socket._GLOBAL_DEFAULT_TIMEOUT, socks_creds=None):

        # save socket credits for futher use
        self.socks_creds = socks_creds

        super(MYPOP3, self).__init__(host=host, port=port,
                 timeout=timeout)

    # override socket creation based on whether we have socks or no
    def _create_socket(self, timeout):
        # return socket.create_connection((self.host, self.port), timeout)

        if self.socks_creds is None:
            return socket.create_connection((self.host, self.port), timeout)
        else:
            # convert this mess to a set of variables suitable for socksify
            proxy_args = get_socks_socket((self.host, self.port), timeout,
                                            None, self.socks_creds)

            return socks.create_connection(**proxy_args)



class MYPOP3_SSL(poplib.POP3_SSL):
    def __init__(self, host, port=poplib.POP3_SSL_PORT, keyfile=None, certfile=None,
                     timeout=socket._GLOBAL_DEFAULT_TIMEOUT, context=None, socks_creds=None):

        # save socket credits for futher use
        self.socks_creds = socks_creds

        super(MYPOP3_SSL, self).__init__(host=host, port=port, keyfile=keyfile, certfile=certfile,
                     timeout=timeout, context=context)

    # override socket creation based on whether we have socks or no
    def _create_socket(self, timeout):
            # sock = POP3._create_socket(self, timeout)

            if self.socks_creds is None:
                sock = socket.create_connection((self.host, self.port), timeout)
            else:
                # convert this mess to a set of variables suitable for socksify
                proxy_args = get_socks_socket((self.host, self.port), timeout,
                                                None, self.socks_creds)

                sock = socks.create_connection(**proxy_args)

            sock = self.context.wrap_socket(sock,
                                            server_hostname=self.host)
            return sock
