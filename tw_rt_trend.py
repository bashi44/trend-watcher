# モジュールインポート
# twitter api
import tweepy
# 必要な標準モジュール
import time
import requests
import json
import os

# tweepy 設定
TWITTER_API_KEY = os.environ['TWITTER_API_KEY']
TWITTER_API_KEY_SECRET = os.environ['TWITTER_API_KEY_SECRET']
TWITTER_ACCESS_TOKEN = os.environ['TWITTER_ACCESS_TOKEN']
TWITTER_ACCESS_TOKEN_SECRET = os.environ['TWITTER_ACCESS_TOKEN_SECRET']
auth = tweepy.OAuthHandler(TWITTER_API_KEY, TWITTER_API_KEY_SECRET)
auth.set_access_token(TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_TOKEN_SECRET)
api = tweepy.API(auth)
woeid = {
  '日本': 23424856
}

# twitter 現在のトレンド30件取得
trends_list = {}
for area, wid in woeid.items():
  trends = api.trends_place(wid)[0]
  for i, content in enumerate(trends['trends']):
    trends_list[i] = content['name']
    if i == 28:
      break
# jsonファイルを読み込み
json_open = open('tw_keywords.json', 'r')
key_words = json.load(json_open)
# トレンドとjsonファイルの内容を比較
match_words_list = []
for value1 in key_words.values():
  for value2 in trends_list.values():
    if value1 == value2:
      match_words_list.append(value1)
# 重複するキーワードを削除
match_words_list = set(match_words_list)
# 現在トレンド入りしているjsonキーワードが含まれるツイート50件検索
if len(match_words_list) != 0:
  count = 50
  for value in match_words_list:
    q = value
    results = api.search(q = q, count = count)
    for result in results:
      # tweetの識別子
      tweet_id = result.id
      # ユーザーネームを取得
      screen_name = result.user._json['screen_name']
      user_data = api.get_user(screen_name = screen_name)
      # フォロワー数を取得
      followers_count = user_data.followers_count
      # フォロワーが500人以上いるアカウントのツイートにいいね
      if followers_count >= 500:
        try:
          api.create_favorite(tweet_id)
          time.sleep(1)
        except:
          print('フォロワーが500人未満です。')
    # キーワードを含むツイートを自動投稿する
    hash_tag = value.replace('#', '')
    msg = f'【広告】 \n 当サイトでは、『{value}』に関する記事を作成しています。 \n https://livequizlife.com \n #{hash_tag}'
    api.update_status(msg)
    time.sleep(1)

# LINEで送信するメッセージを作成
line_msg = 'と'.join(match_words_list)
line_msg += 'がトレンドに入っています。'

# LINE送信処理
def send():
  send_line_notify(line_msg)

def send_line_notify(notification_message):
  LINE_NOTIFY_TOKEN = os.environ['LINE_NOTIFY_TOKEN']
  line_notify_api = 'https://notify-api.line.me/api/notify'
  headers = {'Authorization': f'Bearer {LINE_NOTIFY_TOKEN}'}
  data = {'message': f'\n{notification_message}'}
  requests.post(line_notify_api, headers = headers, data = data)

if __name__ == "__main__":
  if len(match_words_list) != 0:
    send()