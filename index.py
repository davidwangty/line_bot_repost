from flask import Flask, request, abort

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, JoinEvent, TextMessage, TextSendMessage, ImageSendMessage, responses
)
import os
import psycopg2
from datetime import datetime
import pytz

# timezone set
tpe = pytz.timezone('Asia/Taipei')

try:
    AccessToken = os.environ["ChannelAccessToken"]
    ChannelSecret = os.environ["ChannelSecret"]
    ChannelID = os.environ["UserID"]
    # MEDIC
    Group1 = []
    Group1.append(os.environ["Group1"])
    Group1.append(os.environ["Group2"])
    Group1.append(os.environ["Group3"])
    # 國企學會
    Group2 = []
    Group2.append(os.environ["Group2-1"])
    Group2.append(os.environ["Group2-2"])
    # 美食&旅遊
    Group3 = []
    Group3.append(os.environ["Group3-1"])
    Group3.append(os.environ["Group3-2"])
    # 商業合作
    Group4 = []
    Group4.append(os.environ["Group4-1"])
    Group4.append(os.environ["Group4-2"])
     # 公益
    Group5 = []
    Group5.append(os.environ["Group5-1"])
    Group5.append(os.environ["Group5-2"])
     # 法律
    Group6 = []
    Group6.append(os.environ["Group6-1"])
    Group6.append(os.environ["Group6-2"])
     # 求職求才
    Group7 = []
    Group7.append(os.environ["Group7-1"])
    Group7.append(os.environ["Group7-2"])
     # 賣租贈
    Group8 = []
    Group8.append(os.environ["Group8-1"])
    Group8.append(os.environ["Group8-2"])
except Exception as e:
    print(e)

app = Flask(__name__)

line_bot_api = LineBotApi(AccessToken)
handler = WebhookHandler(ChannelSecret)

group_name = ["A", "B", "C"]

# Webhook 處理 驗證後交給hander
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


@handler.add(MessageEvent)
def handel_message(event):
    print("訊息:", event)

    if event.message.type == "text":
        if event.source.type is "group":
            if event.source.group_id in Group1:
                repost(event, Group1)
            elif event.source.group_id in Group2:
                repost(event, Group2)
            elif event.source.group_id in Group3:
                repost(event, Group3)
            elif event.source.group_id in Group4:
                repost(event, Group4)
            elif event.source.group_id in Group5:
                repost(event, Group5)
            elif event.source.group_id in Group6:
                repost(event, Group6)
            elif event.source.group_id in Group7:
                repost(event, Group7)
            elif event.source.group_id in Group8:
                repost(event, Group8)
@handler.default()
def default(event):
    print("事件:", type(event), "\n", event)

def repost(event, Group):
    group_id = event.source.group_id
    index = Group.index(group_id)
    if event.source.user_id:
        user_id = event.source.user_id
        response = line_bot_api._get(
            '/v2/bot/group/{group_id}/member/{user_id}'.format(group_id=group_id, user_id=user_id),
            timeout=None
        )
        profile = responses.Profile.new_from_json_dict(response.json)
        name = profile.display_name
        message = "{index}組 【{name}】 {message}".format(index = group_name[index],
                                                          name = name,
                                                          message = event.message.text)
    else:
        message = "{index}組 {message}".format(index = group_name[index],
                                               message = event.message.text)

    for group in Group:
        if group != group_id:
            line_bot_api.push_message(
                    group,
                    TextSendMessage(text=message))


if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)