from base64 import b64encode as b
from discord_build_info_py import *
import httpx, json, time, threading, requests, sys

captchakey = ''

def create_props():
    build_num, build_hash, build_id = getClientData('stable')

    super_properties = b(json.dumps({
        "os": "Windows",
        "browser": "Edge",
        "device": "",
        "system_locale": "en-US",
        "browser_user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.80 Safari/537.36 Edg/98.0.1108.50",
        "browser_version": "90.0",
        "os_version": "10",
        "referrer": "",
        "referring_domain": "",
        "referrer_current": "",
        "referring_domain_current": "",
        "release_channel": "stable",
        "client_build_number": int(build_num),
        "client_event_source": None
    }, separators=(',', ':')).encode()).decode()

    cookiemonster = httpx.get('https://discord.com/register').headers['set-cookie']
    sep = cookiemonster.split(";")
    sx = sep[0]
    sx2 = sx.split("=")
    dfc = sx2[1]
    split = sep[6]
    split2 = split.split(",")
    split3 = split2[1]
    split4 = split3.split("=")
    sdc = split4[1]

    return {'props':super_properties, "cookies": f"__dcfduid={dfc}; __sdcfduid={sdc}"}

def solve_captcha(invite):
    captchadata = {
        'User-Agent':"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.80 Safari/537.36 Edg/98.0.1108.50"
    }

    captchaurl = f'http://2captcha.com/in.php?key={captchakey}&method=hcaptcha&sitekey=4c672d35-0701-42b2-88c3-78380b0db560&pageurl=https://discord.com/api/v9/invites/{invite}'
    captcharequests = httpx.post(captchaurl, data=captchadata, json=1)

    captchares = (captcharequests.text)
    x = captchares.split('|')
    id = x[1]
    time.sleep(15)

    while True:
        resurl = httpx.get(f'http://2captcha.com/res.php?key={captchakey}&action=get&id={id}')
        if resurl.text == "CAPCHA_NOT_READY":
            pass
        else:
            break

    captoken = resurl.text
    final, captchatoken = captoken.split('|')

    return captchatoken

def joiner(token, invite):
    get_props = create_props()

    header = {
        "authority": "discord.com",
        "scheme": "https",
        "accept": "*/*",
        "accept-encoding": "gzip, deflate, br",
        "accept-language": "en-US",
        "Authorization": token,
        "content-length": "0",
        "cookie": get_props['cookies'],
        "origin": "https://discord.com",
        'referer': 'https://discord.com/channels/@me',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.80 Safari/537.36 Edg/98.0.1108.50",
        "x-context-properties": "eyJsb2NhdGlvbiI6Ikludml0ZSBCdXR0b24gRW1iZWQiLCJsb2NhdGlvbl9ndWlsZF9pZCI6Ijg3OTc4MjM4MDAxMTk0NjAyNCIsImxvY2F0aW9uX2NoYW5uZWxfaWQiOiI4ODExMDg4MDc5NjE0MTk3OTYiLCJsb2NhdGlvbl9jaGFubmVsX3R5cGUiOjAsImxvY2F0aW9uX21lc3NhZ2VfaWQiOiI4ODExOTkzOTI5MTExNTkzNTcifQ==",
        "x-debug-options": "bugReporterEnabled",
        "x-super-properties": get_props['props']
    }

    payload = {
        'captcha_key': solve_captcha(invite)
    }

    join = requests.post(f'https://discord.com/api/v9/invites/{invite}', headers=header, json=payload)
    if join.status_code == 200:
        sys.stdout.write('[+] Joined' + '\n')
    else:
        sys.stdout.write('[-] Failed' + '\n')

if __name__ == '__main__':
    tokens = open("tokens.txt", "r").read().splitlines()
    inv = input('Invite Code Only: ')
    for token in tokens:
        threading.Thread(target=joiner, args=(token, inv)).start()
