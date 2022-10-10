import datetime
import traceback
# email parsers
import email # new statement
import json
# from email.header import decode_header
from email.utils import parsedate_tz, mktime_tz, formatdate
# from bs4 import BeautifulSoup

# pip install yattag

from yattag import Doc
# doc, tag, text = Doc().tagtext()

import re
import email

import base64

re_doctype = re.compile(r'\<\!doctype.*\>', re.IGNORECASE | re.MULTILINE)
re_html = re.compile(r'\<html.*\>', re.IGNORECASE | re.MULTILINE)
re_head = re.compile(r'\<head.*\>', re.IGNORECASE | re.MULTILINE)
re_body = re.compile(r'\<body.*\>', re.IGNORECASE | re.MULTILINE)
re_paragraph = re.compile(r'\<p.*\>', re.IGNORECASE | re.MULTILINE)
re_breakline = re.compile(r'\<br.*\>', re.IGNORECASE | re.MULTILINE)

re_isbase64 = re.compile(r'^([A-Za-z0-9+\/]{4})*([A-Za-z0-9+\/]{3}=|[A-Za-z0-9+\/]{2}==)?$')

# generates email body answer
class MailAnswerClass():
	def __init__(self, msg_body, msg_headers_dict, answer_text):
		self.msg_body = msg_body
		self.msg_headers_dict = msg_headers_dict
		self.answer_text = answer_text

		# in case parser cound't parse well
		self.from_name = msg_headers_dict['From']
		# parse From to make it better show
		parsed = email.utils.getaddresses([msg_headers_dict['From']])
		if len(parsed):
			if len(parsed[0]) and len(parsed[0][0]):
				self.from_name = parsed[0][0]

		# # everytime reinit
		# doc, tag, text = Doc().tagtext()


	def getProcessed(self, generate_html=True, use_reply=True):
		if generate_html in (True, 1):
			return self.generateHtmlAnswer(use_reply=use_reply)
		else:
			return self.generatePlainTextAnswer(use_reply=use_reply)

	def bodyIsLikelyHtml(self):
		markers = 0
		# search for tags, if found more than 2, assume that this is html

		# print("check for re_doctype")
		if re_doctype.search(self.msg_body):
			markers += 1
			# print("re_doctype success, markers state:{}".format(markers))
		else:
			# print("re_doctype fail, markers state:{}".format(markers))
			pass

		# print("check for re_html")
		if re_html.search(self.msg_body):
			markers += 1
			# print("re_html success, markers state:{}".format(markers))
		else:
			# print("re_html fail, markers state:{}".format(markers))
			pass

		# print("check for re_head")
		if re_head.search(self.msg_body):
			markers += 1
			# print("re_head success, markers state:{}".format(markers))
		else:
			# print("re_head fail, markers state:{}".format(markers))
			pass

		# print("check for re_body")
		if re_body.search(self.msg_body):
			markers += 1
			# print("re_body success, markers state:{}".format(markers))
		else:
			# print("re_body fail, markers state:{}".format(markers))
			pass

		# print("check for re_breakline")
		if re_breakline.search(self.msg_body):
			markers += 1
			# print("re_breakline success, markers state:{}".format(markers))
		else:
			# print("re_breakline fail, markers state:{}".format(markers))
			pass

		# print("check for re_paragraph")
		if re_paragraph.search(self.msg_body):
			markers += 1
			# print("re_paragraph success, markers state:{}".format(markers))
		else:
			# print("re_paragraph fail, markers state:{}".format(markers))
			pass

		if markers > 2:
			# print("marker state:{}, return True".format(markers))
			return True
		else:
			# print("marker state:{}, return False".format(markers))
			return False

	def generateHtmlAnswer(self, use_reply=True):
		doc, tag, text = Doc().tagtext()


		re_subject = "Re: "
		if 'Subject' in self.msg_headers_dict:
			if use_reply:
				re_subject = "Re: " + self.msg_headers_dict['Subject']
			else:
				re_subject = self.msg_headers_dict['Subject']


		message_id = ""
		if 'Message-ID' in self.msg_headers_dict:
			message_id = self.msg_headers_dict['Message-ID']
			message_id = re.sub(r'^\<','', message_id)
			message_id = re.sub(r'\>$','', message_id)

		with tag('html'):
			# head
			# with tag("head"):
			# 	with tag("title"):
			# 			text(re_subject)
			# 	with tag("link", ('rel', 'important stylesheet'), ('href', 'chrome://messagebody/skin/messageBody.css')):
			# 		text('')
			# body
			# with tag("body"):
				# header-part-1
				# with tag('table', ('border','0'), ("cellspacing","0"), ("cellpadding","0"), ("width","100%"), ("class","header-part1")):
				# 	with tag('tr'):
				# 		with tag('td'):
				# 			with tag('b'):
				# 				text("Subject: ")
				# 			text(re_subject)
				# 	with tag('tr'):
				# 		with tag('td'):
				# 			with tag('b'):
				# 				text("From: ")
				# 			text(self.msg_headers_dict['From'])
				# 	with tag('tr'):
				# 		with tag('td'):
				# 			with tag('b'):
				# 				text("Date: ")
				# 			text(self.msg_headers_dict['Date'])

				# # header-part-2
				# with tag('table', ('border','0'), ("cellspacing","0"), ("cellpadding","0"), ("width","100%"), ("class","header-part2")):
				# 	with tag('tr'):
				# 		with tag('td'):
				# 			with tag('b'):
				# 				text("To: ")
				# 			text(self.msg_headers_dict['To'])

				# doc.asis('<br/>')
				# with tag('br'):
				# 	text('')

				# with tag('html'):
			with tag('head'):
				with tag('meta', ("http-equiv","Content-Type"), ("content", "text/html; ")):
					text('')

				# not sure if it is needed at all
				# with tag("title"):
				# 	text(re_subject)

			with tag("body", ("text","#000000"), ("bgcolor","#FFFFFF")):
				# if found url without tags, wrap with tags
				self.answer_text = re.sub(r'((?<!\>)(https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)))', '<a href="\g<1>">\g<1></a>', self.answer_text)

				# res = re.findall(r'((?<!\>)(https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)))', self.answer_text)
				# # leave only unique
				# res = list(set(res))
				# for occurence in res:
				# 	if len(occurence) and len(occurence[0]):
				# 		item = occurence[0]
				# 		self.answer_text = self.answer_text.replace( item, f'<a href="{item}">{item}</a>' )

				doc.asis(self.answer_text.replace("\n", "<br/>"))

				# with tag('p'):
				# 	doc.asis('<br/>')
				# 	# with tag('br'):
				# 		# text('')

				if use_reply:
					with tag("div", ("class","moz-cite-prefix")):
						text("On %s, %s wrote:" % (self.msg_headers_dict['Date'].split("-")[0].split("+")[0], self.from_name))
						doc.asis('<br/>')
						# with tag("br"):
							# text('')


					with tag("blockquote", ("type","cite"), ( "cite","mid:%s" % message_id ) ):
						content_type = "text"
						for hkey in self.msg_headers_dict.keys():
							if hkey.lower() == "content-type":
								content_type = self.msg_headers_dict[hkey]

						# if "html" in content_type:
						if self.bodyIsLikelyHtml():
							with tag('head'):
								with tag('meta', ("http-equiv","Content-Type"), ("content", "text/html; charset=UTF-8")):
									text("")
								doc.asis(self.msg_body)
						else:
							with tag('pre', ("class","moz-quote-pre"), ("wrap","")):
								text(self.msg_body)


		return doc.getvalue()

	def generatePlainTextAnswer(self, use_reply=True):
		repl = "\r\n> "
		ret_body = self.answer_text + "\r\n\r\n"
		if use_reply:
			ret_body += "On %s, %s wrote:\r\n" % (self.msg_headers_dict['Date'], self.from_name)
			ret_body += repl + re.sub(r'\r?\n', repl, self.msg_body, flags=re.IGNORECASE | re.MULTILINE )
			ret_body += "\r\n"

		return ret_body

	def bodyIsLikelyBase64(self):
		if len(self.msg_body) > 23 and len(self.msg_body) % 4 == 0 and re_isbase64.match(self.msg_body):
			return True
		else:
			return False

	def decodeBodyFromBase64(self):
		res = True
		try:
			decoded = base64.b64decode(self.msg_body)
			self.msg_body = decoded
		except Exception as e:
			res = False

		return res

if __name__ == "__main__":
	print("Whee")
	# msg_headers_dict = {"Return-Path": "<MAILER-DAEMON>", "Received": "from mwb-vc-mts-004c1.ocn.ad.jp (mwb-vc-mts-004c1.ocn.ad.jp [153.153.67.75])\r\n\tby vg-cb014.ocn.ad.jp (Postfix) with ESMTP id 57F809C0291\r\n\tfor <yuokuda@tsukuba-s.jp>; Wed, 13 Mar 2019 20:56:05 +0900 (JST)", "Date": "Wed, 13 Mar 2019 20:56:05 +0900", "Message-ID": "<1552478165.42UPhum5unqfd42UPh8VkK@mwb-vc-mts-004c1.ocn.ad.jp>", "From": "\"Mail Delivery Subsystem\" <MAILER-DAEMON@mwb-vc-mts-004c1.ocn.ad.jp>", "To": "yuokuda@tsukuba-s.jp", "Subject": "Returned mail: see transcript for details", "MIME-Version": "1.0", "Content-Type": "multipart/report; boundary=\"------------I305M09060309060P_950415524781650\""}
	msg_headers_dict = {
	    "Return-Path": "<MAILER-DAEMON>",
	    "Received": "from mwb-vc-mts-004c1.ocn.ad.jp (mwb-vc-mts-004c1.ocn.ad.jp [153.153.67.75])\r\n\tby vg-cb014.ocn.ad.jp (Postfix) with ESMTP id 57F809C0291\r\n\tfor <yuokuda@tsukuba-s.jp>; Wed, 13 Mar 2019 20:56:05 +0900 (JST)",
	    "Date": "{date}",
	    "Message-ID": "{msg_id}",
	    "From": "{from}",
	    "To": "{to}",
	    "Subject": "{subject}",
	    "MIME-Version": "1.0",
	    "COntent-Type": "multipart/report; boundary=\"------------I305M09060309060P_950415524781650\""
	}
	item = MailAnswerClass(msg_body="Some original body shit text goes here\nWith fome new tring data\r\nand some onther strings", msg_headers_dict=msg_headers_dict, answer_text="Some super duper answer here")

	print(item.getProcessed(True))
