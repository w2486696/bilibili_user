import requests
from fake_useragent import UserAgent
import json
import random
import pymysql
from multiprocessing.dummy import Pool as ThreadPool
import os
import argparse
from functools import  partial

parser = argparse.ArgumentParser(description='获取参数')
parser.add_argument('--f', type=bool, default=False,
                    help='get face?')
parser.add_argument('--sql', type=bool, default=False,
                    help='sum the integers (default: find the max)')
args = parser.parse_args()

if not os.path.exists('./json'):
    os.mkdir("./json")
if not os.path.exists('./image'):
    os.mkdir("./image")

uas = UserAgent()
urls = []
for m in range(20000, 20300):
    url = 'https://space.bilibili.com/' + str(m)
    urls.append(url)


def getsource(url, getface=False, tosql=False):
    mid = url.replace("https://space.bilibili.com/", "")
    payload = {"mid": mid, "jsonp": "jsonp", "callback": "__jp4"}
    ua = uas.random
    head = {
        'User-Agent': ua,
        'Referer': 'https://space.bilibili.com/' + str(mid) + '?from=search&seid=' + str(random.randint(10000, 50000)),
        "Host": "api.bilibili.com",
        "Origin": "https://space.bilibili.com",
    }
    re = requests.session().get("https://api.bilibili.com/x/space/acc/info?", params=payload, headers=head)

    try:
        jsDict = json.loads(re.text[6:-1])
        code = jsDict['code'] if 'code' in jsDict.keys() else True
        if code == 0:
            print(jsDict)
            if "data" in jsDict.keys():
                jsData = jsDict['data']
                mid = jsData['mid']
                name = jsData['name']
                sex = jsData['sex']
                rank = jsData['rank']
                level = jsData['level']
                face = jsData['face']
                birthday = jsData['birthday'] if 'birthday' in jsData.keys() else 'nobirthday'
                sign = jsData['sign']
                vipType = jsData['vip']['type']
                vipStatus = jsData['vip']['status']
                coins = jsData['coins']
                print("Succeed get user info: " + str(mid))
                try:
                    res = requests.get(
                        'https://api.bilibili.com/x/relation/stat?vmid=' + str(mid) + '&jsonp=jsonp').text
                    head_1 = {
                        "Host": "api.bilibili.com",
                        "User-Agent": uas.random
                    }
                    viewinfo = requests.get(
                        'https://api.bilibili.com/x/space/upstat?mid=' + str(mid) + '&jsonp=jsonp', headers=head_1).text
                    js_fans_data = json.loads(res)
                    js_viewdata = json.loads(viewinfo)

                    following = js_fans_data['data']['following']
                    fans = js_fans_data['data']['follower']
                    archiveview = js_viewdata['data']['archive']['view']
                    article = js_viewdata['data']['article']['view']
                except:
                    following = 0
                    fans = 0
                    archiveview = 0
                    article = 0
                content = {"mid": mid, "name": name, "sex": sex, "rank": rank, "level": level, "face": face,
                           "birthday": birthday,
                           "sign": sign, "vipType": vipType, "vipStatus": vipStatus, "coins": coins,
                           "following": following, "fans": fans,
                           "archiveview": archiveview, "article": article}
                # 保存为json格式
                jsObj = json.dumps(content)
                fileObject = open('./json/%d.json' % (mid), 'w')
                fileObject.write(jsObj)
                fileObject.close()
                # 保存头像
                if (getface):
                    with open('./image/%d.jpg' % mid, 'wb') as f:
                        f.write(requests.get(face).content)
            else:
                print('no data now')
            if (tosql):
                try:
                    # Please write your MySQL's information.
                    conn = pymysql.connect(
                        host='localhost', user='root', passwd='w2486696', db='bilibili', charset='utf8')
                    cur = conn.cursor()
                    print(type(archiveview))
                    cur.execute('INSERT INTO bili_user(mid, name, sex, `rank`, level, face, bietuday, sign, vipType, vipStatus, coins, following, fans, archiveview, article) \
                    VALUES ("%s","%s","%s","%s","%s","%s","%s","%s","%s","%s","%s","%s","%s","%s","%s")' \
                                % (
                                mid, name, sex, rank, level, face, birthday, sign, vipType, vipStatus, coins, following,
                                fans, archiveview, article))
                    conn.commit()
                except Exception as e:
                    print(e)
        else:
            print("Error: " + url)
    except Exception as e:
        print("1")
        print(e)
        pass


if __name__ == "__main__":
    pool = ThreadPool(1)
    try:
        results = pool.map(partial(getsource,getface=args.f, tosql=args.sql),urls)
    except Exception as e:
        print(e)

    pool.close()
    pool.join()
