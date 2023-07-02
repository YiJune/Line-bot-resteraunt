from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseForbidden
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage, TemplateSendMessage, ButtonsTemplate, PostbackAction, PostbackEvent,CarouselTemplate, CarouselColumn
from pymongo import MongoClient
import random

line_bot_api = LineBotApi(settings.LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(settings.LINE_CHANNEL_SECRET)
client = MongoClient(settings.PYMONGO_CLIENT)
database = client['test']
collection = database['resteraunt']

@csrf_exempt
def callback(request):
    if request.method == 'POST':
        signature = request.headers['X-Line-Signature']
        body = request.body.decode('utf-8')
        try:
            handler.handle(body, signature)
        except InvalidSignatureError:
            return HttpResponseBadRequest()
        return HttpResponse()
    else:
        return HttpResponseBadRequest()

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    if event.message.text == '抽籤':
        # Code for handling '抽籤' message
        categories = [
            "火鍋",
            "日本料理",
            "燒烤",
            "精緻高級",
            "早午餐",
            "甜點",
            "約會餐廳",
            "韓式料理",
            "餐酒館",
            "居酒屋"
        ]
        buttons = [
            PostbackAction(label=category, data=f'category:{category}')
            for category in categories
        ]
        templates = []
        for i in range(0, len(buttons), 4):
            template = ButtonsTemplate(
                text='請選擇',
                actions=buttons[i:i+4]
            )
            templates.append(template)
        message = [
            TemplateSendMessage(alt_text='請選擇餐廳類別', template=template)
            for template in templates
        ]
        line_bot_api.reply_message(event.reply_token, message)
        
    

@handler.add(PostbackEvent)
def handle_postback(event):
    if event.postback.data.startswith(('category:', 'location:')):
        if event.postback.data.startswith('category:'):
            category = event.postback.data.replace('category:', '')
            location = None
        else:
            category = None
            location = event.postback.data.replace('location:', '')

        if category is not None and location is not None:
            restaurants = collection.find({'品項': category, '地區': location})
        elif category is not None:
            restaurants = collection.find({'品項': category})
        elif location is not None:
            restaurants = collection.find({'地區': location})
        else:
            restaurants = []

        restaurants = list(restaurants)
        if len(restaurants) >= 3:
            sampled_restaurants = random.sample(restaurants, 3)
        else:
            sampled_restaurants = []

        if sampled_restaurants:
            restaurant_info = "\n\n".join([f"店名：{r['店名']}\n評分:{r['評分']}\n營業時間:{', '.join(r['營業時間'])}\n金額:{r['金額']}\n地點:{r['地點']}" for r in sampled_restaurants])
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text=restaurant_info))
        else:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text='找不到符合條件的餐廳。'))

