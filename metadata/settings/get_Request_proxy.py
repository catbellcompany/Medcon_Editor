import requests
from random import choice
from requests.exceptions import ProxyError, SSLError, ConnectTimeout
import traceback
import pandas as pd
import random
import urllib3
import os 

user_agent = pd.read_csv(os.getcwd() + '\\metadata\\settings\\8000_UserAgent.csv', header=None)
user_agent = list(user_agent.iloc[:,0])


def get_proxy_list():
    # 텍스트 파일에서 프록시 IP 받아오기
    # 가장 속도가 괜찮았던 11개의 IP 를 넣어놓음
    read_proxy_list = open(os.getcwd() + '\\metadata\\settings\\proxies.txt', 'r')
    # 라인별로 불러오기
    read_proxy_list = read_proxy_list.readlines()
    new_proxy_list = []

    for proxy in read_proxy_list:
        # 엔터 제거
        proxy = proxy.replace("\n", "")
        # IP 삽입
        new_proxy_list.append(proxy)

    return new_proxy_list


def get_requests(URL):
    # 프록시 리스트 받아오기
    proxy_server_list = get_proxy_list()

    # 헤더 지정
    headers = {
        "User-Agent": random.sample(user_agent, 1)[0],
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8"
    }

    # 제대로된 리퀘스트가 나올때까지 반복
    while True:
        # 제대로 동작하는 리퀘스트를 반환할 때까지 반복됨
        # 프록시 서버 중 하나를 선택
        proxy_server = choice(proxy_server_list)
        # 프록시 설정
        proxies = {"http://": proxy_server, 'https://': proxy_server}
        # print(f'proxies: {proxies}')
        try:
            # 리퀘스트 연결
            # resp = requests.get(URL, headers=headers,
            #                     proxies=proxies, timeout=5)
            resp = requests.get(URL, headers=headers,
                                proxies=proxies, timeout=5)
            # 만약 리퀘스트의 html 정보가 비어있지 않으면 반복 종료
            if(resp.text != ""):
                break

        except (ProxyError, SSLError, ConnectTimeout) as e:
            # 한번 테스트한 IP는 리스트에서 제외
            proxy_server_list.remove(proxy_server)
            print(f'proxy len: {len(proxy_server_list)}')

            if(len(proxy_server_list) == 0):
                # 처음부터 끝까지 다 돌았으면 다시 처음부터 IP 가져오기
                proxy_server_list = get_proxy_list()
            continue

    # 리퀘스트 반환
    return resp
