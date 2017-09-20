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
    Group1 = []
    Group1.append(os.environ["Group1"])
    Group1.append(os.environ["Group2"])
    Group1.append(os.environ["Group3"])
    Group2 = []
    Group2.append(os.environ["Group2-1"])
    Group2.append(os.environ["Group2-2"])
    Group3 = []
    Group3.append(os.environ["Group3-1"])
    Group3.append(os.environ["Group3-2"])
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
                group_id = event.source.group_id
                index = Group1.index(group_id)
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

                for group in Group1:
                    if group != group_id:
                        line_bot_api.push_message(
                                group,
                                TextSendMessage(text=message))
            elif event.source.group_id in Group2:
                group_id = event.source.group_id
                index = Group2.index(group_id)
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

                for group in Group2:
                    if group != group_id:
                        line_bot_api.push_message(
                                group,
                                TextSendMessage(text=message))
            elif event.source.group_id in Group3:
                repost(event, Group3)

@handler.default()
def default(event):
    print("事件:", type(event))
    print(event)

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