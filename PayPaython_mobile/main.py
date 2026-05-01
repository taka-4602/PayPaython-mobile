import requests
from uuid import uuid4
import pkce
import random
from typing import NamedTuple

'''def generate_sentry():
    trace_id = uuid4().hex
    span_id = uuid4().hex[16:]

    class SENTRY_TRACE_SPAN(NamedTuple):
        trace_id:str
        span_id:str
        sentry_trace:str
        sentry_trace_0:str
        sentry_trace_1:str
    
    return SENTRY_TRACE_SPAN(trace_id, span_id, f"{trace_id}-{span_id}", f"{trace_id}-{span_id}-0", f"{trace_id}-{span_id}-1")'''

def generate_vector(r1, r2, r3, precision=8):
    v1 = f"{random.uniform(*r1):.{precision}f}"
    v2 = f"{random.uniform(*r2):.{precision}f}"
    v3 = f"{random.uniform(*r3):.{precision}f}"
    return f"{v1}_{v2}_{v3}"

def generate_device_state():
    device_orientation = generate_vector(
        (2.2, 2.6),
        (-0.2, -0.05),
        (-0.05, 0.1)
    )
    device_orientation_2 = generate_vector(
        (2.0, 2.6),
        (-0.2, -0.05),
        (-0.05, 0.2)
    )
    device_rotation = generate_vector(
        (-0.8, -0.6),
        (0.65, 0.8),
        (-0.12, -0.04)
    )
    device_rotation_2 = generate_vector(
        (-0.85, -0.4),
        (0.53, 0.9),
        (-0.15, -0.03)
    )
    device_acceleration = generate_vector(
        (-0.35, 0.0),
        (-0.01, 0.3),
        (-0.1, 0.1)
    )
    device_acceleration_2 = generate_vector(
        (0.01, 0.04),
        (-0.04, 0.09),
        (-0.03, 0.1)
    )
    class DeviceHeaders(NamedTuple):
        device_orientation: str
        device_orientation_2: str
        device_rotation: str
        device_rotation_2: str
        device_acceleration: str
        device_acceleration_2: str

    return DeviceHeaders(
        device_orientation,
        device_orientation_2,
        device_rotation,
        device_rotation_2,
        device_acceleration,
        device_acceleration_2
    )

'''sentry_public_key="e5f3c063d55d3058bc5bfb0f311152e4"
def update_header_baggage(header:dict,public_key:str,sample_rate:str=None,sampled:bool=None,transaction:str=None,sentry_trace_style:int=None):
    baggage = "sentey-environment=Production," + f"sentry-public_key={public_key},sentry-release=consumer-android%404.78.1%2B47801"
    if sample_rate:
        baggage = baggage + f",sentry-sample_rate={sample_rate}"

    if sampled!=None:
        if sampled:
            baggage = baggage + ",sentry-sampled=true"
        else:
            baggage = baggage + ",sentry-sampled=false"

    #sentry_ids = generate_sentry()
    baggage = baggage + f",sentry-trace_id={sentry_ids.trace_id}"

    if transaction:
        baggage = baggage + f",sentry-transaction={transaction}"

    if sentry_trace_style == 0:
        header[#"sentry-trace"] = sentry_ids.sentry_trace_0
    elif sentry_trace_style == 1:
        header[#"sentry-trace"] = sentry_ids.sentry_trace_1
    else:
        header[#"sentry-trace"] = sentry_ids.sentry_trace
    
    header[#"baggage"] = baggage
    return header'''

class PayPayError(Exception):
    pass
class PayPayLoginError(Exception):
    pass
class P2PTemporaryHoldError(Exception):
    pass
class PayPayNetWorkError(Exception):
    pass
class PayPay():
    def __init__(self, phone:str=None, password:str=None, device_uuid:str=None, client_uuid:str=str(uuid4()), access_token:str=None, proxy:str | dict=None):
        
        if phone and "-" in phone:
            phone = phone.replace("-","")

        self.session = requests.Session()

        if device_uuid:
            self.device_uuid = device_uuid
        else:
            self.device_uuid = str(uuid4())
            
        self.client_uuid = client_uuid

        if isinstance(proxy, str):
            if not "http" in proxy:
                proxy = "http://" + proxy

            self.session.proxies = {"https":proxy,"http":proxy}
            self.proxy = proxy

        elif isinstance(proxy, dict):
            self.session.proxies = proxy
        
            self.proxy = proxy["http"]
        

        self.params={
            "payPayLang":"ja"
        }
        #try:
        #    iosstore=self.session.get("https://apps.apple.com/jp/app/paypay-%E3%83%9A%E3%82%A4%E3%83%9A%E3%82%A4/id1435783608")
        #except Exception as e:
        #    raise NetWorkError(e)
        
        self.version = "5.11.1" #BeautifulSoup(iosstore.text,"html.parser").find(class_="l-column small-6 medium-12 whats-new__latest__version").text.split()[1]
        device_state = generate_device_state()
        self.session.headers = {
            "Accept": "*/*",
            "Accept-Charset": "UTF-8",
            "Accept-Encoding": "gzip",
            "Client-Mode": "NORMAL",
            "Client-OS-Release-Version": "10",
            "Client-OS-Type": "ANDROID",
            "Client-OS-Version": "29.0.0",
            "Client-Type": "PAYPAYAPP",
            "Client-UUID": self.client_uuid,
            "Client-Version": self.version,
            "Connection": "Keep-Alive",
            "Content-Type": "application/x-www-form-urlencoded",
            "Device-Acceleration": device_state.device_acceleration,
            "Device-Acceleration-2": device_state.device_acceleration_2,
            "Device-Brand-Name": "KDDI",
            "Device-Hardware-Name": "qcom",
            "Device-In-Call": "false",
            "Device-Lock-App-Setting": "false",
            "Device-Lock-Type": "NONE",
            "Device-Manufacturer-Name": "samsung",
            "Device-Name": "SCV38",
            "Device-Orientation": device_state.device_orientation,
            "Device-Orientation-2": device_state.device_orientation_2,
            "Device-Rotation": device_state.device_rotation,
            "Device-Rotation-2": device_state.device_rotation_2,
            "Device-UUID": self.device_uuid,
            "Host": "app4.paypay.ne.jp",
            "Is-Emulator": "false",
            "Network-Status": "WIFI",
            "System-Locale": "ja",
            "Timezone": "Asia/Tokyo",
            "User-Agent": f"PaypayApp/{self.version} Android10"
        }
        if access_token:
            self.access_token = access_token
            self.session.headers["Authorization"] = f"Bearer {self.access_token}"
            self.session.headers["content-type"] = "application/json"

        elif phone:
            self.access_token = None
            self.refresh_token = None
            self.code_verifier, self.code_challenge = pkce.generate_pkce_pair(43)
            ##self.session.headers=update_header_baggage(self.session.headers,sentry_public_key,"0",False,"OAuth2Fragment",0)

            payload = {
                "clientId": "pay2-mobile-app-client",
                "clientAppVersion": self.version,
                "clientOsVersion": "29.0.0",
                "clientOsType": "ANDROID",
                "redirectUri": "paypay://oauth2/callback",
                "responseType": "code",
                "state": pkce.generate_code_verifier(43),
                "codeChallenge": self.code_challenge,
                "codeChallengeMethod": "S256",
                "scope": "REGULAR",
                "tokenVersion": "v2",
                "prompt": "",
                "uiLocales": "ja"
            }
            response = self.session.post("https://app4.paypay.ne.jp/bff/v2/oauth2/par?payPayLang=ja", data=payload)
            try:
                response_json = response.json()
            except:
                raise PayPayNetWorkError("日本以外からは接続できません")
            
            if response_json["header"]["resultCode"] != "S0000":
                raise PayPayLoginError(response_json)
            
            headers = {
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
                "Accept-Encoding": "gzip, deflate, br, zstd",
                "Accept-Language": "ja-JP,ja;q=0.9",
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "Host": "www.paypay.ne.jp",
                "is-emulator": "false",
                "Pragma": "no-cache",
                "sec-ch-ua": '"Not A(Brand";v="8", "Chromium";v="132", "Android WebView";v="132"',
                "sec-ch-ua-mobile": "?1",
                "sec-ch-ua-platform": '"Android"',
                "Sec-Fetch-Dest": "document",
                "Sec-Fetch-Mode": "navigate",
                "Sec-Fetch-Site": "none",
                "Sec-Fetch-User": "?1",
                "Upgrade-Insecure-Requests": "1",
                "User-Agent": f"Mozilla/5.0 (Linux; Android 10; SCV38 Build/QP1A.190711.020; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/132.0.6834.163 Mobile Safari/537.36 jp.pay2.app.android/{self.version}",
                "X-Requested-With": "jp.ne.paypay.android.app"
            }
            params = {
                "client_id": "pay2-mobile-app-client",
                "request_uri": response_json["payload"]["requestUri"]
            }
            auth_1 = self.session.get("https://www.paypay.ne.jp/portal/api/v2/oauth2/authorize", headers=headers, params=params)
            raise PayPayLoginError("このモジュールは現在、アンチボット対策を実装していません\nアクセストークンが欲しい場合は\nhttps://github.com/taka-4602/PayPaython-mobile\nへアクセスして、ドキュメントを確認してください")
            
            params = {
                "client_id": "pay2-mobile-app-client",
                "mode": "landing"
            }
            self.session.get("https://www.paypay.ne.jp/portal/oauth2/sign-in", headers=headers, params=params)
            
            #sentry_ids = generate_sentry()
            headers = {
                "Accept": "application/json, text/plain, */*",
                "Accept-Encoding": "gzip, deflate, br, zstd",
                "Accept-Language": "ja-JP,ja;q=0.9",
                #"baggage": f"sentry-environment=Production,sentry-release=4.75.0,sentry-public_key=a5e3ae80a20e15b8de50274dd231ab83,sentry-trace_id={sentry_ids.trace_id},sentry-sample_rate=0.0005,sentry-transaction=SignIn,sentry-sampled=false",
                "Cache-Control": "no-cache",
                "Client-Id": "pay2-mobile-app-client",
                "Client-Type": "PAYPAYAPP",
                "Connection": "keep-alive",
                "Host": "www.paypay.ne.jp",
                "Pragma": "no-cache",
                "Referer": "https://www.paypay.ne.jp/portal/oauth2/sign-in?client_id=pay2-mobile-app-client&mode=landing",
                "sec-ch-ua": '"Not A(Brand";v="8", "Chromium";v="132", "Android WebView";v="132")',
                "sec-ch-ua-mobile": "?1",
                "sec-ch-ua-platform": '"Android"',
                "Sec-Fetch-Dest": "empty",
                "Sec-Fetch-Mode": "cors",
                "Sec-Fetch-Site": "same-origin",
                #"sentry-trace": sentry_ids.sentry_trace_0,
                "User-Agent": f"Mozilla/5.0 (Linux; Android 10; SCV38 Build/QP1A.190711.020; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/132.0.6834.163 Mobile Safari/537.36 jp.pay2.app.android/{self.version}",
                "X-Requested-With": "jp.ne.paypay.android.app"
            }
            response = self.session.get("https://www.paypay.ne.jp/portal/api/v2/oauth2/par/check",headers=headers).json()
            if response["header"]["resultCode"] != "S0000":
                raise PayPayLoginError(response)
            
            #sentry_ids = generate_sentry()
            headers = {
                "Accept": "application/json, text/plain, */*",
                "Accept-Encoding": "gzip, deflate, br, zstd",
                "Accept-Language": "ja-JP,ja;q=0.9",
                #"baggage": f"sentry-environment=Production,sentry-release=4.75.0,sentry-public_key=a5e3ae80a20e15b8de50274dd231ab83,sentry-trace_id={sentry_ids.trace_id}",
                "Cache-Control": "no-cache",
                "Client-Id": "pay2-mobile-app-client",
                "Client-OS-Type": "ANDROID",
                "Client-OS-Version": "29.0.0",
                "Client-Type": "PAYPAYAPP",
                "Client-Version": self.version,
                "Connection": "keep-alive",
                "Content-Type": "application/json",
                "Host": "www.paypay.ne.jp",
                "Origin": "https://www.paypay.ne.jp",
                "Pragma": "no-cache",
                "Referer": "https://www.paypay.ne.jp/portal/oauth2/sign-in?client_id=pay2-mobile-app-client&mode=landing",
                "sec-ch-ua": '"Not A(Brand";v="8", "Chromium";v="132", "Android WebView";v="132")',
                "sec-ch-ua-mobile": "?1",
                "sec-ch-ua-platform": '"Android"',
                "Sec-Fetch-Dest": "empty",
                "Sec-Fetch-Mode": "cors",
                "Sec-Fetch-Site": "same-origin",
                #"sentry-trace": sentry_ids.sentry_trace,
                "User-Agent": f"Mozilla/5.0 (Linux; Android 10; SCV38 Build/QP1A.190711.020; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/132.0.6834.163 Mobile Safari/537.36 jp.pay2.app.android/{self.version}",
                "X-Requested-With": "jp.ne.paypay.android.app"
            }
            payload={
                "username":phone,
                "password":password,
                "signInAttemptCount":1
            }
            response = self.session.post("https://www.paypay.ne.jp/portal/api/v2/oauth2/sign-in/password",headers=headers,json=payload).json()
            if response["header"]["resultCode"] != "S0000":
                raise PayPayLoginError(response)

            if device_uuid:
                try:
                    uri = response["payload"]["redirectUrl"].replace("paypay://oauth2/callback?","").split("&")
                except:
                    raise PayPayLoginError("登録されていないDevice-UUID")
                
                headers = self.session.headers
                del headers["Device-Lock-Type"]
                del headers["Device-Lock-App-Setting"]
                #del headers["baggage"]
                #del headers["sentry-trace"]

                confirm_data={
                    "clientId":"pay2-mobile-app-client",
                    "redirectUri":"paypay://oauth2/callback",
                    "code":uri[0].replace("code=",""),
                    "codeVerifier":self.code_verifier
                }
                response = self.session.post("https://app4.paypay.ne.jp/bff/v2/oauth2/token", headers=headers, data=confirm_data, params=self.params).json()
                if response["header"]["resultCode"] != "S0000":
                    raise PayPayLoginError(response)
                
                self.access_token = response["payload"]["accessToken"]
                self.refresh_token = response["payload"]["refreshToken"]
                self.session.headers["Authorization"] = f"Bearer {self.access_token}"
                self.session.headers["content-type"] = "application/json"
                self.session.headers = self._update_header_device_state()

            else:
                response = self.session.post("https://www.paypay.ne.jp/portal/api/v2/oauth2/extension/code-grant/update", headers=headers, json={}).json()
                if response["header"]["resultCode"] != "S0000":
                    raise PayPayLoginError(response)

                headers["Referer"]="https://www.paypay.ne.jp/portal/oauth2/verification-method?client_id=pay2-mobile-app-client&mode=navigation-2fa"
                payload={
                    "params":{
                        "extension_id":"user-main-2fa-v1",
                        "data":{
                            "type":"SELECT_FLOW",
                            "payload":{
                                "flow":"OTL",
                                "sign_in_method":"MOBILE",
                                "base_url":"https://www.paypay.ne.jp/portal/oauth2/l"
                                }
                            }
                        }
                    }
                
                response = self.session.post("https://www.paypay.ne.jp/portal/api/v2/oauth2/extension/code-grant/update",headers=headers,json=payload).json()
                if response["header"]["resultCode"] != "S0000":
                    raise PayPayLoginError(response)
                
                headers["Referer"] = "https://www.paypay.ne.jp/portal/oauth2/otl-request?client_id=pay2-mobile-app-client&mode=navigation-2fa"
                response = self.session.post("https://www.paypay.ne.jp/portal/api/v2/oauth2/extension/code-grant/side-channel/next-action-polling",headers=headers,json={"waitUntil": "PT5S"}).json()
                if response["header"]["resultCode"] != "S0000":
                    raise PayPayLoginError(response)


    def _update_header_device_state(self):
        device_state = generate_device_state()
        self.session.headers["Device-Orientation"] = device_state.device_orientation
        self.session.headers["Device-Orientation-2"] = device_state.device_orientation_2
        self.session.headers["Device-Rotation"] = device_state.device_rotation
        self.session.headers["Device-Rotation-2"] = device_state.device_rotation_2
        self.session.headers["Device-Acceleration"] = device_state.device_acceleration
        self.session.headers["Device-Acceleration-2"] = device_state.device_acceleration_2

    def login(self, url:str):
        if "https://" in url:
            url = url.replace("https://www.paypay.ne.jp/portal/oauth2/l?id=", "")

        #sentry_ids = generate_sentry()
        headers = {
            "Accept": "application/json, text/plain, */*",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Accept-Language": "ja-JP,ja;q=0.9",
            #"baggage": f"sentry-environment=Production,sentry-release=4.75.0,sentry-public_key=a5e3ae80a20e15b8de50274dd231ab83,sentry-trace_id={sentry_ids.trace_id},sentry-sample_rate=0.0005,sentry-transaction=OTL,sentry-sampled=false",
            "Cache-Control": "no-cache",
            "Client-Id": "pay2-mobile-app-client",
            "Client-OS-Type": "ANDROID",
            "Client-OS-Version": "29.0.0",
            "Client-Type": "PAYPAYAPP",
            "Client-Version": self.version,
            "Connection": "keep-alive",
            "Content-Type": "application/json",
            "Host": "www.paypay.ne.jp",
            "Origin": "https://www.paypay.ne.jp",
            "Pragma": "no-cache",
            "Referer": f"https://www.paypay.ne.jp/portal/oauth2/l?id={url}&client_id=pay2-mobile-app-client",
            "sec-ch-ua": '"Not A(Brand";v="8", "Chromium";v="132", "Android WebView";v="132")',
            "sec-ch-ua-mobile": "?1",
            "sec-ch-ua-platform": '"Android"',
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
            #"sentry-trace": sentry_ids.sentry_trace_0,
            "User-Agent": f"Mozilla/5.0 (Linux; Android 10; SCV38 Build/QP1A.190711.020; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/132.0.6834.163 Mobile Safari/537.36 jp.pay2.app.android/{self.version}",
            "X-Requested-With": "jp.ne.paypay.android.app"
        }
        response = self.session.post("https://www.paypay.ne.jp/portal/api/v2/oauth2/extension/sign-in/2fa/otl/verify",headers=headers,json={"code":url}).json()
        if response["header"]["resultCode"] != "S0000":
            raise PayPayLoginError(response)
        
        payload={
            "params":{
            "extension_id":"user-main-2fa-v1",
            "data":{
                "type":"COMPLETE_OTL",
                "payload":None
                }
            }
        }
        response = self.session.post("https://www.paypay.ne.jp/portal/api/v2/oauth2/extension/code-grant/update", headers=headers, json=payload).json()
        if response["header"]["resultCode"] != "S0000":
            raise PayPayLoginError(response)
        
        try:
            uri = response["payload"]["redirect_uri"].replace("paypay://oauth2/callback?","").split("&")
        except:
            raise PayPayLoginError('redirect_uriが見つかりませんでした\n' + str(response))

        headers = self.session.headers
        del headers["Device-Lock-Type"]
        del headers["Device-Lock-App-Setting"]
        #del headers["baggage"]
        #del headers["sentry-trace"]

        confirm_data={
            "clientId":"pay2-mobile-app-client",
            "redirectUri":"paypay://oauth2/callback",
            "code":uri[0].replace("code=",""),
            "codeVerifier":self.code_verifier
        }
        response = self.session.post("https://app4.paypay.ne.jp/bff/v2/oauth2/token", headers=headers, data=confirm_data, params=self.params).json()
        if response["header"]["resultCode"] != "S0000":
            raise PayPayLoginError(response)
        
        self.access_token = response["payload"]["accessToken"] #90日もつよ
        self.refresh_token = response["payload"]["refreshToken"]
        self.session.headers["Authorization"] = f"Bearer {self.access_token}"
        self.session.headers["content-type"] = "application/json"
        self.session.headers = self._update_header_device_state()

        return response
    
    def token_refresh(self, refresh_token:str) -> dict:
        return "deleted from endpoint"
        if not self.access_token:
            raise PayPayLoginError("まずはログインしてください")
        
        #self.session.headers=update_header_baggage(self.session.headers,sentry_public_key,"0",False,"OAuth2Fragment",0)
        form_data = {
            "clientId": "pay2-mobile-app-client",
            "refreshToken": refresh_token,
            "tokenVersion": "v2"
        }
        response = self.session.post("https://app4.paypay.ne.jp/bff/v2/oauth2/refresh", data=form_data).json()

        if response["header"]["resultCode"] == "S0001" or response["header"]["resultCode"] == "S1003":
            raise PayPayLoginError(response)
        
        if response["header"]["resultCode"] == "S0003":
            raise PayPayLoginError(response)
        
        if response["header"]["resultCode"] != "S0000":
            raise PayPayError(response)
        
        self.access_token = response["payload"]["accessToken"]
        self.refresh_token = response["payload"]["refreshToken"]
        self.session.headers["Authorization"] = f"Bearer {response['payload']['accessToken']}"

        return response

    def get_history(self, size:int=20, cashback:bool=False) -> dict:
        if not self.access_token:
            raise PayPayLoginError("まずはログインしてください")

        #self.session.headers=update_header_baggage(self.session.headers,sentry_public_key,"0.0099999997764826",False,"TransactionHistoryV2Fragment",0)

        params = {
            "pageSize": str(size),
            "orderTypes": "",
            "paymentMethodTypes": "",
            "signUpCompletedAt": "2021-01-02T10:16:24Z",
            "isOverdraftOnly": "false",
            "payPayLang": "ja"
        }
        if cashback:
            params["orderTypes"] = "CASHBACK"

        response = self.session.get(f"https://app4.paypay.ne.jp/bff/v3/getPaymentHistory", params=params).json()

        if response["header"]["resultCode"] == "S0001":
            raise PayPayLoginError(response)
        
        if response["header"]["resultCode"] != "S0000":
            raise PayPayError(response)
        
        return response

    def get_balance(self):
        if not self.access_token:
            raise PayPayLoginError("まずはログインしてください")

        #self.session.headers=update_header_baggage(self.session.headers,sentry_public_key,"0",False,"WalletAssetDetailsFragment")

        params = {
            "includePendingBonusLite": "false",
            "includePending": "true",
            "noCache": "true",
            "includeKycInfo": "true",
            "includePayPaySecuritiesInfo": "true",
            "includePointInvestmentInfo": "true",
            "includePayPayBankInfo": "true",
            "includeGiftVoucherInfo": "true",
            "payPayLang": "ja"
        }
        response = self.session.get("https://app4.paypay.ne.jp/bff/v1/getBalanceInfo",params=params).json()

        if response["header"]["resultCode"] == "S0001":
            raise PayPayLoginError(response)
        
        if response["header"]["resultCode"] != "S0000":
            raise PayPayError(response)
        
        try:
            money = response["payload"]["walletDetail"]["emoneyBalanceInfo"]["balance"]
        except:
            money = None

        class GetBalance(NamedTuple):
            money: int
            money_light: int
            all_balance: int
            useable_balance: int
            points: int
            raw: dict
        
        money_light = response["payload"]["walletDetail"]["prepaidBalanceInfo"]["balance"]
        all_balance = response["payload"]["walletSummary"]["allTotalBalanceInfo"]["balance"]
        useable_balance = response["payload"]["walletSummary"]["usableBalanceInfoWithoutCashback"]["balance"]
        points = response["payload"]["walletDetail"]["cashBackBalanceInfo"]["balance"]

        return GetBalance(money,money_light,all_balance,useable_balance,points,response)

    def link_check(self, url:str, web_api:bool=False):
        if "https://" in url:
            url = url.replace("https://pay.paypay.ne.jp/","")

        if web_api:
            headers={
                "Accept":"application/json, text/plain, */*",
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
                "Content-Type":"application/json"
            }
            link_info = requests.get(f"https://www.paypay.ne.jp/app/v2/p2p-api/getP2PLinkInfo?verificationCode={url}", headers=headers).json()
            
        else:
            if not self.access_token:
                raise PayPayLoginError("まずはログインしてください")

            #self.session.headers=update_header_baggage(self.session.headers,sentry_public_key,"0.0099999997764826",False,"P2PMoneyTransferDetailFragment",0)
            params={
                "verificationCode": url,
                "payPayLang": "ja"
            }
            link_info = self.session.get("https://app4.paypay.ne.jp/bff/v2/getP2PLinkInfo",params=params).json()
        
        if link_info["header"]["resultCode"] == "S0001":
            raise PayPayLoginError(link_info)
        
        if link_info["header"]["resultCode"] != "S0000":
            raise PayPayError(link_info)
        
        class LinkInfo(NamedTuple):
            sender_name: str
            sender_external_user_id: str
            sender_icon: str
            order_id: str
            chat_room_id: str
            amount: int
            status: str
            money_light: int
            money: int
            has_password: bool
            raw: dict

        sender_name = link_info["payload"]["sender"]["displayName"]
        sender_external_user_id = link_info["payload"]["sender"]["externalId"]
        sender_icon = link_info["payload"]["sender"]["photoUrl"]
        order_id = link_info["payload"]["pendingP2PInfo"]["orderId"]
        chat_room_id = link_info["payload"]["message"]["chatRoomId"]
        amount = link_info["payload"]["pendingP2PInfo"]["amount"]
        status = link_info["payload"]["message"]["data"]["status"]
        money_light = link_info["payload"]["message"]["data"]["subWalletSplit"]["senderPrepaidAmount"]
        money = link_info["payload"]["message"]["data"]["subWalletSplit"]["senderEmoneyAmount"]
        has_password = link_info["payload"]["pendingP2PInfo"]["isSetPasscode"]

        return LinkInfo(sender_name,sender_external_user_id,sender_icon,order_id,chat_room_id,amount,status,money_light,money,has_password,link_info)
    
    def link_receive(self, url:str, passcode:str=None, link_info:dict=None) -> dict:
        if not self.access_token:
            raise PayPayLoginError("まずはログインしてください")

        if "https://" in url:
            url = url.replace("https://pay.paypay.ne.jp/","")

        if not link_info:
            #self.session.headers=update_header_baggage(self.session.headers,sentry_public_key,"0.0099999997764826",False,"P2PMoneyTransferDetailFragment",0)
            params={
                "verificationCode": url,
                "payPayLang": "ja"
            }
            link_info = self.session.get("https://app4.paypay.ne.jp/bff/v2/getP2PLinkInfo", params=params).json()
        
        if link_info["header"]["resultCode"] == "S0001":
            raise PayPayLoginError(link_info)
        
        if link_info["header"]["resultCode"] != "S0000":
            raise PayPayError(link_info)
        
        #self.session.headers=update_header_baggage(self.session.headers,sentry_public_key)
        payload={
            "requestId":str(uuid4()),
            "orderId":link_info["payload"]["pendingP2PInfo"]["orderId"],
            "verificationCode":url,
            "passcode":None,
            "senderMessageId":link_info["payload"]["message"]["messageId"],
            "senderChannelUrl":link_info["payload"]["message"]["chatRoomId"]
        }
        
        
        if link_info["payload"]["orderStatus"] != "PENDING":
            raise PayPayError("すでに 受け取り / 辞退 / キャンセル されているリンクです")
        
        if link_info["payload"]["pendingP2PInfo"]["isSetPasscode"] and passcode==None:
            raise PayPayError("このリンクにはパスワードが設定されています")
    
        if link_info["payload"]["pendingP2PInfo"]["isSetPasscode"]:
            payload["passcode"] = passcode
            
        response = self.session.post("https://app4.paypay.ne.jp/bff/v2/acceptP2PSendMoneyLink",json=payload,params={"payPayLang":"ja","appContext":"P2PMoneyTransferDetailScreen_linkReceiver"})
        try:
            response = response.json()
        except:
            raise PayPayNetWorkError("日本以外からは接続できません")
        
        if response["header"]["resultCode"] == "S0001":
            raise PayPayLoginError(response)
        
        if response["header"]["resultCode"] != "S0000":
            if response["error"]["backendResultCode"] == "42007013":
                raise P2PTemporaryHoldError(response)
            
            raise PayPayError(response)
        
        return response
    
    def link_reject(self, url:str, link_info:dict=None) -> dict:
        if not self.access_token:
            raise PayPayLoginError("まずはログインしてください")

        if "https://" in url:
            url = url.replace("https://pay.paypay.ne.jp/","")

        if not link_info:
            #self.session.headers=update_header_baggage(self.session.headers,sentry_public_key,"0.0099999997764826",False,"P2PMoneyTransferDetailFragment",0)
            params={
                "verificationCode": url,
                "payPayLang": "ja"
            }
            link_info = self.session.get("https://app4.paypay.ne.jp/bff/v2/getP2PLinkInfo", params=params).json()
        
        #self.session.headers=update_header_baggage(self.session.headers,sentry_public_key)
        payload={
            "requestId":str(uuid4()),
            "orderId":link_info["payload"]["pendingP2PInfo"]["orderId"],
            "verificationCode":url,
            "senderMessageId":link_info["payload"]["message"]["messageId"],
            "senderChannelUrl":link_info["payload"]["message"]["chatRoomId"]
        }
        if link_info["header"]["resultCode"] == "S0001":
            raise PayPayLoginError(link_info)

        if link_info["header"]["resultCode"] != "S0000":
            raise PayPayError(link_info)
        
        if link_info["payload"]["orderStatus"] != "PENDING":
            raise PayPayError("すでに 受け取り / 辞退 / キャンセル されているリンクです")

        response = self.session.post("https://app4.paypay.ne.jp/bff/v2/rejectP2PSendMoneyLink",json=payload,params=self.params).json()
        
        if response["header"]["resultCode"] == "S0001":
            raise PayPayLoginError(response)

        if response["header"]["resultCode"] != "S0000":
            raise PayPayError(response)
        
        return response

    def link_cancel(self, url:str, link_info:dict=None) -> dict:
        if not self.access_token:
            raise PayPayLoginError("まずはログインしてください")

        if "https://" in url:
            url = url.replace("https://pay.paypay.ne.jp/","")

        if not link_info:
            #self.session.headers=update_header_baggage(self.session.headers,sentry_public_key,"0.0099999997764826",False,"P2PMoneyTransferDetailFragment",0)
            params={
                "verificationCode": url,
                "payPayLang": "ja"
            }
            link_info = self.session.get("https://app4.paypay.ne.jp/bff/v2/getP2PLinkInfo", params=params).json()

        #self.session.headers=update_header_baggage(self.session.headers,sentry_public_key)
        payload = {
            "orderId":link_info["payload"]["pendingP2PInfo"]["orderId"],
            "requestId":str(uuid4()),
            "verificationCode":url,
        }
        if link_info["header"]["resultCode"] == "S0001":
            raise PayPayLoginError(link_info)

        if link_info["header"]["resultCode"] != "S0000":
            raise PayPayError(link_info)
        
        if link_info["payload"]["orderStatus"] != "PENDING":
            raise PayPayError("すでに 受け取り / 辞退 / キャンセル されているリンクです")
        
        response = self.session.post("https://app4.paypay.ne.jp/p2p/v1/cancelP2PSendMoneyLink", json=payload, params=self.params).json()
        
        if response["header"]["resultCode"] == "S0001":
            raise PayPayLoginError(response)
        
        if response["header"]["resultCode"] != "S0000":
            raise PayPayError(response)
        
        return response

    def create_link(self, amount:int, passcode:str=None, pochibukuro:bool=False, theme:str="default-sendmoney"):
        if not self.access_token:
            raise PayPayLoginError("まずはログインしてください")

        #self.session.headers=update_header_baggage(self.session.headers,sentry_public_key)
        payload={
            "requestId":str(uuid4()),
            "amount":amount,
            "socketConnection": "P2P",
            "theme":theme,
            "source":"sendmoney_home_sns"
        }
        if passcode:
            payload["passcode"] = passcode

        if pochibukuro:
            payload["theme"] = "pochibukuro"

        response = self.session.post("https://app4.paypay.ne.jp/bff/v2/executeP2PSendMoneyLink", json=payload, params=self.params)
        try:
            response = response.json()
        except:
            raise PayPayNetWorkError("日本以外からは接続できません")
        
        if response["header"]["resultCode"] == "S0001":
            raise PayPayLoginError(response)
        
        if response["header"]["resultCode"] != "S0000":
            raise PayPayError(response)
        
        class CreateLink(NamedTuple):
            link: str
            chat_room_id: str
            order_id: str
            raw: dict

        link = response["payload"]["link"]
        chat_room_id = response["payload"]["chatRoomId"]
        order_id = response["payload"]["orderId"]
        
        return CreateLink(link,chat_room_id,order_id,response)

    def send_money(self, amount:int, receiver_id:str, pochibukuro:bool=False, theme:str="default-sendmoney"):
        if not self.access_token:
            raise PayPayLoginError("まずはログインしてください")

        #self.session.headers=update_header_baggage(self.session.headers,sentry_public_key)
        payload = {
            "amount":amount,
            "theme":theme,
            "requestId":str(uuid4()),
            "externalReceiverId":receiver_id,
            "ackRiskError":False,
            "source":"sendmoney_history_chat",
            "socketConnection": "P2P"
        }
        if pochibukuro:
            payload["theme"] = "pochibukuro"

        response = self.session.post(f"https://app4.paypay.ne.jp/p2p/v3/executeP2PSendMoney",json=payload,params=self.params)
        try:
            response = response.json()
        except:
            raise PayPayNetWorkError("日本以外からは接続できません")
        
        if response["header"]["resultCode"] == "S0001":
            raise PayPayLoginError(response )
        
        if response["header"]["resultCode"] != "S0000":
            raise PayPayError(response)

        class SendMoney(NamedTuple):
            chat_room_id: str
            order_id: str
            raw: dict
        
        chat_room_id = response["payload"]["chatRoomId"]
        order_id = response["payload"]["orderId"]
        
        return SendMoney(chat_room_id,order_id,response)
    
    def send_message(self,chat_room_id:str,message:str) -> dict:
        if not self.access_token:
            raise PayPayLoginError("まずはログインしてください")

        #if not "sendbird_group_channel_" in chat_room_id:
        #    chat_room_id="sendbird_group_channel_" + chat_room_id
        
        #self.session.headers=update_header_baggage(self.session.headers,sentry_public_key)
        payload = {
            "channelUrl":chat_room_id,
            "message":message,
            "socketConnection": "P2P"
        }
        response = self.session.post("https://app4.paypay.ne.jp/p2p/v1/sendP2PMessage",json=payload,params=self.params).json()
        
        if response["header"]["resultCode"] == "S0001":
            raise PayPayLoginError(response)
        
        if response["header"]["resultCode"] != "S0000":
            raise PayPayError(response)
        
        return response
    
    def create_p2pcode(self,amount:int=None):
        if not self.access_token:
            raise PayPayLoginError("まずはログインしてください")
        
        #self.session.headers=update_header_baggage(self.session.headers,sentry_public_key)
        payload = {
            "amount":None,
            "sessionId":None
        }
        if amount:
            payload["amount"]=amount
            payload["sessionId"]=str(uuid4())
            
        response = self.session.post("https://app4.paypay.ne.jp/bff/v1/createP2PCode", json=payload, params=self.params).json()
        
        if response["header"]["resultCode"] == "S0001":
            raise PayPayLoginError(response)
        
        if response["header"]["resultCode"] != "S0000":
            raise PayPayError(response)
        
        class P2PCode(NamedTuple):
            p2pcode: str
            raw: dict

        p2pcode = response["payload"]["p2pCode"]

        return P2PCode(p2pcode, response)
    
    def get_profile(self):
        if not self.access_token:
            raise PayPayLoginError("まずはログインしてください")
        
        #self.session.headers=update_header_baggage(self.session.headers,sentry_public_key,"0",False,"ProfileFragment",0)
        response = self.session.get("https://app4.paypay.ne.jp/bff/v2/getProfileDisplayInfo", params={"includeExternalProfileSync":"true","completedOptionalTasks": "ENABLED_NEARBY_DEALS","payPayLang":"ja"}).json()
        
        if response["header"]["resultCode"] == "S0001":
            raise PayPayLoginError(response)

        if response["header"]["resultCode"] != "S0000":
            raise PayPayError(response)
        
        class Profile(NamedTuple):
            name: str
            external_user_id: str
            icon: str
            raw: dict

        name = response["payload"]["userProfile"]["nickName"]
        external_user_id = response["payload"]["userProfile"]["externalUserId"]
        icon = response["payload"]["userProfile"]["avatarImageUrl"]

        return Profile(name, external_user_id, icon, response)

    def set_money_priority(self, paypay_money:bool=False) -> dict:
        if not self.access_token:
            raise PayPayLoginError("まずはログインしてください")

        #self.session.headers=update_header_baggage(self.session.headers,sentry_public_key)

        if paypay_money:
            setting = {"moneyPriority":"MONEY_FIRST"}
        else:
            setting = {"moneyPriority":"MONEY_LITE_FIRST"}

        response = self.session.post("https://app4.paypay.ne.jp/p2p/v1/setMoneyPriority", json=setting, params={"payPayLang":"ja"}).json()
        
        if response["header"]["resultCode"] == "S0001":
            raise PayPayLoginError(response)
        
        if response["header"]["resultCode"] != "S0000":
            raise PayPayError(response)

        return response
    
    def get_chat_rooms(self, size:int=20, last_message:bool=True):
        if not self.access_token:
            raise PayPayLoginError("まずはログインしてください")

        #self.session.headers=update_header_baggage(self.session.headers,sentry_public_key,"0.0099999997764826",False,"P2PChatRoomListFragment",0)
        params = {
            "pageSize":str(size),
            "customTypes":"P2P_CHAT,P2P_CHAT_INACTIVE,P2P_PUBLIC_GROUP_CHAT,P2P_LINK,P2P_OLD",
            "requiresLastMessage":last_message,
            "socketConnection": "P2P",
            "payPayLang":"ja"
        }
        response =self.session.get("https://app4.paypay.ne.jp/p2p/v1/getP2PChatRoomListLite", params=params).json()
        
        if response["header"]["resultCode"] == "S0001":
            raise PayPayLoginError(response)
        
        if response["header"]["resultCode"] == "S5000":
            raise PayPayError("チャットルームが見つかりませんでした")

        if response["header"]["resultCode"] != "S0000":
            raise PayPayError(response)

        return response

    def get_chat_room_messages(self, chat_room_id:str, prev:int=15, next:int=0, include:bool=False) -> dict:
        if not self.access_token:
            raise PayPayLoginError("まずはログインしてください")
        
        if not "sendbird_group_channel_" in chat_room_id:
            chat_room_id = "sendbird_group_channel_" + chat_room_id

        #self.session.headers=update_header_baggage(self.session.headers,sentry_public_key,"0.0099999997764826",False,"P2PChatRoomFragment",0)
        params = {
            "chatRoomId":chat_room_id,
            "include":include,
            "prev":str(prev),
            "next":str(next),
            "payPayLang":"ja"
        }
        response = self.session.get("https://app4.paypay.ne.jp/bff/v1/getP2PMessageList", params=params).json()
        
        if response["header"]["resultCode"] == "S0001":
            raise PayPayLoginError(response)
        
        if response["header"]["resultCode"] == "S5000":
            raise PayPayError("チャットルームが見つかりませんでした")

        if response["header"]["resultCode"] != "S0000":
            raise PayPayError(response)

        return response

    def get_point_history(self) -> dict:
        if not self.access_token:
            raise PayPayLoginError("まずはログインしてください")

        #self.session.headers=update_header_baggage(self.session.headers,sentry_public_key)
        params = {
            "pageSize": "20",
            "orderTypes": "CASHBACK",
            "paymentMethodTypes": "",
            "signUpCompletedAt": "2021-01-02T10:16:24Z",
            "pointType": "REGULAR",
            "isOverdraftOnly": "false",
            "payPayLang": "ja"
        }
        response = self.session.get("https://app4.paypay.ne.jp/bff/v3/getPaymentHistory", params=params).json()
        
        if response["header"]["resultCode"] == "S0001":
            raise PayPayLoginError(response)

        if response["header"]["resultCode"] != "S0000":
            raise PayPayError(response)
        
        return response

    def search_p2puser(self, user_id:str, size:int=10, is_global:bool=True, order:int=0):
        if not self.access_token:
            raise PayPayLoginError("まずはログインしてください")

        #self.session.headers=update_header_baggage(self.session.headers,sentry_public_key)
        payload = {
            "searchTerm":user_id,
            "pageToken":"",
            "pageSize":size,
            "isIngressSendMoney":False,
            "searchTypes":"GLOBAL_SEARCH"
        }
        if not is_global:
            payload["searchTypes"]="FRIEND_AND_CANDIDATE_SEARCH"

        response = self.session.post("https://app4.paypay.ne.jp/p2p/v3/searchP2PUser", json=payload, params=self.params).json()
        if response["header"]["resultCode"] == "S0001":
            raise PayPayLoginError(response)

        if response["header"]["resultCode"] != "S0000":
            if response["error"]["displayErrorResponse"]["description"]=="しばらく時間をおいて、再度お試しください":
                raise PayPayError("レート制限に達しました")
            
            raise PayPayError(response)
        
        if response["payload"]["searchResultEnum"] == "NO_USERS_FOUND":
            raise PayPayError("ユーザーが見つかりませんでした")

        class P2PUser(NamedTuple):
            name: str
            icon: str
            external_user_id: str
            raw: dict

        if is_global:
            name = response["payload"]["globalSearchResult"]["displayName"]
            icon = response["payload"]["globalSearchResult"]["photoUrl"]
            external_user_id = response["payload"]["globalSearchResult"]["externalId"]
        else:
            name = response["payload"]["friendsAndCandidatesSearchResults"]["friends"][order]["displayName"]
            icon = response["payload"]["friendsAndCandidatesSearchResults"]["friends"][order]["photoUrl"]
            external_user_id = response["payload"]["friendsAndCandidatesSearchResults"]["friends"][order]["externalId"]

        return P2PUser(name, icon, external_user_id, response)

    def initialize_chatroom(self, external_user_id:str):
        if not self.access_token:
            raise PayPayLoginError("まずはログインしてください")
        
        #self.session.headers=update_header_baggage(self.session.headers,sentry_public_key,"0.0099999997764826",False,"P2PChatRoomFragment",0)
        payload = {
            "returnChatRoom":True,
            "shouldCheckMessageForFriendshipAppeal":True,
            "externalUserId":external_user_id,
            "socketConnection": "P2P"
        }
        response = self.session.post("https://app4.paypay.ne.jp/p2p/v1/initialiseOneToOneAndLinkChatRoom", json=payload, params=self.params).json()
        if response["header"]["resultCode"] == "S0001":
            raise PayPayLoginError(response)

        if response["header"]["resultCode"] == "S5000":
            raise PayPayError("チャットルームが見つかりませんでした")

        if response["header"]["resultCode"] != "S0000":
            raise PayPayError(response)

        class InitializeChatRoom(NamedTuple):
            chatroom_id: str
            raw: dict

        chatroom_id = response["payload"]["chatRoom"]["chatRoomId"]

        return InitializeChatRoom(chatroom_id, response)

    def get_barcode_info(self, url: str):
        if not self.access_token:
            raise PayPayLoginError("まずはログインしてください")
        
        params = {
            "code": url,
            #"paymentMethodId": "135062845",
            #"paymentMethodType": "PAY_LATER_CC",
            #"lastSelectedHomePaymentMethodId": "135062845",
            #"lastSelectedHomePaymentMethodType": "PAY_LATER_CC",
            "payPayLang": "ja"
        }
        response = self.session.get("https://app4.paypay.ne.jp/bff/v2/getBarcodeInfo", params=params).json()

        if response["header"]["resultCode"] == "S0001":
            raise PayPayLoginError(response)

        if response["header"]["resultCode"] != "S0000":
            raise PayPayError(response)
        
        class BarcodeInfo(NamedTuple):
            amount: int
            user_name: str
            external_user_id: str
            user_icon: str
            raw: dict

        return BarcodeInfo(
            amount=response["payload"]["userCodeInfo"]["amount"],
            user_name=response["payload"]["userCodeInfo"]["userInfo"]["displayName"],
            external_user_id=response["payload"]["userCodeInfo"]["userInfo"]["externalUserId"],
            user_icon=response["payload"]["userCodeInfo"]["userInfo"]["avatarImageUrl"],
            raw=response
        )

    def cashout_to_paypaybank(self, amount:int):
        if not self.access_token:
            raise PayPayLoginError("まずはログインしてください")
        
        payload = {
            "amount": amount,
            "payoutMethodId": "21438946",
            "requestId": str(uuid4()),
            "agreeSimilarTransactionFlag": False,
            "senderName": "ＰＡＹＰＡＹ"
        }
        response = self.session.post("https://app4.paypay.ne.jp/bff/v2/executePayout", json=payload, params=self.params).json()

        if response["header"]["resultCode"] == "S0001":
            raise PayPayLoginError(response)

        if response["header"]["resultCode"] != "S0000":
            raise PayPayError(response)
        
        payout_info = response["payload"]["paymentInfo"]["orderTypeSpecificInfo"]["payoutInfo"]
        class CashoutResult(NamedTuple):
            bank_name: str
            bank_account_type: str
            bank_branch_name: str
            bank_account_number: str
        
        return CashoutResult(
            bank_name=payout_info["bankName"],
            bank_account_type=payout_info["bankAccountType"],
            bank_branch_name=payout_info["bankBranchName"],
            bank_account_number=payout_info["bankAccountNumber"]
        )

    def alive(self) -> None:
        if not self.access_token:
            raise PayPayLoginError("まずはログインしてください")
        
        #self.session.headers=update_header_baggage(self.session.headers,sentry_public_key,"0.0099999997764826",False,"MainActivity",0)
        response = self.session.get("https://app4.paypay.ne.jp/bff/v1/getGlobalServiceStatus?payPayLang=en").json()
        if response["header"]["resultCode"] == "S0001":
            raise PayPayLoginError(response)
        
        if response["header"]["resultCode"] != "S0000":
            raise PayPayError(response)
        
        self.session.post("https://app4.paypay.ne.jp/bff/v3/getHomeDisplayInfo?payPayLang=ja",json={"excludeMissionBannerInfoFlag": False,"includeBeginnerFlag": False,"includeSkinInfoFlag": False,"networkStatus": "WIFI"})
        self.session.get("https://app4.paypay.ne.jp/bff/v1/getSearchBar?payPayLang=ja")