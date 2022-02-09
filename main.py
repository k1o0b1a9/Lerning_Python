#スクレイピング用インポート↓
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
import time
import pandas
#Seleniu4での警告回避用
from selenium.webdriver.chrome import service as fs
from selenium.webdriver.common.by import By
#スクレイピング用インポート↑

import requests

from flask import Flask, request, abort

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
)
import os

app = Flask(__name__)

#AmazonのPS5販売ページ
url='https://www.amazon.co.jp/%E3%82%BD%E3%83%8B%E3%83%BC%E3%83%BB%E3%82%A4%E3%83%B3%E3%82%BF%E3%83%A9%E3%82%AF%E3%83%86%E3%82%A3%E3%83%96%E3%82%A8%E3%83%B3%E3%82%BF%E3%83%86%E3%82%A4%E3%83%B3%E3%83%A1%E3%83%B3%E3%83%88-PlayStation-5-CFI-1100A01/dp/B09CTQPQNV/ref=sr_1_38?__mk_ja_JP=%E3%82%AB%E3%82%BF%E3%82%AB%E3%83%8A&crid=19TKW2FUUFBZR&keywords=PS5&qid=1643263211&sprefix=ps%2Caps%2C359&sr=8-38'

#環境変数取得
YOUR_CHANNEL_ACCESS_TOKEN = os.environ["YOUR_CHANNEL_ACCESS_TOKEN"]
YOUR_CHANNEL_SECRET = os.environ["YOUR_CHANNEL_SECRET"]

line_bot_api = LineBotApi(YOUR_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(YOUR_CHANNEL_SECRET)

@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'

def LineNotify(message):
    line_notify_token = YOUR_CHANNEL_ACCESS_TOKEN
    line_notify_api = "https://notify-api.line.me/api/notify"

    payload = {"message":message}
    headers = {"Authorization":"Bearer " + line_notify_token}
    requests.post(line_notify_api, data = payload, headers = headers)


def monitor():
    # chromedriverの設定とキーワード検索実行
    #headlessで実行時ウィンドウが開かないとように変更
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    #Chromedriverが二ヶ所にある？？？
    #chrome_service = fs.Service('/opt/homebrew/bin/chromedriver')
    #chrome_service = fs.Service('/opt/homebrew/Caskroom/chromedriver/97.0.4692.71/chromedriver')
    chrome_service = fs.Service('/app/.chromedriver/bin/chromedriver')
    #driver = webdriver.Chrome(ChromeDriverManager().install(),service=chrome_service)
    driver = webdriver.Chrome(ChromeDriverManager().install(), options=options,service=chrome_service)
    driver.get(url)

    #実行にゆとりを持たせて負荷軽減
    interval=60
    limit=1
    count=0

    #カートボタン監視
    #実際の使用時はsleepを挟んで負荷軽減
    while True:
        test=driver.find_elements(By.ID,'add-to-cart-button')
        if len(test) == 0:
            count+=1
            if count==limit:
                return '在庫なし'
        else:
            return '在庫あり'
            #在庫ありの場合、カートに追加
            #driver.find_elements(By.NAME,'submit.add-to-cart').click()
        time.sleep(interval)

@handler.add(MessageEvent, message=TextMessage)

def handle_message(event):
    '''オウム返し
    line_bot_api.reply_message(
        event.reply_token,
        #event.message.textで受信したメッセージをそのまま送信
        TextSendMessage(text=event.message.text))
    '''
    '''定型分返し
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text='aiueo'))
    '''
    #在庫監視結果格納
    message = monitor()
    #LineNotify(message)

    #ユーザからのメッセージを介さず自分で送信できるように
    #line_bot_api.push_message('@563aipyl', TextSendMessage(text='Hello World!'))

    #メッセージをトリガーとして在庫状況を伝える
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=message))

    #プッシュ通知
    #プッシュ通知送り先LINE ID
    user_id = "keigo1019"
    line_bot_api.push_message(
        user_id, 
        TextSendMessage(text='Hello World!'))


if __name__ == "__main__":
#    app.run()
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port)