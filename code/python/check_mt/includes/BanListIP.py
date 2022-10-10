# Based on ptoject from GitHub page:
# https://github.com/jgamblin/isthisipbad/blob/master/isthisipbad.py
# Modified by MJC to fix errors.

import os
import sys
import urllib
import urllib.request
# import urllib2
import re
import socket
# Requires dnspython AKA python-dns package
import dns.resolver
import socks

from ipaddress import ip_network, ip_address

# net = ip_network("1.1.0.0/16")
# print(ip_address("1.1.2.2") in net)    # True

# blacklists for dns resolving
# bls = ["b.barracudacentral.org", "bl.spamcannibal.org", "bl.spamcop.net",
#        "blacklist.woody.ch", "cbl.abuseat.org", "cdl.anti-spam.org.cn",
#        "combined.abuse.ch", "combined.rbl.msrbl.net", "db.wpbl.info",
#        "dnsbl-1.uceprotect.net", "dnsbl-2.uceprotect.net",
#        "dnsbl-3.uceprotect.net", "dnsbl.cyberlogic.net",
#        "dnsbl.sorbs.net", "drone.abuse.ch", "drone.abuse.ch",
#        "duinv.aupads.org", "dul.dnsbl.sorbs.net", "dul.ru",
#        "dyna.spamrats.com", "dynip.rothen.com",
#        "http.dnsbl.sorbs.net", "images.rbl.msrbl.net",
#        "ips.backscatterer.org", "ix.dnsbl.manitu.net",
#        "korea.services.net", "misc.dnsbl.sorbs.net",
#        "noptr.spamrats.com", "ohps.dnsbl.net.au", "omrs.dnsbl.net.au",
#        "orvedb.aupads.org", "osps.dnsbl.net.au", "osrs.dnsbl.net.au",
#        "owfs.dnsbl.net.au", "pbl.spamhaus.org", "phishing.rbl.msrbl.net",
#        "probes.dnsbl.net.au", "proxy.bl.gweep.ca", "rbl.interserver.net",
#        "rdts.dnsbl.net.au", "relays.bl.gweep.ca", "relays.nether.net",
#        "residential.block.transip.nl", "ricn.dnsbl.net.au",
#        "rmst.dnsbl.net.au", "smtp.dnsbl.sorbs.net",
#        "socks.dnsbl.sorbs.net", "spam.abuse.ch", "spam.dnsbl.sorbs.net",
#        "spam.rbl.msrbl.net", "spam.spamrats.com", "spamrbl.imp.ch",
#        "t3direct.dnsbl.net.au", "tor.dnsbl.sectoor.de",
#        "torserver.tor.dnsbl.sectoor.de", "ubl.lashback.com",
#        "ubl.unsubscore.com", "virus.rbl.jp", "virus.rbl.msrbl.net",
#        "web.dnsbl.sorbs.net", "wormrbl.imp.ch", "xbl.spamhaus.org",
#        "zen.spamhaus.org", "zombie.dnsbl.sorbs.net"]

# blacklists for dns resolving SHORT
bls = ['zen.spamhaus.org',
'dnsbl.sorbs.net',
'bl.spamcop.net']

# URLS to check if our ip in list
URLS = [
    #TOR
    ('http://torstatus.blutmagie.de/ip_list_exit.php/Tor_ip_list_EXIT.csv',
     'is not a TOR Exit Node',
     'is a TOR Exit Node',
     False),

    #EmergingThreats
    ('http://rules.emergingthreats.net/blockrules/compromised-ips.txt',
     'is not listed on EmergingThreats',
     'is listed on EmergingThreats',
     True),

    #AlienVault
    ('http://reputation.alienvault.com/reputation.data',
     'is not listed on AlienVault',
     'is listed on AlienVault',
     True),

    #BlocklistDE
    ('http://www.blocklist.de/lists/bruteforcelogin.txt',
     'is not listed on BlocklistDE',
     'is listed on BlocklistDE',
     True),

    #Dragon Research Group - SSH
    ('http://dragonresearchgroup.org/insight/sshpwauth.txt',
     'is not listed on Dragon Research Group - SSH',
     'is listed on Dragon Research Group - SSH',
     True),

    #Dragon Research Group - VNC
    ('http://dragonresearchgroup.org/insight/vncprobe.txt',
     'is not listed on Dragon Research Group - VNC',
     'is listed on Dragon Research Group - VNC',
     True),

    #OpenBLock
    ('http://www.openbl.org/lists/date_all.txt',
     'is not listed on OpenBlock',
     'is listed on OpenBlock',
     True),

    #NoThinkMalware
    ('http://www.nothink.org/blacklist/blacklist_malware_http.txt',
     'is not listed on NoThink Malware',
     'is listed on NoThink Malware',
     True),

    #NoThinkSSH
    ('http://www.nothink.org/blacklist/blacklist_ssh_all.txt',
     'is not listed on NoThink SSH',
     'is listed on NoThink SSH',
     True),

    #Feodo
    ('http://rules.emergingthreats.net/blockrules/compromised-ips.txt',
     'is not listed on Feodo',
     'is listed on Feodo',
     True),

    #antispam.imp.ch
    ('http://antispam.imp.ch/spamlist',
     'is not listed on antispam.imp.ch',
     'is listed on antispam.imp.ch',
     True),

    #dshield
    ('http://www.dshield.org/ipsascii.html?limit=10000',
     'is not listed on dshield',
     'is listed on dshield',
     True),

    #malc0de
    ('http://malc0de.com/bl/IP_Blacklist.txt',
     'is not listed on malc0de',
     'is listed on malc0de',
     True),

    #MalWareBytes
    ('http://hosts-file.net/rss.asp',
     'is not listed on MalWareBytes',
     'is listed on MalWareBytes',
     True)]

#    #Spamhaus DROP (in CIDR format, needs parsing)
#    ('https://www.spamhaus.org/drop/drop.txt',
#     'is not listed on Spamhaus DROP',
#     'is listed on Spamhaus DROP',
#     False),
#    #Spamhaus EDROP (in CIDR format, needs parsing)
#    ('https://www.spamhaus.org/drop/edrop.txt',
#     'is not listed on Spamhaus EDROP',
#     'is listed on Spamhaus EDROP',
#     False)]

URLSCIDR = [
   #Spamhaus DROP (in CIDR format, needs parsing)
   ('https://www.spamhaus.org/drop/drop.txt',
    'is not listed on Spamhaus DROP',
    'is listed on Spamhaus DROP',
    False),
   #Spamhaus EDROP (in CIDR format, needs parsing)
   ('https://www.spamhaus.org/drop/edrop.txt',
    'is not listed on Spamhaus EDROP',
    'is listed on Spamhaus EDROP',
    False)
]

def checIpForDNSResolver(badip):
    global bls
    occurencies = []
    for bl in bls:
        check_addr = None

        try:
            check_host = '.'.join(reversed(str(badip).split("."))) + "." + bl
            check_addr = socket.gethostbyname(check_host)
        # except socket.error:
        except Exception as e:
            check_addr = None

        if check_addr is not None and "127.0.0." in check_addr:
            # print("blacklisted check_addr:%s" % check_addr)
            # print ("[checIpForDNSResolver] %s is listed in %s (%s: %s)" % (badip, bl, check_addr, check_host) )
            occurencies.append(bl)
        else:
            pass
            # print ("[checIpForDNSResolver] %s is NOT listed in %s (%s: %s)" % (badip, bl, check_addr, check_host) )


        # try:
        #     my_resolver = dns.resolver.Resolver()
        #     query = '.'.join(reversed(str(badip).split("."))) + "." + bl


        #     my_resolver.nameservers = [
        #         '8.8.8.8', #google
        #         '8.8.4.4', #google
        #         '8.26.56.26', # Comodo
        #         '8.20.247.20', # Comodo
        #         '84.200.69.80', #DNS.Watch
        #         '84.200.70.40', #DNS.Watch
        #         '77.88.8.88', #yandex
        #         '77.88.8.2' #yandex
        #     ]
        #     my_resolver.timeout = 5
        #     my_resolver.lifetime = 5

        #     print("[checIpForDNSResolver][query]%s" % query)

        #     answers = my_resolver.query(query, "A")
        #     answer_txt = my_resolver.query(query, "TXT")

        #     print(str(answers[0:]))
        #     print(str(answer_txt[0:]))

        #     # for rr in answers:
        #     #     print("[checIpForDNSResolver][aswers]%s" % rr)

        #     # for rr in answer_txt:
        #     #     print("[checIpForDNSResolver][answer_txt]%s" % rr)

        #     print ("[checIpForDNSResolver] %s is listed in %s (%s: %s)" % (badip, bl, answers[0], answer_txt[0]) )
        #     occurencies.append(bl)

        # except dns.resolver.NXDOMAIN:
        #     print ("[checIpForDNSResolver] %s is not listed in %s" % (badip, bl) )
        #     pass

        # except dns.resolver.Timeout:
        #     pass
        #     print ("[checIpForDNSResolver]WARNING: Timeout querying for [%s][%s]" % (badip, bl) )

        # except dns.resolver.NoNameservers:
        #     pass
        #     print ("[checIpForDNSResolver]WARNING: No nameservers for [%s][%s]" % (badip, bl) )

        # except dns.resolver.NoAnswer:
        #     pass
        #     print ("[checIpForDNSResolver]WARNING: No answer for [%s][%s]" % (badip, bl) )

    return occurencies

# def checkIpInCIDRRecord(badip, cidr):
#     net = ip_network(cidr)
#     return ip_address(badip) in net

# blacklists list of dicts from getBlackLists() function
def checkIpInBlackList(badip, blacklists):
    occurencies = []

    for bl in blacklists:
        # treat regular ip
        if bl['type'] == 'ip':
            matches = re.findall(badip, bl['content'])
            if len(matches):
                occurencies.append(bl['url'])
        # treat cidr records
        else:
            # print("cidr list check")
            cidr_list = bl['content'].split("\n")
            for cidr in cidr_list:
                # print("Checking cidr[%s] for ip[%s] " % (cidr, badip))
                net = ip_network(cidr)
                if ip_address(badip) in net:
                    occurencies.append(bl['url'])

    # remove duplicates
    occurencies = list(set(occurencies))

    return occurencies

# predownload all blacklists
def getBlackLists(dl_regular = True, dl_cidr = True):
    global URLS
    blacklists = []
    try:
        # regular ip list
        if dl_regular:
            for url, succ_txt, fail_txt, mal in URLS:
                with urllib.request.urlopen(url) as response:
                    retcode = response.code
                    if retcode == 200:
                        html_content = response.read().decode('utf8')
                        blacklists.append({"url": url, "content": html_content, "type": "ip"})

        # CIDR formatted ip list
        if dl_cidr:
            for url, succ_txt, fail_txt, mal in URLSCIDR:
                with urllib.request.urlopen(url) as response:
                    retcode = response.code
                    if retcode == 200:
                        html_content = response.read().decode('utf8')
                        matches = re.findall("(?:\d{1,3}\.){3}\d{1,3}(?:/\d\d?)?", html_content)
                        blacklists.append({"url": url, "content": "\n".join(matches), "type": "ip_cidr"})

    except Exception as e:
        print( "checkIpInBlackList error: [%s] %s" % (url, str(e)) )

    return blacklists
