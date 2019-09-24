import requests, json, time
from datetime import datetime
from mongo import MongoConn, MONGODB_CONFIG
from sender import send_message
from fetcher import create_new_fetcher, ExitSignal
import os

HEADERS_FOR_FORM = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.96 Safari/537.36',
    'Accept': '*/*',
    'X-Requested-With': 'XMLHttpRequest'
}
HEADERS_IN_USE = HEADERS_FOR_FORM

URL = "https://cn.investing.com/instruments/Service/GetTechincalData"
BODY = dict(pairID="944923", period="86400", viewType="normal")
TICK = 1
STR = """
Accept: */*
Accept-Encoding: gzip, deflate, br
Accept-Language: zh-CN,zh;q=0.9
Connection: keep-alive
Content-Length: 42
Content-Type: application/x-www-form-urlencoded
Cookie: adBlockerNewUserDomains=1567404577; _ga=GA1.2.695913845.1567404581; _gid=GA1.2.1392768259.1567404581; __qca=P0-1880379269-1567404583907; __gads=ID=555f8af75c88b64c:T=1567404591:S=ALNI_MaIUMdOXQKQvcRl-vxQznXI82L9iA; PHPSESSID=h3gkh4hlp61g3t4ogjjspl91pq; geoC=CN; StickySession=id.43603938871.489cn.investing.com; Hm_lvt_a1e3d50107c2a0e021d734fe76f85914=1567426938,1567483755,1567508823,1567574096; SideBlockUser=a%3A2%3A%7Bs%3A10%3A%22stack_size%22%3Ba%3A1%3A%7Bs%3A11%3A%22last_quotes%22%3Bi%3A8%3B%7Ds%3A6%3A%22stacks%22%3Ba%3A1%3A%7Bs%3A11%3A%22last_quotes%22%3Ba%3A7%3A%7Bi%3A0%3Ba%3A3%3A%7Bs%3A7%3A%22pair_ID%22%3Bs%3A7%3A%221017510%22%3Bs%3A10%3A%22pair_title%22%3Bs%3A0%3A%22%22%3Bs%3A9%3A%22pair_link%22%3Bs%3A34%3A%22%2Fequities%2Fnsfocus-information-tech%22%3B%7Di%3A1%3Ba%3A3%3A%7Bs%3A7%3A%22pair_ID%22%3Bs%3A6%3A%22944068%22%3Bs%3A10%3A%22pair_title%22%3Bs%3A0%3A%22%22%3Bs%3A9%3A%22pair_link%22%3Bs%3A26%3A%22%2Fequities%2Fboe-technology-a%22%3B%7Di%3A2%3Ba%3A3%3A%7Bs%3A7%3A%22pair_ID%22%3Bs%3A6%3A%22945332%22%3Bs%3A10%3A%22pair_title%22%3Bs%3A0%3A%22%22%3Bs%3A9%3A%22pair_link%22%3Bs%3A40%3A%22%2Fequities%2Fbeijing-originwater-technology%22%3B%7Di%3A3%3Ba%3A3%3A%7Bs%3A7%3A%22pair_ID%22%3Bs%3A7%3A%221017444%22%3Bs%3A10%3A%22pair_title%22%3Bs%3A0%3A%22%22%3Bs%3A9%3A%22pair_link%22%3Bs%3A34%3A%22%2Fequities%2Fzhejiang-century-huatong%22%3B%7Di%3A4%3Ba%3A3%3A%7Bs%3A7%3A%22pair_ID%22%3Bs%3A6%3A%22944949%22%3Bs%3A10%3A%22pair_title%22%3Bs%3A0%3A%22%22%3Bs%3A9%3A%22pair_link%22%3Bs%3A23%3A%22%2Fequities%2Fyifan-xinfu-a%22%3B%7Di%3A5%3Ba%3A3%3A%7Bs%3A7%3A%22pair_ID%22%3Bs%3A6%3A%22953915%22%3Bs%3A10%3A%22pair_title%22%3Bs%3A0%3A%22%22%3Bs%3A9%3A%22pair_link%22%3Bs%3A45%3A%22%2Fequities%2Fshanghai-runda-medical-technology-c%22%3B%7Di%3A6%3Ba%3A3%3A%7Bs%3A7%3A%22pair_ID%22%3Bs%3A6%3A%22944923%22%3Bs%3A10%3A%22pair_title%22%3Bs%3A0%3A%22%22%3Bs%3A9%3A%22pair_link%22%3Bs%3A23%3A%22%2Fequities%2Fxj-goldwind-a%22%3B%7D%7D%7D%7D; billboardCounter_6=0; __atuvc=84%7C36; __atuvs=5d6f486c95ffce8900c; nyxDorf=MTUyYDNlN3VmMTo%2BNGM5JWc3P2MxPzcrZWUzODY5; Hm_lpvt_a1e3d50107c2a0e021d734fe76f85914=1567575905
Host: cn.investing.com
Origin: https://cn.investing.com
Referer: https://cn.investing.com/equities/xj-goldwind-a-technical
Sec-Fetch-Mode: cors
Sec-Fetch-Site: same-origin
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36
X-Requested-With: XMLHttpRequest
"""


def Test_prepare(self):
    pass


def Test_work(self):
    r = requests.post(url=URL, data=BODY, headers=HEADERS_IN_USE, timeout=5, verify=False)

    if r.status_code != 200:
        raise Exception
    else:
        self.c = 0
    print(r.text)
    with open("1.html", "w", encoding="utf-8") as f:
        f.write(r.text)
    raise ExitSignal


def Test_exception(self):
    pass


def test_meta():
    newFetcher = create_new_fetcher("TestFetcher", Test_prepare, Test_work, Test_exception)
    n = newFetcher()
    print(n.name, n.uuid)
    n.run_test()
    exit(1)


def mk_header(str):
    lines = list(str.strip().split("\n"))
    pairs = list(map(lambda line: (line.split(": ")[0], line.split(": ")[1]), lines))
    header = {pair[0]: pair[1] for pair in pairs}
    return header


if __name__ == "__main__":
    test_meta()
