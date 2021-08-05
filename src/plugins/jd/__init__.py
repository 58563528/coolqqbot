"""京东扫码登录"""
import json
import re
import requests
import base64
import time
import nonebot
from nonebot import logger,on_command
from nonebot.adapters.cqhttp import Bot
from nonebot.adapters.cqhttp.event import Message, MessageEvent, GroupMessageEvent, PrivateMessageEvent
from urllib.parse import urlencode, quote_plus
from typing import Union
from nonebot.rule import to_me
from .config import plugin_config
requests.packages.urllib3.disable_warnings()

jd_cmd = on_command('jd', aliases={'京豆', '扫码', '京东扫码'})
jd_cmd.__doc__ = """
jd 京豆

扫码
京豆
"""
cdTime = plugin_config.cdTime
QQ_group_id = plugin_config.QQ_group_id
i=0
#s = requests.session()
jd_ua = 'jdapp;android;10.0.5;11;{0};network/wifi;model/M2102K1C;osVer/30;appBuild/88681;partner/lc001;eufv/1;jdSupportDarkMode/0;Mozilla/5.0 (Linux; Android 11; M2102K1C Build/RKQ1.201112.002; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/77.0.3865.120 MQQBrowser/6.2 TBS/045534 Mobile Safari/537.36'


@jd_cmd.handle()
async def _(bot: Bot, event: Union[PrivateMessageEvent, GroupMessageEvent]):
    qid = event.get_user_id()
    data = readJson()
    try:
        cd = event.time - data[qid][0]
    except:
        cd = cdTime + 1
    logger.info(cd)
    try:
        
        if (event.group_id == QQ_group_id):
            logger.info(event.group_id)
            #writeJson(qid, event.time, '', data)
            if cd > cdTime :#or event.get_user_id() in nonebot.get_driver().config.superusers:

                await token_get(qid, event.time)
            else:
                await jd_cmd.send(f'不要请求太快，你的CD还有{cdTime-cd}秒', at_sender=True)
        else:
            return
    except Exception as e:
        logger.info(e)
        await jd_cmd.send('正在等待其他人扫码，请稍后再试', at_sender=True)


async def save_qrcode(pic_url: str) -> str:
    try:
        headers={"User-Agent":"Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36 QIHU 360SE"}
        data=requests.get(pic_url, headers=headers).content
        base64_data = base64.b64encode(data)
        pic_file = base64_data.decode()
        #print('data:image/jpeg;base64,%s' % pic_file)
    except Exception:
        raise Exception("服务器转存请求图片错误！\r\n")
    
    return f'[CQ:image,file=base64://{pic_file}]'

async def token_get(qid, nowetime):
    s = requests.session()
    t = round(time.time())
    headers = {
        'User-Agent': jd_ua.format(t),
        'referer': 'https://plogin.m.jd.com/cgi-bin/mm/new_login_entrance?lang=chs&appid=300&returnurl=https://wq.jd.com/passport/LoginRedirect?state={0}&returnurl=https://home.m.jd.com/myJd/newhome.action?sceneval=2&ufc=&/myJd/home.action&source=wq_passport'.format(t)
    }
    t = round(time.time())
    url = 'https://plogin.m.jd.com/cgi-bin/mm/new_login_entrance?lang=chs&appid=300&returnurl=https://wq.jd.com/passport/LoginRedirect?state={0}&returnurl=https://home.m.jd.com/myJd/newhome.action?sceneval=2&ufc=&/myJd/home.action&source=wq_passport'.format(t)
    res = s.get(url=url, headers=headers, verify=False)
    res_json = json.loads(res.text)
    #print(res_json)
    s_token = res_json['s_token']
    
    t = round(time.time() * 1000)
    headers = {
        'User-Agent': jd_ua.format(t),
        'referer': 'https://plogin.m.jd.com/login/login?appid=300&returnurl=https://wqlogin2.jd.com/passport/LoginRedirect?state={0}&returnurl=//home.m.jd.com/myJd/newhome.action?sceneval=2&ufc=&/myJd/home.action&source=wq_passport'.format(t),
        'Content-Type': 'application/x-www-form-urlencoded; Charset=UTF-8'
    }
    url = 'https://plogin.m.jd.com/cgi-bin/m/tmauthreflogurl?s_token={0}&v={1}&remember=true'.format(s_token, t)
    data = {
        'lang': 'chs',
        'appid': 300,
        'returnurl': 'https://wqlogin2.jd.com/passport/LoginRedirect?state={0}returnurl=//home.m.jd.com/myJd/newhome.action?sceneval=2&ufc=&/myJd/home.action&source=wq_passport'.format(t)
        }
    res = s.post(url=url, headers=headers, data=data, verify=False)
    #print(res.text)
    res_json = json.loads(res.text)
    token = res_json['token']
    #print("token:", token)
    c = s.cookies.get_dict()
    okl_token = c['okl_token']
    # print("okl_token:", okl_token)
    qrurl = 'https://plogin.m.jd.com/cgi-bin/m/tmauth?client_type=m&appid=300&token={0}'.format(token)
    payload = {'data': qrurl}
    result = urlencode(payload, quote_via=quote_plus)
    pic_url = 'https://api.qrserver.com/v1/create-qr-code/?size=300x300&{0}'.format(result)
    #print(pic_url)
    qrcode_report = await save_qrcode(pic_url)
    await jd_cmd.send(f"\n请在1分钟之内完成扫码！\n" + Message(qrcode_report), at_sender=True)
    writeJson(qid, nowetime, '', data)
    await check_token(qid, s, token, okl_token)


async def check_token(qid, s, token, okl_token):
    t = round(time.time() * 1000)
    headers = {
        'User-Agent': jd_ua.format(t),
        'referer': 'https://plogin.m.jd.com/login/login?appid=300&returnurl=https://wqlogin2.jd.com/passport/LoginRedirect?state={0}&returnurl=//home.m.jd.com/myJd/newhome.action?sceneval=2&ufc=&/myJd/home.action&source=wq_passport'.format(t),
        'Content-Type': 'application/x-www-form-urlencoded; Charset=UTF-8'
    }
    url = 'https://plogin.m.jd.com/cgi-bin/m/tmauthchecktoken?&token={0}&ou_state=0&okl_token={1}'.format(token, okl_token)
    data = {
        'lang': 'chs',
        'appid': 300,
        'returnurl': 'https://wqlogin2.jd.com/passport/LoginRedirect?state={0}&returnurl=//home.m.jd.com/myJd/newhome.action?sceneval=2&ufc=&/myJd/home.action'.format(t),
        'source': 'wq_passport',
    }
    res = s.post(url=url, headers=headers, data=data, verify=False)
    check = json.loads(res.text)
    code = check['errcode']
    message = check['message']
    global i
    while code == 0:
        print("扫码成功")
        await jd_cmd.send('扫码成功！',at_sender=True)
        jd_ck = s.cookies.get_dict()
        pt_key = 'pt_key=' + jd_ck['pt_key']
        pt_pin = 'pt_pin=' + jd_ck['pt_pin']
        ck = str(pt_key) + ';' + str(pt_pin) + ';'
        s.close()
        data = readJson()
        writeJson(qid, int(time.time()), ck, data)
        print(ck)
        break
    else:
        i = i + 1
        if i < 15:
            print("第" + str(i) + "次等待扫码结果:" + message)
            time.sleep(2)
            #if  i % 8 == 0:
                #await jd_cmd.send('等待用户' +qid + "扫码结果", at_sender=True )
            await check_token(qid, s, token, okl_token)
        else:
            i = 0
            await jd_cmd.send('用户' + qid + "未扫码！结束此次", at_sender=True )
            #break
            #exit(0)


async def write_cookie(qid,ck):
    
    t = round(time.time() * 1000)
    headers = {
        'Authorization': 'Bearer eyJhbGciOiJIUzM4NCIsInR5cCI6IkpXVCJ9.eyJ1c2VybmFtZSI6ImFkbWluIiwicGFzc3dvcmQiOiI1ODU2MzUyOFFRIiwiaWF0IjoxNjI3ODg0NDEwLCJleHAiOjE2Mjg0ODkyMTB9.og7ICSumJttBWhpmdH7tmVXVIktSvyToh9G0YcRHtfHQ1x9duAK4PpeRQ48hTrKp',
    }
    url = 'https://192.168.20.100:55700/api/cookies?t={0}'.format(t)
    data = {
        'value': ck,
        }
    res = s.post(url=url, headers=headers, data=data, verify=False)
    await jd_cmd.send(Message(res), at_sender=True)
    

def readJson():
    with open(r'./src/plugins/jd/userscd.json', 'r') as f_in:
        data = json.load(f_in)
        f_in.close()
        return data


def writeJson(qid: str, time: int, ck: str, data: dict):
    data[qid] = [time, ck]
    with open(r'./src/plugins/jd/userscd.json', 'w') as f_out:
        json.dump(data, f_out)
        f_out.close()
