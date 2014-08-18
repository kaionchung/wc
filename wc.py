#!/usr/bin/python
# -*- coding: utf-8 -*-
from ConfigParser import SafeConfigParser
from Crypto.Cipher import AES
from pkcs7 import *
import StringIO
import gzip
import json
import sys
import base64
import urllib2
import zlib
import time
import cookielib

DEBUG = False #False #True

ENABLE_PROXY = True
PROXY_SERVER = 'http://192.168.11.1:8080'

configFile = 'wc.conf'
config = SafeConfigParser()

WC_APP_VERSION = '1.0.5'
WC_APP_KEY = "AZfzBz3h#u0kxRxbPgn5c@VCl1HelEB#"
WC_APP_IV =  "zVd#ByDcQFBq#Gd5"

false = False
true = True
  
def wc_request(session,endpoint,data=None):
  cookies = cookielib.CookieJar()
  if ENABLE_PROXY:
    proxy_handler = urllib2.ProxyHandler({"http" : PROXY_SERVER})
  else:
    proxy_handler = urllib2.ProxyHandler({})
  opener = urllib2.build_opener(proxy_handler,urllib2.HTTPCookieProcessor(cookies))
  
  if session is None:
    uh = None
    cookie = ''
  else:
    uh = session['uh']
    cookie = session['cookie']  

#  POST http://wcat.colopl.jp/ajax/regist/checkregister HTTP/1.1
  headers = { 
    'X-Unity-Version' : '4.5.0f6',
    'Content-Type' : 'application/x-www-form-urlencoded',
    'apv' : WC_APP_VERSION,
    'Cookie ' : cookie,
    'User-Agent' : 'Dalvik/1.6.0 (Linux; U; Android 4.4.4; C6806_GPe Build/KTU84P.S1)',
#    'Connection' : 'Keep-Alive',
    'Accept-Encoding' : 'gzip',
#    'Content-Length': '8'
    'Host' : 'wcat.colopl.jp',
  }
#  print session
  if data is not None:
    data = 'data=' + quote(wc_encrypt(data,uh)) + '&' 
  else:
    data = ''
  data += 'app=wcat'
#  print data
#  exit()
  url = 'http://wcat.colopl.jp/' + endpoint 
  req = urllib2.Request(url, data, headers)
  response = opener.open(req)
  
  for item in cookies:
    set_conf('cookie', item.name, item.value.rstrip('%3A1'))
    
  if response.info().get('Content-Encoding') == 'gzip':
    buf = StringIO.StringIO( response.read() )
    f = gzip.GzipFile(fileobj=buf)
    response_data = f.read()
  else:
    response_data = response.read()
    
  response_json = json.loads(zlib.decompress(wc_decrypt(response_data,uh)))
  if DEBUG :
    print_color(response_json,"1;33")
    
  return response_json
    
def get_conf(section,option):
  config.read(configFile)
  if not config.has_section(section): 
    return None
  elif not config.has_option(section, option):
    return None
  return config.get(section, option)
  
def set_conf(section,option,value):
  config.read(configFile)
  if not config.has_section(section): 
    config.add_section(section)
  config.set(section, option, value)
  fp = open(configFile, 'wb')
  config.write(fp)
  return config.get(section, option)
  
def quote(s, safe = ''):
  always_safe = ('ABCDEFGHIJKLMNOPQRSTUVWXYZ'
                 'abcdefghijklmnopqrstuvwxyz'
                 '0123456789' '_.-')
  safe = always_safe + safe
  if s == None:
    print 'WARRING: quote(s), s is not None!'
    return 'NONE'
  res = list(s)
  for i in range(len(res)):
    c = res[i]
    if c not in safe:
     res[i] = '%%%02x' % ord(c)
  return ''.join(res)

def wc_decrypt(secret_text, key_text = None, iv_text = None):
  if key_text is None:
    key_text = WC_APP_KEY
  if iv_text is None:
    iv_text = WC_APP_IV
  mode = AES.MODE_CBC
  cipher_text = base64.b64decode(secret_text)
  f = AES.new(key_text, mode, iv_text)
  padded_text = f.decrypt(cipher_text)
  encoder = PKCS7Encoder()
  return encoder.decode(padded_text)
  
def wc_encrypt(text, key_text = None, iv_text = None):
  if key_text is None:
    key_text = WC_APP_KEY
  if iv_text is None:
    iv_text = WC_APP_IV
  encoder = PKCS7Encoder()
  padded_text = encoder.encode(text)
  #print "".join("{:02x}".format(ord(c)) for c in padded_text)
  mode = AES.MODE_CBC
  f = AES.new(key_text, mode, iv_text)
  cipher_text = f.encrypt(padded_text)
  return base64.b64encode(cipher_text)

def generate_qt():
  import uuid
  return str(uuid.uuid4()).replace('-', '')
     
def print_color(target,color=33):
  if type(target) is dict:
    print '\033[0;' + str(color) + 'm' + json.dumps(target, ensure_ascii=False).encode('utf8').replace('\\"', '"').replace(', ', ',').replace(': ', ':') + '\033[m'
    print '---------------------------------------------------------------------'
  else:
    print '\033[0;' + str(color) + 'm' + target + '\033[m'
    print '---------------------------------------------------------------------'

def wc_load_session():
  session = {}
  session['cookie'] = 'wcatpt=' + get_conf('cookie','wcatpt') + '%3A1'
  session['uh'] = get_conf('device','uh')
  return session  
               
def main():
  if not len(sys.argv) >= 2:
    return
    
  elif sys.argv[1] == 'decrypt' or sys.argv[1] == 'de':
    if not len(sys.argv) == 2:
      print 'wc decrypt [data] [uh]'
      return
    if len(sys.argv) >= 4:
      uh = sys.argv[3]
    else:
      uh = None
    print uh
    res = sys.argv[2].find('app=wcat')
    if res == -1:
      text = wc_decrypt(sys.argv[2],uh)
    else:
      tempArray = sys.argv[2].split('&')
      raw = ''
      for temp in tempArray:
        res = temp.find('data')
        if res >= 0:
          target = urllib2.unquote(temp.split('=')[1])
          text = wc_decrypt(target,uh)
          break  
    try:
      text2 = json.loads( zlib.decompress(text) ) 
    except:
      text2 = text
    print_color(text2)

  elif sys.argv[1] == 'takeover' or sys.argv[1] == 'ta':
    session = wc_load_session()
    print_color(wc_request(session,'ajax/regist/createwcataccount','{"email":"' + get_conf('device','id') + '@wcat.co.jp","password":"1234qwer","confirmPassword":"1234qwer","secretQuestionType":7,"secretQuestionAnswer":"kawasaki"}'))
  
  elif sys.argv[1] == 'tutorial' or sys.argv[1] == 'tu':

    resp = wc_request(None,'ajax/regist/create', '{"d":"b0edac6f610d2fda75e2c8763372f8b3b24a39e97b2bdf69e2eccbda1e250fb37e96b91d6e81612b0e576c113366186a","fromCode":"","fromParam":"","fromAffiliate":""}')
    set_conf('device', 'uh', resp["result"]["uh"])
    set_conf('device', 'id', str(resp["result"]["userInfo"]["id"]))

    session = wc_load_session()
    print_color(session)
    
    wc_request(session,'ajax/assetbundle/version', None)    
    wc_request(session,'ajax/deck/defaultweapon', None)
    wc_request(session,'ajax/quest/getdream', None)
    
    qt = generate_qt()
    wc_request(session,'ajax/quest/generate','{"qt":"' + qt + '","qid":9999999,"did":0,"fid":6877844,"fcid":10100440,"hard":0}') 

    qt = generate_qt()
    wc_request(session,'ajax/quest/generate','{"qt":"' + qt + '","qid":1,"did":0,"fid":1,"fcid":10400010,"hard":0}')
    time.sleep(10)
    wc_request(session,'ajax/quest/complete', '{"qt":"' + qt + '","gold":324,"soul":23,"cardIds":[],"weaponIds":[],"ornamentIds":[],"itemIds":[100110,100110,100110],"destroyEnemyIds":[1,2,3,6,4,5,8,7,12,10,11,13,9,14],"destroyObjectIds":[],"openTreasureIds":[1,2],"totalDamageCount":3,"totalDamageAmount":5,"totalDamageCountFromPlacementObject":0,"totalDeadCount":0,"totalHelperDeadCount":0,"totalBadStatusCount":0,"totalActionSkillUseCount":0,"totalAllAttackUseCount":0,"isDestroyBossAtActionSkill":false,"isDestroyBossAtAllAttack":false,"maxChainNum":0,"routeId":0}')

    wc_request(session,'ajax/user/updatename', '{"name":"カオル"}')
    wc_request(session,'ajax/quest/talkread', '{"qid":1,"baType":1,"hard":0}')
    wc_request(session,'ajax/quest/talkread', '{"qid":2,"baType":0,"hard":0}')

    qt = generate_qt()
    wc_request(session,'ajax/quest/generate', '{"qt":"' + qt + '","qid":2,"did":0,"fid":2325920,"fcid":20600000,"hard":0}')
    time.sleep(10)
    wc_request(session,'ajax/quest/complete', '{"qt":"' + qt + '","gold":343,"soul":22,"cardIds":[],"weaponIds":[],"ornamentIds":[],"itemIds":[100110,100310],"destroyEnemyIds":[16,17,21,23,19,20,18,22,15,24,30,25,27,29,26,28,32,33,31,34],"destroyObjectIds":[],"openTreasureIds":[3],"totalDamageCount":5,"totalDamageAmount":20,"totalDamageCountFromPlacementObject":0,"totalDeadCount":0,"totalHelperDeadCount":0,"totalBadStatusCount":0,"totalActionSkillUseCount":0,"totalAllAttackUseCount":0,"isDestroyBossAtActionSkill":false,"isDestroyBossAtAllAttack":false,"maxChainNum":0,"routeId":0}')

    qt = generate_qt()
    wc_request(session,'ajax/quest/generate', '{"qt":"' + qt + '","qid":3,"did":0,"fid":2762707,"fcid":10100000,"hard":0}')
    time.sleep(10)
    wc_request(session,'ajax/quest/complete', '{"qt":"' + qt + '","gold":479,"soul":28,"cardIds":[],"weaponIds":[],"ornamentIds":[],"itemIds":[100610,100110,100110,100110,100410,100110,100410],"destroyEnemyIds":[36,44,40,41,39,43,42,37,38,45,46,53,54,52,47,49,51,50,48,57,56,55,60,61,59,58],"destroyObjectIds":[],"openTreasureIds":[4,5],"totalDamageCount":17,"totalDamageAmount":95,"totalDamageCountFromPlacementObject":0,"totalDeadCount":0,"totalHelperDeadCount":0,"totalBadStatusCount":0,"totalActionSkillUseCount":0,"totalAllAttackUseCount":0,"isDestroyBossAtActionSkill":false,"isDestroyBossAtAllAttack":false,"maxChainNum":0,"routeId":0}')

    wc_request(session,'ajax/quest/talkread', '{"qid":2,"baType":1,"hard":0}')   
    wc_request(session,'ajax/quest/talkread', '{"qid":3,"baType":1,"hard":0}')

    weapon_resp = wc_request(session,'ajax/gacha/weaponexe', '{"gId":100,"nowCrystal":0}')
    print_color(weapon_resp,"1;32")
    wc_request(session,'ajax/deck/compoweapon', '{"uwId":"' + weapon_resp["result"]["weapon"]["uwId"] + '"}')
 
    qt = generate_qt() 
    wc_request(session,'ajax/quest/generate', '{"qt":"' + qt + '","qid":108,"did":0,"fid":2781705,"fcid":10100000,"hard":0}')
    time.sleep(10)
    wc_request(session,'ajax/quest/complete', '{"qt":"' + qt + '","gold":593,"soul":39,"cardIds":[],"weaponIds":[],"ornamentIds":[],"itemIds":[100110,100110,100110,100110,100510,100410,100110,100110,100410,100410],"destroyEnemyIds":[2944,2947,2950,2952,2949,2953,2946,2951,2945,2954,2948,2955,2959,2958,2957,2963,2956,2962,2961,2964,2965,2960,2970,2969,2968,2967,2966,2975,2974,2971,2972,2973],"destroyObjectIds":[],"openTreasureIds":[275,277,276],"totalDamageCount":17,"totalDamageAmount":91,"totalDamageCountFromPlacementObject":0,"totalDeadCount":0,"totalHelperDeadCount":0,"totalBadStatusCount":0,"totalActionSkillUseCount":0,"totalAllAttackUseCount":0,"isDestroyBossAtActionSkill":false,"isDestroyBossAtAllAttack":false,"maxChainNum":0,"routeId":0}')
    
    gacha1_resp = wc_request(session,'ajax/gacha/exe', '{"id":100,"nowCrystal":0}')
    print_color(gacha1_resp, '1;32')

    wc_request(session,'ajax/quest/talkread', '{"qid":5,"baType":0,"hard":0}')	
    while True:
      presents = wc_request(session,'ajax/present/list', '{"page":0}')
      ids = []
      for present in presents["result"]["userPresents"]:
        ids.append(present["id"])
      if ids == []:
        break
      wc_request(session,'ajax/present/receive', '{"ids":' + str(ids).replace('u\'', '\"').replace('\'', '"').replace(' ', '') + '}')
    
    gacha2_resp = wc_request(session,'ajax/gacha/exe', '{"id":2,"nowCrystal":25}')
    print_color(gacha2_resp, '1;32')
    

if __name__ == "__main__":
  main()
