# PayPaython-mobile ![icon](https://raw.githubusercontent.com/taka-4602/PayPaython/main/images/1.png)
Python用のPayPayモバイルAPIラッパー
### >> ```pip install paypaython-mobile``` <<
## [ ! ] PayPayからのレスポンス集 -> *[PayPayResponce.md](https://github.com/taka-4602/PayPaython/blob/main/PAYPAYRESPONCE.md)*
PayPay APIを使った時に返されるレスポンスをまとめたドキュメントです  
返ってきたレスポンスにどんな意味があるか知りたい場合、このドキュメントが役に立つかもしれません   
## 始める前に確認すること
### ログインを3回失敗するとアカウントが一時ロックされる
PayPayのサポートに連絡することで早く解除してもらえるみたいです (めんどくさいけど)
### セッションを作りすぎない
セッションを大量に作るとアカウント凍結の可能性があるみたいです (モバイルAPIで起こるか不明だし、WebAPIでも僕は未確認)
### 日本からしかアクセスできない
ふつうにブロックされます  
海外のバーチャルマシンとかを使う場合はプロキシを使いましょう
## Let'Go! ([前と同じ](https://github.com/taka-4602/PayPaython?tab=readme-ov-file#lets-go)ノリ)
#### example.py  
```py
from PayPaython_mobile import PayPay

paypay=PayPay("080-1234-5678","Unko-1234")#電話番号とパスワードでログインスタート、ハイフンはありでもなしでも。
url=input("URL?: ")#URLと書いてあるけどIDだけでもOK
paypay.login(url)#URLなら https://www.paypay.ne.jp/portal/oauth2/l?id=TK4602 をそのままいれる、IDをいれるなら id=の横、TK4602
print(paypay.access_token)#アクセストークンは2ヶ月と28日有効
print(paypay.refresh_token)
print(paypay.device_uuid)#デバイスUUIDで登録デバイスを管理してるぽい
print(paypay.client_uuid)#クライアントUUIDは特に必要ない
#これでログイン完了、次回からはアクセストークンかデバイスUUIDを入力してログインできる
#アクセストークンならログイン作業自体をスキップできるからおすすめ

paypay.resend_url()#認証用URLを再送信、いらないと思うけどいちおう...

paypay=PayPay("080-1234-5678","Unko-1234","登録済みのデバイスUUID",proxy=None)
print(paypay.access_token)
print(paypay.refresh_token)
#URLを入力する必要はない

paypay=PayPay(access_token="アクセストークン")
#ログインをスキップ

paypay.token_refresh("ここにリフレッシュトークン")#アクセストークンは90日経つと失効するので失効したらリフレッシュしよう
print(paypay.access_token)
print(paypay.refresh_token)
#↑ここ2つはリフレッシュ後のものを返すようになる

paypay.get_profile()#引数なし、プロフィールを取得する
print(paypay.name)#ユーザー名
print(paypay.external_user_id)#識別のためのユーザーID、自分で決められるやつとは違う
print(paypay.icon)#アイコンのURL

paypay.get_balance()#これも引数なし、PayPay残高を取得する
print(paypay.all_balance)#すべての残高
print(paypay.useable_balance)#すべての使用可能な残高
print(paypay.money_light)#もってるマネーライト
print(paypay.money)#もってるマネー
print(paypay.points)#もってるポイント

print(paypay.get_history(size=20))#支出入の履歴を取得する、size=どれだけ履歴を取得するか、デフォルトは20だったけど少なくもできる
print(paypay.get_chat_rooms(size=20))#PayPayのDMリストを取得する
print(paypay.get_chat_room_messages(chat_room_id="sendbird_group_channel_なんとか_なんとか"))#グループIDのDMを取得する sendbird_group_channel_ はなくてもOK
print(paypay.get_point_history())#ポイントの履歴を取得する

paypay.link_check("KT975hvzbH1EulTr")#web=True でWebAPIを使ってリンクを確認できる (ログインがいらない、もし使う場合はPayPay(access_token="なし"))とでもしておく
link_info=paypay.link_check("https://pay.paypay.ne.jp/KT975hvzbH1EulTr")#URLそのままでもOK
print(paypay.link_amount)#リンクの合計金額
print(paypay.link_money_light)#金額のマネーライト分
print(paypay.link_money)#金額のマネー分
print(paypay.link_has_password)#パスワードがあるなら True
print(paypay.link_chat_room_id)#チャットルームID リンク受け取ったらメッセージ送れるあれのID
print(paypay.link_status)#PENDING COMPLEATED REJECTED CANCELED 
print(paypay.link_order_id)
#paypay.link_nantoka で返されるのはリンクチェックしたものだけ

paypay.link_receive("ここもURL / IDどっちでもOK","必要ならパスワード 4602",link_info=link_info)#リンク受け取り、link_infoにリンクのdictをぶちこむとリンクチェックをスキップする
paypay.link_reject("ここもURL / IDどっちでもOK",link_info=link_info)#リンクを辞退する、link_infoがないならチェックリンクするのでどっちでもいい
paypay.link_cancel("ここもURL / IDどっちでもOK",link_info=link_info)#PayPayやっとリンクキャンセルできるようになった

paypay.create_link(amount=100,password="4602")#送金リンク作成、金額と必要ならパスワード
print(paypay.created_link)#↑で作ったURL
print(paypay.created_chat_room_id)#↑で作ったリンクのチャットルームID

paypay.create_p2pcode()#引数なし、自分に送金してもらうためのQRコードのリンク
print(paypay.created_p2pcode)#↑で作ったURL

print(paypay.create_paymentcode())#レジでスキャンする用のバーコードを生成、画像はアプリ内で処理されるからコードだけ生成してもよっぽど機材を持ってる人じゃない限り無意味、死に機能

paypay.send_money(amount=100,receiver_id="受取人のexternal_id")
paypay.send_message(chat_room_id="DMのID",message="100円くれてありがとう!")#link_checkで取得したchat_room_idをそのまま入れてOK、PayPayのDMを自動化できる、商用してる人なら "お買い上げありがとうございます。" 的な

paypay.set_money_priority(paypay_money=False)#PayPayで送る残高の優先度を変更する、Falseでマネーライト有線、Trueでマネー優先に設定

paypay.search_p2puser(user_id="ユーザーID")#ユーザーが決められるPayPayIDでユーザー検索ができる、グローバルサーチはすぐにレート制限に入る
print(paypay.found_user_name)#見つかったユーザーの表示名
print(paypay.found_user_icon)#見つかったユーザーのアイコン
print(paypay.found_user_external_id)#見つかったユーザーのExternalID

paypay.search_p2puser(user_id="表示名",is_global=False,order=0)#is_grobalをFalseにしてフレンドなら表示名でExternalIDを取得できる、orderはユーザー名が被った時何番目のユーザーの情報を取得するか、リストだから1番上は0
print(paypay.found_user_icon)#見つかったユーザーのアイコン
print(paypay.found_user_external_id)#見つかったユーザーのExternalID

paypay.initialize_chatroom("ExternalID")#ExternalIDを使ってDM送信用のチャットルームIDを取得できる
print(paypay.found_chatroom_id)#見つかったユーザーのチャットルームID
```
WebAPIに比べてすごく長い、でも機能はたくさん  
#コメントで使い方は書いてるしそれが全部  
### dictを見る必要がなくなった  
1部 (get_histoyなどリストで返ってくるものとか) 以外、よく使うものは変数にまとめたのでdict探し地獄はマシになったと思います  
それでもすべてのメソッドはdictを返すようになっているので返り値全文を見たい場合はメソッドの返り値を```print()```してください  
dictをキーで取り出すのはコードの見た目も悪くなりがちだから変数で返ってくるのはうれしいカモ  
## もう少し知る
### ログインについて
WebAPIも電話番号、パスワード、UUID(Client_UUID)、アクセストークンが1セットでしたがモバイルAPIも根本は同じで電話番号、パスワード、Device_UUID、Client_UUID、アクセストークン、リフレッシュトークンが1セットです  
ログインもアクセストークンをヘッダーにつけることでスキップすることができます  
電話番号、パスワード、登録済みDevice_UUIDを使うとワンタイムURLなしでログインできます  
```py
paypay=PayPay("080-1234-5678","Unko-1234","登録済みのデバイスUUID",proxy=None)
print(paypay.access_token)
print(paypay.refresh_token)
#URLを入力する必要はない
```
###### 電話番号のハイフンはあってもなくてもOK
どうやらクライアントUUIDは常にテキトーでいいみたいです  
アクセストークンがヘッダーについてる場合、デバイスUUIDもテキトーでいいみたいです  
```py
paypay=PayPay(access_token="アクセストークン")
#ログインをスキップ
```
アクセストークンは90日間有効みたいで、WebAPIの1080倍長持ち！  
そういえばいつのまにか4桁のOTPは廃止になった  
### ログインのリフレッシュ
上記にあるように電話番号、パスワード、デバイスUUIDでログインすることでワンタイムURLなしにログインをリフレッシュできるけど、```token_refresh```を使う方がスマート  
```py
paypay.token_refresh("ここにリフレッシュトークン")#アクセストークンは90日で失効するので失効したらリフレッシュしよう
print(paypay.access_token)
print(paypay.refresh_token)
#↑ここ2つはリフレッシュ後のものを返すようになる
```
ログインをなにかデータベースに書き込む際はどっちも保存しておいたほうがベター
### PayPayのDM
なぜか自分に送れるし成功って言われる (反映はされない)  
リンクチェックをした時にDM送る用のチャットルームIDが返ってくる  
商用してる人は買われたものの詳細を送ったり、単に "ありがとうございました" だけでも需要はありそう  
IDは```sendbird_group_channel_なんとか_なんとか```の形式だけど```send_message```を使う時の引数にする場合```sendbird_group_channel_```の部分はなくてもOK  
#### もう少し効率化
グループチャンネルIDがリンクチェック時しかわからないのはめんどくさい、検索を組み合わせて使えば効率化できます  
##### PayPayのユーザーIDで検索する場合
```py
paypay.search_p2puser("taka4602")#ここで検索
paypay.initialize_chatroom(paypay.found_user_external_id)#チャットルームIDを取得
paypay.send_message(paypay.found_chatroom_id,"テスト")#取得したチャットルームIDにメッセージを送信
```
##### PayPayの表示名で検索する場合
```py
paypay.search_p2puser("たか",is_global=False)#ここで検索、フレンドを検索する場合は is_global=False 表示名検索はフレンドしか探せない (というかフレンド検索にPayPayIDは使えない)
paypay.initialize_chatroom(paypay.found_user_external_id)#チャットルームIDを取得
paypay.send_message(paypay.found_chatroom_id,"テスト")#取得したチャットルームIDにメッセージを送信
```
しかしユーザーID検索はすぐにレート制限にかかるので、DM送るのはけっきょくリンク受け取り時だったり...これはオプションに過ぎない...  
表示名でフレンド検索する場合は上記に該当せず、逆にフレンド検索にPayPayIDが使えない (NotFoundが返される)  
#### もちろんDMではなく直接送金もできる
```py
paypay.search_p2puser("たか")
paypay.send_money(100,paypay.found_user_external_id)
```
DM送信の時と違ってExternalIDだけで送金できるからこっちの方が簡単
### PayPayエラー
受け取りや辞退の時に既に処理済みのリンクを投げるとエラーになるようにしています  
無効なリンクを処理しようとしてもエラーになります  
また ログイン作業の失敗や S0001 : アクセストークンが取り消されました が返ってきた場合、PayPayLoginError (インポートできます) がraiseされます    
判別用に使ってください
### 余談
WebAPIの時は詐欺に使われたりだったけど4桁OTPが廃止された今のモバイルAPIならもう引っかかる人はいないはず  
ユーザーエージェントはiPhone8 (iOS 16.7.5) トラフィック確認に使った端末がiPhone8だから  
実機はiOS 14.8だけどユーザーエージェントでは16.7.5に変えている (というかPayPayは最近iOS 14のサポートを終了したみたい...)
## コンタクト  
Discord サーバー / https://discord.gg/aSyaAK7Ktm  
Discord ユーザー名 / .taka.  
