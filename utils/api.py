import json
import urllib.parse
from random import randrange
import requests
from hashlib import md5
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
def search_music(func):
    def wapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            print(f"调用API出错: {e}")
            import traceback
            traceback.print_exc()
            return None
    return wapper

@search_music
def search_music(keywords, cookies, limit=10):
    """pa
    网易云音乐搜索接口，返回歌曲信息列表
    :param keywords: 搜索关键词
    :param cookies: 登录 cookies
    :param limit: 返回数量
    :return: 歌曲信息列表
    """
    url = 'https://music.163.com/api/cloudsearch/pc'

    data = {'s': keywords, 'type': 1, 'limit': limit}
    headers = {
        'User-Agent': 'Mozilla/5.0',
        'Referer': 'https://music.163.com/'
    }
    response = requests.post(url, data=data, headers=headers, cookies=cookies)
    result = response.json()
    songs = []
    for item in result.get('result', {}).get('songs', []):
        song_info = {
            'id': item['id'],
            'name': item['name'],
            'artists': '/'.join(artist['name'] for artist in item['ar']),
            'album': item['al']['name'],
            'picUrl': item['al']['picUrl']
        }
        songs.append(song_info)
    return songs

def name_v1(id):
    urls = "https://interface3.music.163.com/api/v3/song/detail"
    data = {'c': json.dumps([{"id":id,"v":0}])}
    response = requests.post(url=urls, data=data)
    return response.json()

def lyric_v1(id, cookies):
    url = "https://interface3.music.163.com/api/song/lyric"
    data= {'id': id, 'cp': 'false', 'tv': '0', 'lv': '0', 'rv': '0', 'kv': '0', 'yv': '0', 'ytv': '0', 'yrv': '0'}
    response = requests.post(url=url, data=data, cookies=cookies)
    return response.json()
def HexDigest(data):
    return "".join([hex(d)[2:].zfill(2) for d in data])

def HashDigest(text):
    HASH = md5(text.encode("utf-8"))
    return HASH.digest()

def HashHexDigest(text):
    return HexDigest(HashDigest(text))
def post(url, params, cookie):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Safari/537.36 Chrome/91.0.4472.164 NeteaseMusicDesktop/2.10.2.200154',
        'Referer': '',
    }
    cookies = {
        "os": "pc",
        "appver": "",
        "osver": "",
        "deviceId": "pyncm!"
    }                
    cookies.update(cookie)
    response = requests.post(url, headers=headers, cookies=cookies, data={"params": params})
    return response.text

def url_v1(id, level, cookies):
    url = "https://interface3.music.163.com/eapi/song/enhance/player/url/v1"
    AES_KEY = b"e82ckenh8dichen8"
    config = {
        "os": "pc",
        "appver": "",
        "osver": "",
        "deviceId": "pyncm!",
        "requestId": str(randrange(20000000, 30000000))
    }

    payload = {
        'ids': [id],
        'level': level,
        'encodeType': 'flac',
        'header': json.dumps(config),
    }

    if level == 'sky':
        payload['immerseType'] = 'c51'
    
    url2 = urllib.parse.urlparse(url).path.replace("/eapi/", "/api/")
    digest = HashHexDigest(f"nobody{url2}use{json.dumps(payload)}md5forencrypt")
    params = f"{url2}-36cd479b6b5-{json.dumps(payload)}-36cd479b6b5-{digest}"
    padder = padding.PKCS7(algorithms.AES(AES_KEY).block_size).padder()
    padded_data = padder.update(params.encode()) + padder.finalize()
    cipher = Cipher(algorithms.AES(AES_KEY), modes.ECB())
    encryptor = cipher.encryptor()
    enc = encryptor.update(padded_data) + encryptor.finalize()
    params = HexDigest(enc)
    response = post(url, params, cookies)
    return json.loads(response)
