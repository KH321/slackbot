from slackbot.bot import respond_to     # @botname: で反応するデコーダ
from slackbot.bot import listen_to      # チャネル内発言で反応するデコーダ
from slackbot.bot import default_reply  # 該当する応答がない場合に反応するデコーダ

import requests, re, random, os
from bs4 import BeautifulSoup

from dotenv import load_dotenv
load_dotenv()

import gspread
from oauth2client.service_account import ServiceAccountCredentials

members = {
  '金村 美玖': 'kanemura.miku',
  '小坂 菜緒': 'kosaka.nao',
  '齊藤 京子': 'saitou.kyouko',
}
members_nicknames = {
  'お寿司': members['金村 美玖'],
  'こさかな': members['小坂 菜緒'],
  'ラーメン': members['齊藤 京子'],
}

scope = ['https://spreadsheets.google.com/feeds',
         'https://www.googleapis.com/auth/drive']
credential_obj = {
    "type": "service_account",
    "project_id": os.environ['project_id'],
    "private_key_id": os.environ['private_key_id'],
    "private_key": os.environ['private_key'],
    "client_email": os.environ['client_email'],
    "client_id": os.environ['client_id'],
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_x509_cert_url": os.environ['client_x509_cert_url']
}

credentials = ServiceAccountCredentials.from_json_keyfile_dict(credential_obj, scope)
gc = gspread.authorize(credentials)

# ワークシートがあればそのまま、なければ作成して返す
def get_ws(book_name, target_title):
  sh = gc.open(book_name)
  ws = sh.worksheets()
  mws = ''
  for sheet in ws:
    if(sheet.title == str(target_title)):
      mws = sh.worksheet(sheet.title)

  if(mws == ''):
    sh.add_worksheet(title = str(target_title), rows = 2000, cols = 20)
    mws = sh.worksheet(str(target_title))
  return mws

def update_spread(imgs, name):
  ws = get_ws('hinata', members[name])
  cell_list = ws.col_values(1)
  print('A' + str(len(cell_list) + 1) + ':A' + str(len(cell_list) + len(imgs)))
  if len(cell_list) + len(imgs) > ws.row_count:
    ws.add_rows(len(cell_list) + len(imgs) - ws.row_count)
  cell_list = ws.range('A' + str(len(cell_list) + 1) + ':A' + str(len(cell_list) + len(imgs)))
  print(cell_list)
  for i, cell in enumerate(cell_list):
    cell.value = imgs[i]

  ws.update_cells(cell_list)

def get_url(name, num=1):
  if num > 46:
    num = 46
  ws = get_ws('hinata', members_nicknames[name])
  cell_list = ws.col_values(1)
#   cell_value = ws.cell(random.randint(1, len(cell_list)), 1).value
  cell_value = [ws.cell(random.randint(1, len(cell_list)), 1).value for i in range(num)]
  print(cell_value)
  return cell_value

headers = {"User-Agent": "Mozilla/5.0"}
pattern = "https?://www.hinatazaka46.com[\w/:%#\$&\(\)~\.=\+\-]+"

@respond_to(r'.*https?://www.hinatazaka46.com/s/official/diary.*')
@listen_to(r'.*https?://www.hinatazaka46.com/s/official/diary.*')
def listen_func(message):
  text = message.body['text']
  url_list = re.findall(pattern, text)
  soup = BeautifulSoup(requests.get(url_list[0], headers=headers).content, 'html.parser')
  imgs = [url.get('src') for url in soup.select('.p-blog-group img')]
  for img in imgs:
    message.send(img)
    print(img)
  for name in members:
    if re.search(name, text):
      update_spread(imgs, name)
      break

@respond_to('ラーメン大好き')
def ramen_func(message):
    message.reply('齊藤京子です！')  # メンション

all_or_nickname = '|'.join(members_nicknames.keys())  # eg. "お寿司|こさかな|ラーメン"
@respond_to(fr'[\s\S]*({all_or_nickname})')
def img_func(message, re_name=''):
  num = re.findall('[0-9]+', message.body['text'])
  if len(num) == 0:
    message.send(get_url(re_name)[0])
  else:
    for url in get_url(re_name, int(num[0])):
      message.send(url)

count = 0
@default_reply()
def default_func(message):
    print(message.body['text'])
    global count        # 外で定義した変数の値を変えられるようにする
    count += 1
    message.reply('%d ラーメン大好き' % count)  # メンション


# @respond_to(r'(?=[\s\S]*(金村 美玖|小坂 菜緒))(?=[\s\S]*https?://www.hinatazaka46.com[\w/:%#\$&\(\)~\.=\+\-]+)')
# @listen_to(r'(?=[\s\S]*(金村 美玖|小坂 菜緒))(?=[\s\S]*https?://www.hinatazaka46.com[\w/:%#\$&\(\)~\.=\+\-]+)')
# def listen_func(message):
#     text = message.body['text']
#     url_list = re.findall(pattern, text)
#     soup = BeautifulSoup(requests.get(url_list[0], headers=headers).content, 'html.parser')
#     for img in [url.get('src') for url in soup.select('.p-blog-group img')]:
#       message.send(img)
#       print(img)
