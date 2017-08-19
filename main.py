# -*- coding:utf-8 -*-
# 2017/8/16 改 增加为监控多辆列车
# 输出 日志

# 李鹏博
# 2017/8/15
# 通过途牛网检测车票信息 如果有票则通知买票人
# 我为什么 使用途牛的接口，而不使用12306的接口？
# 因为12306的接口需要 把名称转换为 简写 这样就需要一个很长的字典，增加代码的长度
# 本程序使用了 twilio 模块
# 如果想使用本程序，需要本人的授权。否则程序会有错误

import requests
import time
from twilio.rest import Client

# --------------------------
# 直接在下边填写信息即可
# --------------------------

# 电话号码--此处是我的电话号码
phoneNumber = '+86'  
# url --此处为 漯河到郑州9月2号
RiQi='2017-09-01'
ChuFaDi="漯河"
DiDaDi="郑州"
url ='http://huoche.tuniu.com/tn?r=train/trainTicket/getTickets&primary%5BdepartureDate%5D={}\
&primary%5BdepartureCityName%5D={}\
&primary%5BarrivalCityName%5D={}&start=0&limit=0'.format(RiQi,ChuFaDi,DiDaDi)
# 填写列车 和 座位
LieChe = ['Z236','Z168','K22','K1628','K434','K1366','K226','K600']
ZuoweiLeixing = '硬座'

'''
# 发送短信
'''
def sentMessage(top = '无', cheCi = '无', date = '无', shichang = '无', zuowei = '无', yupiao = '无'):
    # Your Account SID from twilio.com/console
    #这个地方需要自己申请号码
    account_sid = ""
    # Your Auth Token from twilio.com/console
    auth_token  = ""

    client = Client(account_sid, auth_token)

    message = client.messages.create(
    #这个地方输入电话号码
        to='+86',
        from_="+14154633739",
        body="\n# " + top+
        "\n# 车次："+cheCi+
        "\n# 时间："+date+
        "\n# 时长："+shichang+
        "\n# 座位:"+zuowei+
        '\n# 余票：'+yupiao)
    return message.sid

'''
# 通过user得到json信息
# 如果不能得到，则返回 ‘error’
'''
def getJson(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except:
        return 'error'


# 解析Json文件 返回一个列表
def jieXiJson(json, lieChe):
    # 根据之前分析 json文件中
    # json['data']['list'] 是列车列表
    # json['data']['list'] for循环找到所有车次
    MuBiaoLieChe = {}
    for temp in json['data']['list']:
        # 如果找到则保存起来
        for tempc in lieChe:
            if temp['trainNum'] == tempc:
                MuBiaoLieChe[tempc]={temp['prices'][0]['seatName']:temp['prices'][0]['leftNumber'],
                temp['prices'][1]['seatName']:temp['prices'][1]['leftNumber'],
                temp['prices'][2]['seatName']:temp['prices'][2]['leftNumber'],
                "到站":temp['departDepartTime'],
                "时长":temp['durationStr']}
                break
    
    return MuBiaoLieChe


# ---------------------------------
# @          程序开始             @
# ---------------------------------
# 这个程序需要一直运行 所以死循环
# ---------------------------------

i = 0
j = 0
log = open("log9-1.txt", 'a+')
cuowucishu = 0
while True:
    # 得到json文件 如果失败则重试
    json = getJson(url)
    if json == 'error':
        cuowucishu = cuowucishu+1
        sentMessage(top='失败'+"1"+"次")
        if cuowucishu > 5:
            log.close()
            exit(0)
        time.sleep(60)
        continue

    # 解析JSON 获得列车信息
    LieCheXinXi = jieXiJson(json, LieChe)

    print('2017-09-02第',i,"次监控",file=log, flush=True)
    print('#'*30, file=log, flush=True)
    for temp in LieChe:
        print(temp,":",LieCheXinXi[temp], file=log, flush=True)
    print('#'*30, flush=True, file=log)
    # 每12个小时 发送一次 消息 证明还在监控
    if i%(6*24) == 0:
        sentMessage(top = '还没有车票！\n',cheCi = str(LieChe), date = RiQi, zuowei = ZuoweiLeixing)

    for temp in LieCheXinXi:
        if LieCheXinXi[temp][ZuoweiLeixing] != 0:
            sentMessage(top = "有票了！有票了！",cheCi=temp, date=RiQi+" "+LieCheXinXi[temp]["到站"], shichang=LieCheXinXi[temp]["时长"], zuowei=ZuoweiLeixing,yupiao=str(LieCheXinXi[temp][ZuoweiLeixing]))
            time.sleep(1)
            j += 1
            if j>10:
                log.close()
                exit(0)
    # 每5分钟 获取一份数据
    time.sleep(60*5)
    i = i+1
    cuowucishu = 0
