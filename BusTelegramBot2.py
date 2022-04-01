import requests
import telegram
from telegram.ext import Updater
from telegram.ext import MessageHandler, Filters
import config

bot = telegram.Bot(config.API_TOKEN)
 
# updater
updater = Updater(token=config.API_TOKEN, use_context=True)
dispatcher = updater.dispatcher
updater.start_polling()

def bus_info_get(arsId):
    url2 = 'http://ws.bus.go.kr/api/rest/stationinfo/getStationByUid?serviceKey=' + config.SERVICE_KEY + '&arsId=' + arsId + "&resultType=json"
    print(url2)
    response = requests.get(url2)
    if response.status_code == 200:                   
        json_obj = response.json()
        item_list2 = json_obj["msgBody"]["itemList"]
        bus_info = []
        for bi in item_list2:
            b = {}
            b['arrmsg1'] = bi['arrmsg1']
            b['arrmsg2'] = bi['arrmsg2']
            if 'stationNm1' in bi:
                b['stationNm1'] = bi['stationNm1']
            else:
                b['stationNm1'] = 'None'

            b['stationNm2'] = bi['stationNm2'] if 'stationNm2' in bi else ''
            b['rtNm'] = bi['rtNm']

            b['routeType'] = bi['routeType']

            bus_info.append(b)
        print(">>> bus_info", bus_info)
        return bus_info
    else:
        pass 

def handler(update, context):
    msg = update.message.text 
    print("message:", update.message.text )
    
    cmds = msg.split(' ')
    cmd = cmds[0]
    if cmd == '/bus':
        arsId = cmds[-1]
        bus_infos = bus_info_get(arsId)
        print(bus_infos)

        user_id = update.message.from_user.id
        print(f"chat_id:{config.BOT_CHAT_ID}, user_id:{user_id}")

        cnt = 0
        while cnt < len(bus_infos) -1 :
            msg = ''
            msg += f"{bus_infos[cnt]['rtNm']} bus-------------\n"
            msg += f"Estimated Arrival Time : {bus_infos[cnt]['arrmsg1']}\n"
            if bus_infos[cnt]['routeType'] == '3':
                msg += "RouteType : Ganson\n"
                img_url = "http://learnsteam.kr/img/bus_red.png"
            elif bus_infos[cnt]['routeType'] == '4':
                msg += "RouteType : Jison\n"
                img_url = "http://learnsteam.kr/img/bus_green.png"
            elif bus_infos[cnt]['routeType'] == '6':
                msg += "RouteType : Gwangyuk\n"
                img_url = "http://learnsteam.kr/img/bus_blue.png"    
            else:
                msg += "RouteType : other\n"
                img_url = "http://learnsteam.kr/img/bus_gray.png"

            if bus_infos[cnt]['stationNm1'] not in ['None', '']:
                msg += f"Destination1 : {bus_infos[cnt]['stationNm1']}\n"
            if bus_infos[cnt]['stationNm2'] not in ['None', '']:
                msg += f"Destination2 : {bus_infos[cnt]['stationNm2']}\n"
            msg += "\n"
        
            print("img url:", img_url)
            bot.sendPhoto( chat_id=user_id, photo=img_url)
            bot.sendMessage(chat_id=user_id, text=msg)
            cnt += 1
        
    elif cmd == '/start':
        user_id = update.message.from_user.id
        print(f"chat_id:{config.BOT_CHAT_ID}, user_id:{user_id}")
        msg = "Start"
        bot.sendMessage(chat_id=user_id, text=msg)

dispatcher.add_handler( MessageHandler(Filters.text | Filters.command, handler) ) 
