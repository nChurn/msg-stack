from bs4 import BeautifulSoup

# dumbfuck hack for AttributeError: 'Model' object has no attribute '_distribution_strategy'
# model._get_distribution_strategy = lambda: None
import string
import random
import re

def randomString(size_min=4, size_max=10, chars=string.ascii_letters + string.digits):
    if size_max == 0:
        gen_size = size_min
    else:
        gen_size = random.randint(size_min, size_max)

    return ''.join(random.choice(chars) for _ in range(gen_size))

#экземпляр модели создан, задаем некоторые функции для пост-обработки и препроцессинга текста
def ClearTextAfterGeneration(t):
    for i in ['.',",",'?',':','!','(',')',';']:
        t=t.replace(' {} '.format(i), '{} '.format(i))
        t=re.sub('\s\s+',' ',t)
        t=t.strip()
        return t

def ClearTextBefore(t):
    # # try  to remove double escaping
    # print(f'ClearTextBefore:0')
    # if t:
    #   t = t.replace("\\\\", "\\")
    #   # .replace('\\"', '"').replace("\\'", "'")

    try:
      tree = BeautifulSoup(t, 'lxml') #создаем объект и указываем парсер
      print("ClearTextBefore 1")
      body = tree.body
      for tag in body.select('script'):
          print("ClearTextBefore 2")
          tag.decompose()
      for tag in body.select('style'):
          print("ClearTextBefore 3")
          tag.decompose()
      #убираем тэги и скрипты и немного причесываем текст

      text = body.get_text()
      print("ClearTextBefore 4")
    except Exception as e:
      print(f"ClearTextBefore 5:{e}")
      text = randomString(1,1)

    print("ClearTextBefore 6")
    #replace_elements=['\\r','\\t','\\n','\\xa0','\\u200c']
    for key,value in smbls.items():
        text=text.replace(key,value)
        text = re.sub('\s\s+',' ',text)

    print("ClearTextBefore 7")
    return text


#словарь, который используем как реплэйс-паттерн
smbls={
            'New message:':'',
            '\n':' ',
            '\\n':' ',
            '\\t':' ',
            '\\r':' ',
            '\r':' ',
            '\\u2019':"'",
            '\\u2018':"'",
            '\u2019':"'",
            '\u2018':"'",
            '\xa0':' ',
            '\\xa0':' ',
            '\\u2026':' ',
            '\u2026':' ',
            '\u201c':"''",
            '\\u201c':"''",
            '\xe9':'é',
            '\\xe9':'é',
            '\\xed':'í',
            '\xed':'í',
            '\xf3':'ó',
            '\\xf3':'ó',
            '\\xe1':'á',
            '\xe1':'á',
            '\xf1':'ñ',
            '\\xf1':'ñ',
            '\\u2013':'-',
            '\\\u201d':"'",
            '\\u2014':'-',
            '\\xe0':'à',
            '\\xe8':'è',
            '---------- Forwarded message ---------':'',
            'Sent from my iPhone':'',
            'Subject:':'',

            '\\xf4':'ô',

            '---- Original Message ----':'',
            'Forwarded Message':'',
            'Original Message':'',
            '\\u2022 ':'',
            '\\xa9':'',
            '\\xbf':'¿',
            '\\xc1':'Á',
            '\\xdal':'Ú',
            '\\xfa':'ú',
            '\\xae':'',
            '\u2192':'',
            '...':'.',
            "If you're having trouble viewing this email, you may see it online. Share this:":''
            ,'¿':' ¿ '
            ,'¡':' ¡ '
            ,'.':' . '
            ,',':' , '
            ,'!':' ! '
            ,'?':' ? '
            ,'(':' ( '
            ,')':' ) '
            ,':':' : '}

sample = """<html><head><meta http-equiv=\\"content-type\\" content=\\"text/html; charset=utf-8\\"></head><body dir=\\"auto\\">Provvedi<br><br><div dir=\\"ltr\\">Inviato da iPhone</div><div dir=\\"ltr\\"><br>Inizio messaggio inoltrato:<br><br></div><blockquote type=\\"cite\\"><div dir=\\"ltr\\"><b>Da:</b> purchasing@sirti.it<br><b>Data:</b> 4 novembre 2020 13:14:27 CET<br><b>A:</b> amministrazione@igeimpianti.com<br><b>Cc:</b> c.venuso@sirti.it<br><b>Oggetto:</b> <b>Contratto 4600004939</b><br><br></div></blockquote><blockquote type=\\"cite\\"><div dir=\\"ltr\\">\\ufeff\\r\\n\\r\\n\\r\\n\\r\\n  <meta content=\\"HTML Tidy for SAP R/3 (vers 25 March 2009), see www.w3.org\\" name=\\"generator\\">\\r\\n\\r\\n  <title></title>\\r\\n\\r\\n\\r\\n\\r\\n <p>Gentile fornitore,</p>p&gt;Gentile fornitore,<p></p>\\r\\n\\r\\n <p>la informiamo che il documento d\'acquisto 4600004939 registrato in data 20200929, \\u00e8 stato pubblicato nel Portale del Gruppo Sirti.</p>\\r\\n\\r\\n\\r\\n <p>Documento PDF firmato digitalmente e allegati ufficiali sono al link: </p>\\r\\n\\r\\n <p>https://extranet.portale.sirti.net/APPLICAZIONI/AE02</p>\\r\\n\\r\\n <p>Tramite le funzionalit\\u00e0 del Portale il documento dovr\\u00e0 essere accettato e ricaricato firmato.</p>\\r\\n\\r\\n \\r\\n<p>Per qualsiasi domanda riferirsi al buyer indicato in calce oppure consultare il manuale d\'uso presente nella Home Page dell\'applicazione di cui al link.</p>\\r\\n\\r\\n <p>Cordiali saluti<br></p>\\r\\n\\r\\n <p>Carmine Venuso</p>\\r\\n\\r\\n  <p></p>\\r\\n\\r\\n  <p></p>\\r\\n\\r\\n  <p>PS: I documenti di tipo Call-Off, nella fascia 47xxxxxxxx, non devono essere accettati. </p>\\r\\n\\r\\n\\r\\n</div></blockquote></body></html><html><head><meta http-equiv=\\"content-type\\" content=\\"text/html; charset=us-ascii\\"></head><body dir=\\"auto\\"><blockquote type=\\"cite\\"><div dir=\\"ltr\\"></div></blockquote></body></html><html xmlns:v=\\"urn:schemas-microsoft-com:vml\\" xmlns:o=\\"urn:schemas-microsoft-com:office:office\\" xmlns:w=\\"urn:schemas-microsoft-com:office:word\\" xmlns:m=\\"http://schemas.microsoft.com/office/2004/12/omml\\" xmlns=\\"http://www.w3.org/TR/REC-html40\\"><head><meta http-equiv=Content-Type content=\\"text/html; charset=utf-8\\"><meta name=Generator content=\\"Microsoft Word 15 (filtered medium)\\"><style><!--\\r\\n/* Font Definitions */\\r\\n@font-face\\r\\n\\t{font-family:\\"Cambria Math\\";\\r\\n\\tpanose-1:2 4 5 3 5 4 6 3 2 4;}\\r\\n@font-face\\r\\n\\t{font-family:Calibri;\\r\\n\\tpanose-1:2 15 5 2 2 2 4 3 2 4;}\\r\\n/* Style Definitions */\\r\\np.MsoNormal, li.MsoNormal, div.MsoNormal\\r\\n\\t{margin:0cm;\\r\\n\\tfont-size:11.0pt;\\r\\n\\tfont-family:\\"Calibri\\",sans-serif;}\\r\\na:link, span.MsoHyperlink\\r\\n\\t{mso-style-priority:99;\\r\\n\\tcolor:#0563C1;\\r\\n\\ttext-decoration:underline;}\\r\\nspan.StileMessaggioDiPostaElettronica20\\r\\n\\t{mso-style-type:personal-reply;\\r\\n\\tfont-family:\\"Calibri\\",sans-serif;\\r\\n\\tcolor:windowtext;}\\r\\n.MsoChpDefault\\r\\n\\t{mso-style-type:export-only;\\r\\n\\tfont-size:10.0pt;}\\r\\n@page WordSection1\\r\\n\\t{size:612.0pt 792.0pt;\\r\\n\\tmargin:72.0pt 72.0pt 72.0pt 72.0pt;}\\r\\ndiv.WordSection1\\r\\n\\t{page:WordSection1;}\\r\\n--></style><!--[if gte mso 9]><xml>\\r\\n<o:shapedefaults v:ext=\\"edit\\" spidmax=\\"1026\\" />\\r\\n</xml><![endif]--><!--[if gte mso 9]><xml>\\r\\n<o:shapelayout v:ext=\\"edit\\">\\r\\n<o:idmap v:ext=\\"edit\\" data=\\"1\\" />\\r\\n</o:shapelayout></xml><![endif]--></head><body lang=EN-GB link=\\"#0563C1\\" vlink=\\"#954F72\\" style=\'word-wrap:break-word\'><div class=WordSection1><p class=MsoNormal><span style=\'mso-fareast-language:EN-US\'>Imma provvedi \\u2026grazie<o:p></o:p></span></p><p class=MsoNormal><span style=\'mso-fareast-language:EN-US\'><o:p>&nbsp;</o:p></span></p><div><div style=\'border:none;border-top:solid #E1E1E1 1.0pt;padding:3.0pt 0cm 0cm 0cm\'><p class=MsoNormal><b><span lang=IT>Da:</span></b><span lang=IT> purchasing@sirti.it &lt;purchasing@sirti.it&gt; <br><b>Inviato:</b> 02 November 2020 12:04<br><b>A:</b> amministrazione@igeimpianti.com<br><b>Cc:</b> d.donzelli@sirti.it<br><b>Oggetto:</b> Contratto 4600004049<o:p></o:p></span></p></div></div><p class=MsoNormal><o:p>&nbsp;</o:p></p><p>Gentile fornitore,<o:p></o:p></p><p class=MsoNormal>p&gt;Gentile fornitore,<o:p></o:p></p><p>la informiamo che il documento d\'acquisto 4600004049 registrato in data 20200402, \\u00e8 stato pubblicato nel Portale del Gruppo Sirti.<o:p></o:p></p><p>Documento PDF firmato digitalmente e allegati ufficiali sono al link: <o:p></o:p></p><p><a href=\\"https://extranet.portale.sirti.net/APPLICAZIONI/AE02\\">https://extranet.portale.sirti.net/APPLICAZIONI/AE02</a><o:p></o:p></p><p>Tramite le funzionalit\\u00e0 del Portale il documento dovr\\u00e0 essere accettato e ricaricato firmato.<o:p></o:p></p><p>Per qualsiasi domanda riferirsi al buyer indicato in calce oppure consultare il manuale d\'uso presente nella Home Page dell\'applicazione di cui al link.<o:p></o:p></p><p>Cordiali saluti<o:p></o:p></p><p>Carmine Venuso<o:p></o:p></p><p>PS: I documenti di tipo Call-Off, nella fascia 47xxxxxxxx, non devono essere accettati. <o:p></o:p></p></div></body></html><html xmlns:v=\\"urn:schemas-microsoft-com:vml\\" xmlns:o=\\"urn:schemas-microsoft-com:office:office\\" xmlns:w=\\"urn:schemas-microsoft-com:office:word\\" xmlns:m=\\"http://schemas.microsoft.com/office/2004/12/omml\\" xmlns=\\"http://www.w3.org/TR/REC-html40\\"><head><meta http-equiv=Content-Type content=\\"text/html; charset=utf-8\\"><meta name=Generator content=\\"Microsoft Word 15 (filtered medium)\\"><!--[if !mso]><style>v\\\\:* {behavior:url(#default#VML);}\\r\\no\\\\:* {behavior:url(#default#VML);}\\r\\nw\\\\:* {behavior:url(#default#VML);}\\r\\n.shape {behavior:url(#default#VML);}\\r\\n</style><![endif]--><style><!--\\r\\n/* Font Definitions */\\r\\n@font-face\\r\\n\\t{font-family:\\"Cambria Math\\";\\r\\n\\tpanose-1:2 4 5 3 5 4 6 3 2 4;}\\r\\n@font-face\\r\\n\\t{font-family:Calibri;\\r\\n\\tpanose-1:2 15 5 2 2 2 4 3 2 4;}\\r\\n@font-face\\r\\n\\t{font-family:\\"Trebuchet MS\\";\\r\\n\\tpanose-1:2 11 6 3 2 2 2 2 2 4;}\\r\\n@font-face\\r\\n\\t{font-family:\\"Arial Black\\";\\r\\n\\tpanose-1:2 11 10 4 2 1 2 2 2 4;}\\r\\n/* Style Definitions */\\r\\np.MsoNormal, li.MsoNormal, div.MsoNormal\\r\\n\\t{margin:0cm;\\r\\n\\tfont-size:11.0pt;\\r\\n\\tfont-family:\\"Calibri\\",sans-serif;}\\r\\na:link, span.MsoHyperlink\\r\\n\\t{mso-style-priority:99;\\r\\n\\tcolor:#0563C1;\\r\\n\\ttext-decoration:underline;}\\r\\nspan.StileMessaggioDiPostaElettronica19\\r\\n\\t{mso-style-type:personal-reply;\\r\\n\\tfont-family:\\"Calibri\\",sans-serif;\\r\\n\\tcolor:windowtext;}\\r\\n.MsoChpDefault\\r\\n\\t{mso-style-type:export-only;\\r\\n\\tfont-size:10.0pt;}\\r\\n@page WordSection1\\r\\n\\t{size:612.0pt 792.0pt;\\r\\n\\tmargin:72.0pt 72.0pt 72.0pt 72.0pt;}\\r\\ndiv.WordSection1\\r\\n\\t{page:WordSection1;}\\r\\n--></style><!--[if gte mso 9]><xml>\\r\\n<o:shapedefaults v:ext=\\"edit\\" spidmax=\\"1026\\" />\\r\\n</xml><![endif]--><!--[if gte mso 9]><xml>\\r\\n<o:shapelayout v:ext=\\"edit\\">\\r\\n<o:idmap v:ext=\\"edit\\" data=\\"1\\" />\\r\\n</o:shapelayout></xml><![endif]--></head><body bgcolor=\\"#CCCCCC\\" lang=EN-GB link=\\"#0563C1\\" vlink=\\"#954F72\\" style=\'word-wrap:break-word\'><div class=WordSection1><p class=MsoNormal><span style=\'mso-fareast-language:EN-US\'><o:p>&nbsp;</o:p></span></p><p class=MsoNormal><span style=\'mso-fareast-language:EN-US\'><o:p>&nbsp;</o:p></span></p><div><div style=\'border:none;border-top:solid #E1E1E1 1.0pt;padding:3.0pt 0cm 0cm 0cm\'><p class=MsoNormal><b><span lang=IT>Da:</span></b><span lang=IT> navision@sielte.it &lt;navision@sielte.it&gt; <br><b>Inviato:</b> 29 October 2020 18:15<br><b>A:</b> amministrazione@igeimpianti.com<br><b>Oggetto:</b> Riepilogo Operazioni Navision Sielte S.p.A.<o:p></o:p></span></p></div></div><p class=MsoNormal><o:p>&nbsp;</o:p></p><div align=center><table class=MsoNormalTable border=1 cellspacing=0 cellpadding=0 style=\'background:white;border:solid #005CB7 1.0pt\'><tr><td colspan=4 style=\'border:none;padding:0cm 7.5pt 0cm 0cm\'><p class=MsoNormal><span style=\'font-size:8.0pt;font-family:\\"Trebuchet MS\\",sans-serif;color:#045FB8\'><img width=250 height=55 style=\'width:2.6041in;height:.5729in\' id=\\"_x0000_i1027\\" src=\\"http://www.sielte.it/images/logo_ms_dynamics.gif\\"></span><span style=\'font-size:8.0pt;font-family:\\"Trebuchet MS\\",sans-serif;color:#045FB8\'><o:p></o:p></span></p></td></tr><tr><td colspan=4 style=\'border:none;padding:7.5pt 7.5pt 0cm 7.5pt\'><p class=MsoNormal><span style=\'font-size:8.0pt;font-family:\\"Trebuchet MS\\",sans-serif;color:#045FB8\'>Gentile <a href=\\"mailto:amministrazione@igeimpianti.com\\">amministrazione@igeimpianti.com</a>,<o:p></o:p></span></p></td></tr><tr><td colspan=4 style=\'border:none;padding:0cm 7.5pt 0cm 7.5pt\'><p class=MsoNormal><span style=\'font-size:8.0pt;font-family:\\"Trebuchet MS\\",sans-serif;color:#045FB8\'>Sono state pubblicate sul Portale Sielte le seguenti informazioni:<o:p></o:p></span></p></td></tr><tr style=\'height:26.25pt\'><td width=150 style=\'width:112.5pt;border:none;padding:15.0pt 7.5pt 0cm 7.5pt;height:26.25pt\'><p class=MsoNormal><b><span style=\'font-size:8.0pt;font-family:\\"Trebuchet MS\\",sans-serif;color:#045FB8\'>Tipo Documento<o:p></o:p></span></b></p></td><td width=150 style=\'width:112.5pt;border:none;padding:15.0pt 7.5pt 0cm 7.5pt;height:26.25pt\'><p class=MsoNormal><b><span style=\'font-size:8.0pt;font-family:\\"Trebuchet MS\\",sans-serif;color:#045FB8\'>Nr. Documento<o:p></o:p></span></b></p></td><td width=150 style=\'width:112.5pt;border:none;padding:15.0pt 7.5pt 0cm 7.5pt;height:26.25pt\'><p class=MsoNormal><b><span style=\'font-size:8.0pt;font-family:\\"Trebuchet MS\\",sans-serif;color:#045FB8\'>Data Pubblicazione<o:p></o:p></span></b></p></td><td width=320 style=\'width:240.0pt;border:none;padding:15.0pt 7.5pt 0cm 7.5pt;height:26.25pt\'><p class=MsoNormal><b><span style=\'font-size:8.0pt;font-family:\\"Trebuchet MS\\",sans-serif;color:#045FB8\'>Descrizione<o:p></o:p></span></b></p></td></tr><tr><td colspan=4 style=\'border:none;padding:0cm 7.5pt 0cm 7.5pt\'><div class=MsoNormal align=center style=\'text-align:center\'><span style=\'font-size:8.0pt;font-family:\\"Trebuchet MS\\",sans-serif;color:#045FB8\'><hr size=2 width=\\"100%\\" align=center></span></div></td></tr><tr><td width=150 style=\'width:112.5pt;border:none;background:#E3EEFA;padding:0cm 7.5pt 0cm 7.5pt\'><p class=MsoNormal><span style=\'font-size:8.0pt;font-family:\\"Trebuchet MS\\",sans-serif;color:#045FB8\'>Ordine<o:p></o:p></span></p></td><td width=150 style=\'width:112.5pt;border:none;background:#E3EEFA;padding:0cm 7.5pt 0cm 7.5pt\'><p class=MsoNormal><span style=\'font-size:8.0pt;font-family:\\"Trebuchet MS\\",sans-serif;color:#045FB8\'>20/0018213<o:p></o:p></span></p></td><td width=150 style=\'width:112.5pt;border:none;background:#E3EEFA;padding:0cm 7.5pt 0cm 7.5pt\'><p class=MsoNormal><span style=\'font-size:8.0pt;font-family:\\"Trebuchet MS\\",sans-serif;color:#045FB8\'>29/10/20 17:47<o:p></o:p></span></p></td><td width=320 style=\'width:240.0pt;border:none;background:#E3EEFA;padding:0cm 7.5pt 0cm 7.5pt\'><p class=MsoNormal><span style=\'font-size:8.0pt;font-family:\\"Trebuchet MS\\",sans-serif;color:#045FB8\'>Pubblicato<o:p></o:p></span></p></td></tr><tr><td width=150 style=\'width:112.5pt;border:none;padding:0cm 7.5pt 0cm 7.5pt\'><p class=MsoNormal><span style=\'font-size:8.0pt;font-family:\\"Trebuchet MS\\",sans-serif;color:#045FB8\'>Ordine<o:p></o:p></span></p></td><td width=150 style=\'width:112.5pt;border:none;padding:0cm 7.5pt 0cm 7.5pt\'><p class=MsoNormal><span style=\'font-size:8.0pt;font-family:\\"Trebuchet MS\\",sans-serif;color:#045FB8\'>20/0018214<o:p></o:p></span></p></td><td width=150 style=\'width:112.5pt;border:none;padding:0cm 7.5pt 0cm 7.5pt\'><p class=MsoNormal><span style=\'font-size:8.0pt;font-family:\\"Trebuchet MS\\",sans-serif;color:#045FB8\'>29/10/20 17:47<o:p></o:p></span></p></td><td width=320 style=\'width:240.0pt;border:none;padding:0cm 7.5pt 0cm 7.5pt\'><p class=MsoNormal><span style=\'font-size:8.0pt;font-family:\\"Trebuchet MS\\",sans-serif;color:#045FB8\'>Pubblicato<o:p></o:p></span></p></td></tr><tr><td colspan=4 style=\'border:none;padding:15.0pt 7.5pt 15.0pt 7.5pt\'><p class=MsoNormal><span style=\'font-size:8.0pt;font-family:\\"Trebuchet MS\\",sans-serif;color:#045FB8\'>Non rispondere a questo messaggio. Questa casella E-Mail non \\u00e8 monitorata e non verr\\u00e0 inviata alcuna risposta.<o:p></o:p></span></p></td></tr><tr><td colspan=4 style=\'border:none;background:#00256B;padding:7.5pt 7.5pt 0cm 7.5pt\'><p class=MsoNormal align=right style=\'text-align:right\'><span style=\'font-size:10.0pt;font-family:\\"Arial Black\\",sans-serif;color:white\'>Portale Sielte S.p.A.<o:p></o:p></span></p></td></tr></table></div><p class=MsoNormal><o:p>&nbsp;</o:p></p></div></body></html>"""

print( ClearTextBefore(sample) )
