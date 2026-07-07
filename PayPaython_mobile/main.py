import time
import random
from uuid import uuid4
from typing import NamedTuple

import requests
import pkce


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


def update_header_device_state(headers: dict):
    device_state = generate_device_state()
    headers["Device-Orientation"] = device_state.device_orientation
    headers["Device-Orientation-2"] = device_state.device_orientation_2
    headers["Device-Rotation"] = device_state.device_rotation
    headers["Device-Rotation-2"] = device_state.device_rotation_2
    headers["Device-Acceleration"] = device_state.device_acceleration
    headers["Device-Acceleration-2"] = device_state.device_acceleration_2

    return headers

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


class LinkStatus(NamedTuple):
    PENDING = "PENDING"
    SUCCESS = "SUCCESS"
    REJECTED = "REJECTED"
    FAILED = "FAILED" # canceled by sender. why failed?


class PayPayError(Exception):
    pass


class PayPayLoginError(Exception):
    pass


class P2PTemporaryHoldError(Exception):
    pass


class PayPayNetWorkError(Exception):
    pass


class PayPay():
    def __init__(self, phone: str = None, password: str = None, device_uuid: str = None, client_uuid: str = str(uuid4()), access_token: str = None, proxy: str = None):

        if phone and "-" in phone:
            phone = phone.replace("-", "")

        self.session = requests.Session()

        if device_uuid:
            self.device_uuid = device_uuid
            self.registered_device = True
        else:
            self.device_uuid = str(uuid4())
            self.registered_device = False

        self.client_uuid = client_uuid

        self.proxy = proxy
        self.session.proxies = {"http": proxy, "https": proxy} if proxy else {}
        self.phone = phone
        self.password = password
        self.access_token = None
        self.refresh_token = None
        self.code_verifier = None

        self.params = {
            "payPayLang": "ja"
        }

        self.version = "5.57.0"

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


    def request(self, method: str, url: str, **kwargs):
        if method.lower() == "get":
            response = self.session.get(url, **kwargs)

        elif method.lower() == "post":
            response = self.session.post(url, **kwargs)

        else:
            raise ValueError("Invalid HTTP method. Use 'get' or 'post'.")

        try:
            response_json = response.json()
        except:
            raise PayPayNetWorkError(f"Failed to parse JSON response: {response.text}")


        response_header = response_json.get("header", {})
        if response_header:
            result_code = response_header.get("resultCode")
            if result_code == "S0001":
                raise PayPayLoginError(response_json)

            elif result_code == "S4002":
                pass

            elif result_code == "S5000":
                raise PayPayError("チャットルームが見つかりませんでした")

            elif result_code != "S0000":
                try:
                    if response_json["error"]["backendResultCode"] == "42007013":
                        raise P2PTemporaryHoldError(response_json)
                except:
                    pass

                try:
                    if response_json["error"]["displayErrorResponse"]["description"] == "しばらく時間をおいて、再度お試しください":
                        raise PayPayError("レート制限に達しました")
                except KeyError:
                    pass

                raise PayPayError(response_json)

        return response_json

    def login(self):
        if not self.phone:
            raise PayPayLoginError("電話番号を入力してください")

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

        response = self.request("post", "https://app4.paypay.ne.jp/bff/v2/oauth2/par?payPayLang=ja", data=payload)

        if response["header"]["resultCode"] != "S0000":
            raise PayPayLoginError(response)

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
            "request_uri": response["payload"]["requestUri"]
        }

        raise PayPayLoginError("このモジュールは現在、アンチボット対策を実装していません\nアクセストークンが欲しい場合は\nhttps://github.com/taka-4602/PayPaython-mobile\nへアクセスして、ドキュメントを確認してください")

        response = self.session.get(f"https://www.paypay.ne.jp/portal/api/v2/oauth2/authorize", headers=headers, params=params, allow_redirects=False)

        params = {
            "client_id": "pay2-mobile-app-client",
            "mode": "landing"
        }
        response = self.session.get("https://www.paypay.ne.jp/portal/oauth2/sign-in", headers=headers, params=params)
        if response.status_code > 400:
            raise PayPayLoginError("サインインページの取得に失敗しました")

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
        response = self.session.get("https://www.paypay.ne.jp/portal/api/v2/oauth2/par/check", headers=headers)
        par_check = response.json()
        if par_check["header"]["resultCode"] != "S0000":
            raise PayPayLoginError(par_check)

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
        payload = {
            "username": self.phone,
            "password": self.password,
            "signInAttemptCount": 1
        }
        response = self.session.post("https://www.paypay.ne.jp/portal/api/v2/oauth2/sign-in/password", headers=headers, json=payload)
        signin = response.json()
        if signin["header"]["resultCode"] != "S0000":
            raise PayPayLoginError(signin)

        if self.registered_device:
            try:
                uri = signin["payload"]["redirectUrl"].replace("paypay://oauth2/callback?", "").split("&")
            except:
                raise PayPayLoginError("登録されていないDevice-UUID")

            headers = self.session.headers
            del headers["Device-Lock-Type"]
            del headers["Device-Lock-App-Setting"]
            #del headers["baggage"]
            #del headers["sentry-trace"]

            confirm_data = {
                "clientId": "pay2-mobile-app-client",
                "redirectUri": "paypay://oauth2/callback",
                "code": uri[0].replace("code=", ""),
                "codeVerifier": self.code_verifier
            }
            response = self.session.post("https://app4.paypay.ne.jp/bff/v2/oauth2/token", headers=headers, data=confirm_data, params=self.params)
            get_token = response.json()
            if get_token["header"]["resultCode"] != "S0000":
                raise PayPayLoginError(get_token)

            self.access_token = get_token["payload"]["accessToken"]
            self.refresh_token = get_token["payload"]["refreshToken"]
            self.session.headers["Authorization"] = f"Bearer {self.access_token}"
            self.session.headers["content-type"] = "application/json"
            self.session.headers = update_header_device_state(self.session.headers)

        else:
            response = self.session.post("https://www.paypay.ne.jp/portal/api/v2/oauth2/extension/code-grant/update", headers=headers, json={})
            code_update = response.json()
            if code_update["header"]["resultCode"] != "S0000":
                raise PayPayLoginError(code_update)

            headers["Referer"] = "https://www.paypay.ne.jp/portal/oauth2/verification-method?client_id=pay2-mobile-app-client&mode=navigation-2fa"
            payload = {
                "params": {
                    "extension_id": "user-main-2fa-v1",
                    "data": {
                        "type": "SELECT_FLOW",
                        "payload": {
                            "flow": "OTL",
                            "sign_in_method": "MOBILE",
                            "base_url": "https://www.paypay.ne.jp/portal/oauth2/l"
                        }
                    }
                }
            }

            response = self.session.post("https://www.paypay.ne.jp/portal/api/v2/oauth2/extension/code-grant/update", headers=headers, json=payload)
            nav_2fa = response.json()
            if nav_2fa["header"]["resultCode"] != "S0000":
                raise PayPayLoginError(nav_2fa)

            headers["Referer"] = "https://www.paypay.ne.jp/portal/oauth2/otl-request?client_id=pay2-mobile-app-client&mode=navigation-2fa"
            response = self.session.post("https://www.paypay.ne.jp/portal/api/v2/oauth2/extension/code-grant/side-channel/next-action-polling", headers=headers, json={"waitUntil": "PT5S"})
            otl_request = response.json()
            if otl_request["header"]["resultCode"] != "S0000":
                raise PayPayLoginError(otl_request)

    def login_confirm(self, url: str):
        if self.session.headers.get("Authorization"):
            return "already logged in"

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
        response = self.session.post("https://www.paypay.ne.jp/portal/api/v2/oauth2/extension/sign-in/2fa/otl/verify", headers=headers, json={"code": url})
        confirm_url = response.json()
        if confirm_url["header"]["resultCode"] != "S0000":
            raise PayPayLoginError(confirm_url)

        payload = {
            "params": {
                "extension_id": "user-main-2fa-v1",
                "data": {
                    "type": "COMPLETE_OTL",
                    "payload": None
                }
            }
        }
        response = self.session.post("https://www.paypay.ne.jp/portal/api/v2/oauth2/extension/code-grant/update", headers=headers, json=payload)
        get_uri = response.json()
        if get_uri["header"]["resultCode"] != "S0000":
            raise PayPayLoginError(get_uri)

        try:
            uri = get_uri["payload"]["redirect_uri"].replace("paypay://oauth2/callback?", "").split("&")
        except:
            raise PayPayLoginError('redirect_uriが見つかりませんでした\n' + str(get_uri))

        headers = self.session.headers
        del headers["Device-Lock-Type"]
        del headers["Device-Lock-App-Setting"]
        #del headers["baggage"]
        #del headers["sentry-trace"]

        confirm_data = {
            "clientId": "pay2-mobile-app-client",
            "redirectUri": "paypay://oauth2/callback",
            "code": uri[0].replace("code=", ""),
            "codeVerifier": self.code_verifier
        }
        response = self.session.post("https://app4.paypay.ne.jp/bff/v2/oauth2/token", headers=headers, data=confirm_data, params=self.params)
        get_token = response.json()
        if get_token["header"]["resultCode"] != "S0000":
            raise PayPayLoginError(get_token)

        self.access_token = get_token["payload"]["accessToken"]  #90日もつよ
        self.refresh_token = get_token["payload"]["refreshToken"]
        self.session.headers["Authorization"] = f"Bearer {self.access_token}"
        self.session.headers["content-type"] = "application/json"
        self.session.headers = update_header_device_state(self.session.headers)

        return get_token

    def get_history(self, size: int = 20, cashback: bool = False) -> dict:
        if not self.access_token:
            raise PayPayLoginError("まずはログインしてください")

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

        response = self.request("get", f"https://app4.paypay.ne.jp/bff/v4/getPaymentHistory", params=params)

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
        response = self.request("get", "https://app4.paypay.ne.jp/bff/v1/getBalanceInfo", params=params)

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
            bank_balance: int
            raw: dict

        money_light = response["payload"]["walletDetail"]["prepaidBalanceInfo"]["balance"]
        all_balance = response["payload"]["walletSummary"]["allTotalBalanceInfo"]["balance"]
        useable_balance = response["payload"]["walletSummary"]["usableBalanceInfoWithoutCashback"]["balance"]
        points = response["payload"]["walletDetail"]["cashBackBalanceInfo"]["balance"]
        bank_balance = response["payload"].get("payPayBankInfo", {}).get("amount")

        return GetBalance(money, money_light, all_balance, useable_balance, points, bank_balance, response)

    def link_check(self, url: str, web_api: bool = False):
        if "https://" in url:
            url = url.replace("https://pay.paypay.ne.jp/", "")

        if web_api:
            headers = {
                "Accept": "application/json, text/plain, */*",
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
                "Content-Type": "application/json"
            }
            response = self.session.get(f"https://www.paypay.ne.jp/app/v2/p2p-api/getP2PLinkInfo?verificationCode={url}", headers=headers)
            link_info = response.json()

        else:
            if not self.access_token:
                raise PayPayLoginError("まずはログインしてください")

            #self.session.headers=update_header_baggage(self.session.headers,sentry_public_key,"0.0099999997764826",False,"P2PMoneyTransferDetailFragment",0)
            params = {
                "verificationCode": url,
                "payPayLang": "ja"
            }
            link_info = self.request("get", "https://app4.paypay.ne.jp/bff/v2/getP2PLinkInfo", params=params)


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

        return LinkInfo(sender_name, sender_external_user_id, sender_icon, order_id, chat_room_id, amount, status, money_light, money, has_password, link_info)

    def link_receive(self, url: str, passcode: str = None, link_info: dict | LinkInfo = None) -> dict:
        if not self.access_token:
            raise PayPayLoginError("まずはログインしてください")

        try:
            if passcode:
                int(passcode)
                if len(passcode) != 4:
                    raise PayPayError("パスコードは4桁の数字で入力してください")

        except:
            raise PayPayError("パスコードは4桁の数字で入力してください")


        if "https://" in url:
            url = url.replace("https://pay.paypay.ne.jp/", "")

        if link_info:
            if isinstance(link_info, LinkInfo):
                link_info = link_info.raw

        else:
            params = {
                "verificationCode": url,
                "payPayLang": "ja"
            }
            link_info = self.request("get", "https://app4.paypay.ne.jp/bff/v2/getP2PLinkInfo", params=params)

        payload = {
            "requestId": str(uuid4()),
            "orderId": link_info["payload"]["pendingP2PInfo"]["orderId"],
            "verificationCode": url,
            "passcode": None,
            "senderMessageId": link_info["payload"]["message"]["messageId"],
            "senderChannelUrl": link_info["payload"]["message"]["chatRoomId"]
        }

        order_status = link_info["payload"]["orderStatus"]
        if order_status == LinkStatus.PENDING:
            pass

        elif order_status == LinkStatus.SUCCESS:
            raise PayPayError("すでに受け取り済みのリンクです")

        elif order_status == LinkStatus.REJECTED:
            raise PayPayError("すでに辞退済みのリンクです")

        elif order_status == LinkStatus.FAILED:
            raise PayPayError("すでにキャンセル済みのリンクです")


        if link_info["payload"]["pendingP2PInfo"]["isSetPasscode"] and passcode == None:
            raise PayPayError("このリンクにはパスワードが設定されています")

        if link_info["payload"]["pendingP2PInfo"]["isSetPasscode"]:
            payload["passcode"] = passcode


        response = self.request("post", "https://app4.paypay.ne.jp/bff/v2/acceptP2PSendMoneyLink", json=payload, params={"payPayLang": "ja", "appContext": "P2PMoneyTransferDetailScreen_linkReceiver"})

        return response

    def link_reject(self, url: str, link_info: dict | LinkInfo = None) -> dict:
        if not self.access_token:
            raise PayPayLoginError("まずはログインしてください")

        if "https://" in url:
            url = url.replace("https://pay.paypay.ne.jp/", "")

        if link_info:
            if isinstance(link_info, LinkInfo):
                link_info = link_info.raw

        else:
            params = {
                "verificationCode": url,
                "payPayLang": "ja"
            }
            link_info = self.request("get", "https://app4.paypay.ne.jp/bff/v2/getP2PLinkInfo", params=params)

        payload = {
            "requestId": str(uuid4()),
            "orderId": link_info["payload"]["pendingP2PInfo"]["orderId"],
            "verificationCode": url,
            "senderMessageId": link_info["payload"]["message"]["messageId"],
            "senderChannelUrl": link_info["payload"]["message"]["chatRoomId"]
        }

        order_status = link_info["payload"]["orderStatus"]
        if order_status == LinkStatus.PENDING:
            pass

        elif order_status == LinkStatus.SUCCESS:
            raise PayPayError("すでに受け取り済みのリンクです")

        elif order_status == LinkStatus.REJECTED:
            raise PayPayError("すでに辞退済みのリンクです")

        elif order_status == LinkStatus.FAILED:
            raise PayPayError("すでにキャンセル済みのリンクです")

        response = self.request("post", "https://app4.paypay.ne.jp/bff/v2/rejectP2PSendMoneyLink", json=payload, params=self.params)

        return response

    def link_cancel(self, url: str, link_info: dict | LinkInfo = None) -> dict:
        if not self.access_token:
            raise PayPayLoginError("まずはログインしてください")

        if "https://" in url:
            url = url.replace("https://pay.paypay.ne.jp/", "")

        if link_info:
            if isinstance(link_info, LinkInfo):
                link_info = link_info.raw

        else:
            params = {
                "verificationCode": url,
                "payPayLang": "ja"
            }
            link_info = self.request("get", "https://app4.paypay.ne.jp/bff/v2/getP2PLinkInfo", params=params)

        payload = {
            "orderId": link_info["payload"]["pendingP2PInfo"]["orderId"],
            "requestId": str(uuid4()),
            "verificationCode": url,
        }

        order_status = link_info["payload"]["orderStatus"]
        if order_status == LinkStatus.PENDING:
            pass

        elif order_status == LinkStatus.SUCCESS:
            raise PayPayError("すでに受け取り済みのリンクです")

        elif order_status == LinkStatus.REJECTED:
            raise PayPayError("すでに辞退済みのリンクです")

        elif order_status == LinkStatus.FAILED:
            raise PayPayError("すでにキャンセル済みのリンクです")

        response = self.request("post", "https://app4.paypay.ne.jp/p2p/v1/cancelP2PSendMoneyLink", json=payload, params=self.params)

        return response

    def create_link(self, amount: int, passcode: str = None, pochibukuro: bool = False, theme: str = "default-sendmoney"):
        if not self.access_token:
            raise PayPayLoginError("まずはログインしてください")

        payload = {
            "requestId": str(uuid4()),
            "amount": amount,
            "socketConnection": "P2P",
            "theme": theme,
            "source": "sendmoney_home_sns",
            "ackPhoneCallDetected": False
        }

        if passcode:
            payload["passcode"] = passcode

        if pochibukuro:
            payload["theme"] = "pochibukuro"

        response = self.request("post", "https://app4.paypay.ne.jp/bff/v2/executeP2PSendMoneyLink", json=payload, params=self.params)

        class CreateLink(NamedTuple):
            link: str
            chat_room_id: str
            order_id: str
            raw: dict

        link = response["payload"]["link"]
        chat_room_id = response["payload"]["chatRoomId"]
        order_id = response["payload"]["orderId"]

        return CreateLink(link, chat_room_id, order_id, response)

    def send_money(self, amount: int, receiver_id: str, pochibukuro: bool = False, theme: str = "default-sendmoney"):
        if not self.access_token:
            raise PayPayLoginError("まずはログインしてください")

        payload = {
            "amount": amount,
            "theme": theme,
            "requestId": str(uuid4()),
            "externalReceiverId": receiver_id,
            "ackRiskError": False,
            "ackPhoneCallDetected": False,
            "source": "sendmoney_history_chat",
            "qrCodeId": "",
            "metricMetadata": {
                "timestamp": time.time(),
            }
        }
        if pochibukuro:
            payload["theme"] = "pochibukuro"

        response = self.request("post", f"https://app4.paypay.ne.jp/p2p/v3/executeP2PSendMoney", json=payload, params=self.params)

        if response["header"]["resultCode"] == "S4002":
            print(response["header"]["resultMessage"])
            print("waiting 5 seconds and retrying...")

            time.sleep(5)
            payload["ackRiskError"] = True
            payload["ackPhoneCallDetected"] = True

            response = self.request("post", f"https://app4.paypay.ne.jp/p2p/v3/executeP2PSendMoney", json=payload, params=self.params)

        class SendMoney(NamedTuple):
            chat_room_id: str
            order_id: str
            raw: dict

        chat_room_id = response["payload"]["chatRoomId"]
        order_id = response["payload"]["orderId"]

        return SendMoney(chat_room_id, order_id, response)

    def send_message(self, chat_room_id: str, message: str) -> dict:
        if not self.access_token:
            raise PayPayLoginError("まずはログインしてください")

        payload = {
            "channelUrl": chat_room_id,
            "message": message,
            "socketConnection": "P2P",
            "metricMetadata": {
                "timestamp": time.time()
            }
        }

        response = self.request("post", "https://app4.paypay.ne.jp/p2p/v1/sendP2PMessage", json=payload, params=self.params)

        return response

    def create_p2pcode(self, amount: int = None):
        if not self.access_token:
            raise PayPayLoginError("まずはログインしてください")

        payload = {
            "amount": None,
            "sessionId": None
        }
        if amount:
            payload["amount"] = amount
            payload["sessionId"] = str(uuid4())

        create_p2pcode = self.request("post", "https://app4.paypay.ne.jp/bff/v1/createP2PCode", json=payload, params=self.params)

        class P2PCode(NamedTuple):
            p2pcode: str
            raw: dict

        p2pcode = create_p2pcode["payload"]["p2pCode"]

        return P2PCode(p2pcode, create_p2pcode)

    def get_profile(self):
        if not self.access_token:
            raise PayPayLoginError("まずはログインしてください")

        response = self.request("get", "https://app4.paypay.ne.jp/bff/v2/getProfileDisplayInfo", params={"includeExternalProfileSync": "true", "completedOptionalTasks": "ENABLED_NEARBY_DEALS", "payPayLang": "ja"})

        class Profile(NamedTuple):
            name: str
            external_user_id: str
            icon: str
            raw: dict

        name = response["payload"]["userProfile"]["nickName"]
        external_user_id = response["payload"]["userProfile"]["externalUserId"]
        icon = response["payload"]["userProfile"]["avatarImageUrl"]

        return Profile(name, external_user_id, icon, response)

    def set_money_priority(self, paypay_money: bool = False) -> dict:
        if not self.access_token:
            raise PayPayLoginError("まずはログインしてください")

        if paypay_money:
            payload = {"moneyPriority": "MONEY_FIRST"}
        else:
            payload = {"moneyPriority": "MONEY_LITE_FIRST"}

        response = self.request("post", "https://app4.paypay.ne.jp/p2p/v1/setMoneyPriority", json=payload, params={"payPayLang": "ja"})

        return response

    def get_chat_rooms(self, size: int = 20, last_message: bool = True):
        if not self.access_token:
            raise PayPayLoginError("まずはログインしてください")

        params = {
            "pageSize": str(size),
            "customTypes": "P2P_CHAT,P2P_CHAT_INACTIVE,P2P_PUBLIC_GROUP_CHAT,P2P_LINK,P2P_OLD",
            "requiresLastMessage": last_message,
            "socketConnection": "P2P",
            "payPayLang": "ja"
        }
        response = self.request("get", "https://app4.paypay.ne.jp/p2p/v1/getP2PChatRoomListLite", params=params)

        return response

    def get_chat_room_messages(self, chat_room_id: str, prev: int = 15, next: int = 0, include: bool = False) -> dict:
        if not self.access_token:
            raise PayPayLoginError("まずはログインしてください")

        params = {
            "chatRoomId": chat_room_id,
            "include": include,
            "prev": str(prev),
            "next": str(next),
            "payPayLang": "ja"
        }
        response = self.request("get", "https://app4.paypay.ne.jp/bff/v1/getP2PMessageList", params=params)

        return response

    def get_point_history(self) -> dict:
        if not self.access_token:
            raise PayPayLoginError("まずはログインしてください")

        params = {
            "pageSize": "20",
            "orderTypes": "CASHBACK",
            "paymentMethodTypes": "",
            "signUpCompletedAt": "2021-01-02T10:16:24Z",
            "pointType": "REGULAR",
            "isOverdraftOnly": "false",
            "payPayLang": "ja"
        }
        response = self.request("get", "https://app4.paypay.ne.jp/bff/v3/getPaymentHistory", params=params)

        return response

    def search_p2puser(self, user_id: str, size: int = 10, is_global: bool = False, order: int = 0):
        if not self.access_token:
            raise PayPayLoginError("まずはログインしてください")

        payload = {
            "searchTerm": user_id,
            "pageToken": "",
            "pageSize": size,
            "isIngressSendMoney": False,
            "searchTypes": "FRIEND_AND_CANDIDATE_SEARCH"
        }

        if is_global:
            payload["searchTypes"] = "GLOBAL_SEARCH"

        response = self.request("post", "https://app4.paypay.ne.jp/p2p/v3/searchP2PUser", json=payload, params=self.params)
        if response["header"]["resultCode"] != "S0000":
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

    def initialize_chatroom(self, external_user_id: str):
        if not self.access_token:
            raise PayPayLoginError("まずはログインしてください")

        payload = {
            "returnChatRoom": True,
            "shouldCheckMessageForFriendshipAppeal": True,
            "externalUserId": external_user_id,
            "socketConnection": "P2P"
        }
        response = self.request("post", "https://app4.paypay.ne.jp/p2p/v1/initialiseOneToOneAndLinkChatRoom", json=payload, params=self.params)

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
        barcode = self.request("get", "https://app4.paypay.ne.jp/bff/v2/getBarcodeInfo", params=params)

        class BarcodeInfo(NamedTuple):
            amount: int
            user_name: str
            external_user_id: str
            user_icon: str
            raw: dict

        return BarcodeInfo(
            amount=barcode["payload"]["userCodeInfo"]["amount"],
            user_name=barcode["payload"]["userCodeInfo"]["userInfo"]["displayName"],
            external_user_id=barcode["payload"]["userCodeInfo"]["userInfo"]["externalUserId"],
            user_icon=barcode["payload"]["userCodeInfo"]["userInfo"]["avatarImageUrl"],
            raw=barcode
        )

    def cashout_to_paypaybank(self, amount: int):
        if not self.access_token:
            raise PayPayLoginError("まずはログインしてください")

        payout_display_info = self.request("get", "https://app4.paypay.ne.jp/bff/v2/getPayoutDisplayInfo", params={"payPayLang": "ja"})
        self_payout_methods = payout_display_info["payload"]["selfPayoutMethodInfoList"]
        for method in self_payout_methods:
            if method["payoutBankInfo"]["bankName"] == "PayPay銀行":
                payment_method_id = method["id"]
                break

        payload = {
            "amount": amount,
            "payoutMethodId": payment_method_id,
            "requestId": str(uuid4()),
            "agreeSimilarTransactionFlag": False,
            "senderName": "ＰＡＹＰＡＹ"
        }
        response = self.request("post", "https://app4.paypay.ne.jp/bff/v2/executePayout", json=payload, params=self.params)

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

    def pay_qr_code(self, url: str):
        if not self.access_token:
            raise PayPayLoginError("まずはログインしてください")

        if "https://qr.paypay.ne.jp/" in url:
            url = url.replace("https://qr.paypay.ne.jp/", "")

        barcode_info = self.request("get", "https://app4.paypay.ne.jp/bff/v2/getBarcodeInfo?code=" + "https://qr.paypay.ne.jp/" + url, params={"payPayLang": "ja", "isScannedFromFile": "false"})
        amount = barcode_info["payload"]["codeInfo"]["dynamicCodeInfo"]["amount"]
        payment_method_id = barcode_info["payload"]["paymentMethodInfo"]["paymentMethodIdString"]
        merchant_id = barcode_info["payload"]["codeInfo"]["dynamicCodeInfo"]["merchantInfo"]["merchantId"]
        merchant_order_id = barcode_info["payload"]["codeInfo"]["dynamicCodeInfo"]["merchantOrderId"]
        code = barcode_info["payload"]["codeInfo"]["dynamicCodeInfo"]["code"]

        payload = {
            "requestId": "97e4b15d-2e8a-499d-8d21-78d8953cdced",
            "merchantId": merchant_id,
            "storeId": "",
            "stickerId": "",
            "amount": amount,
            "currency": "JPY",
            "paymentMethodId": payment_method_id,
            "paymentMethodType": "WALLET",
            "agreeSimilarTransactionFlag": False,
            "code": code,
            "merchantOrderId": merchant_order_id,
            "mode": "DYNAMIC_QR"
        }

        payment_result = self.request("post", "https://app4.paypay.ne.jp/bff/v2/executePayment", json=payload, params={"payPayLang": "ja"})

        class PayQRCodeResult(NamedTuple):
            order_id: str
            order_status: str
            amount: int
            merchant_name: str
            raw: dict

        order_id = payment_result["payload"]["paymentInfo"]["orderInfo"]["orderId"]
        order_status = payment_result["payload"]["paymentInfo"]["orderInfo"]["statusInfo"]["orderStatus"]
        amount = payment_result["payload"]["paymentInfo"]["participantDetails"]["amountDetail"]["amount"]["value"]
        merchant_name = payment_result["payload"]["paymentInfo"]["participantDetails"]["title"]

        return PayQRCodeResult(
            order_id=order_id,
            order_status=order_status,
            amount=amount,
            merchant_name=merchant_name,
            raw=payment_result
        )

    def alive(self) -> bool:
        if not self.access_token:
            raise PayPayLoginError("まずはログインしてください")

        params = {
            "payPayLang": "ja"
        }

        self.request("get", "https://app4.paypay.ne.jp/bff/v1/getGlobalServiceStatus", params=params)

        payload = {
            "abTestFlags": {
                "dedupeFeatureAndFavoritesTab": False
            },
            "excludeMissionBannerInfoFlag": False,
            "excludeTobaccoPolicyBannerFlag": True,
            "includeBeginnerFlag": False,
            "includeSkinInfoFlag": False,
            "networkStatus": "WIFI"
        }

        self.request("post", "https://app4.paypay.ne.jp/bff/v4/getHomeDisplayInfo", params=params, json=payload)

        payload = {
            "flagNames": [
                "enable_home_screen_favoriting_suggestions",
                "home_screen_all_entry_point_ab_test",
                "enable_cache_encryption_engine",
                "credit-card-maintenance-in-progress",
                "vpc_home_merchant_list",
                "aws_iot_core_migration_enabled",
                "enable_insufficient_balance_topup_android",
                "is_post_payment_route_migration_enabled",
                "enable_transaction_history_migration_android",
                "enable_nc_redesign",
                "nearby_halfsheet_combined_ab_test",
                "home-screen/p2p_tab_bar_item",
                "cashback_sound_multiplier",
                "p2p_chat_room_gift_voucher_nudge"
            ]
        }

        self.request("post", "https://app4.paypay.ne.jp/bff/v1/getFeatureFlagInfo", params=params, json=payload)

        return True