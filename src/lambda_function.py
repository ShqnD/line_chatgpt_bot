import os, sys
from linebot import (LineBotApi, WebhookHandler)
from linebot.models import (MessageEvent, TextMessage, TextSendMessage,)
from linebot.exceptions import (LineBotApiError, InvalidSignatureError)
import openai

line_bot_api = LineBotApi(os.environ['LINE_CHANNEL_ACCESS_TOKEN'])
handler = WebhookHandler(os.environ['LINE_CHANNEL_SECRET'])
openai.api_key = os.environ['API_KEY']

def lambda_handler(event, context):
    signature = event["headers"]["x-line-signature"]
    body = event["body"]

    ok_json = {"isBase64Encoded":False, "statusCode":200, "headers":{}, "body":""}
    error_json = {"isBase64Encoded":False, "statusCode":403, "headers":{}, "body":"Error"}

    @handler.add(MessageEvent, message=TextMessage)
    def message(line_event):
        text = openai.ChatCompletion.create(model='gpt-3.5-turbo',
                                    messages=[
                                        {'role':'user', 'content':line_event.message.text}
                                    ]
                                )

        text = text["choices"][0]["message"]["content"].strip()
        
        line_bot_api.reply_message(line_event.reply_token, TextSendMessage(text=text)) 
    try:
        handler.handle(body, signature)
    except LineBotApiError as e:
        logger.error("Got exception from LINE Messaging API: %s\n" % e.message)
        for m in e.error.details:
            logger.error("  %s: %s" % (m.property, m.message))
        return error_json
    except InvalidSignatureError:
        return error_json
    return ok_json