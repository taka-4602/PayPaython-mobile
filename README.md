# PayPaython-mobile ![icon](https://raw.githubusercontent.com/taka-4602/PayPaython/main/images/1.png)
Python用のPayPayモバイルAPIラッパー
## インストール
```py
pip install paypaython-mobile
```
必須：requests, pkce
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
## Let's Go! ([前と同じ](https://github.com/taka-4602/PayPaython?tab=readme-ov-file#lets-go)ノリ)
#### example.py  
```py
from PayPaython_mobile import PayPay

paypay=PayPay("080-1234-5678","Unko-1234")#電話番号とパスワードでログインスタート、ハイフンはありでもなしでも。
url=input("URL?: ")#URLと書いてあるけどIDだけでもOK
paypay.login(url)#URLなら https://www.paypay.ne.jp/portal/oauth2/l?id=TK4602 をそのままいれる、IDをいれるなら id=の横、TK4602
print(paypay.access_token)#アクセストークンは90日有効
print(paypay.refresh_token)
print(paypay.device_uuid)#デバイスUUIDで登録デバイスを管理してるぽい
print(paypay.client_uuid)#クライアントUUIDは特に必要ない
#これでログイン完了、次回からはアクセストークンかデバイスUUIDを入力してログインできる
#アクセストークンならログイン作業自体をスキップできる

paypay=PayPay("080-1234-5678","Unko-1234","登録済みのデバイスUUID",proxy=None)#プロキシはdictでもstrでもOK、str="http://host:port" http://が無くてもOK
print(paypay.access_token)
print(paypay.refresh_token)
#URLを入力する必要はない

paypay=PayPay(access_token="アクセストークン")
#ログインをスキップ

paypay.token_refresh("ここにリフレッシュトークン")#アクセストークンは90日経つと失効するので失効したらリフレッシュしよう
print(paypay.access_token)
print(paypay.refresh_token)
#↑ここ2つはリフレッシュ後のものを返すようになる

get_profile=paypay.get_profile()#引数なし、プロフィールを取得する
print(get_profile.name)#ユーザー名
print(get_profile.external_user_id)#識別のためのユーザーID、自分で決められるやつとは違う
print(get_profile.icon)#アイコンのURL

get_balance=paypay.get_balance()#これも引数なし、PayPay残高を取得する
print(get_balance.all_balance)#すべての残高
print(get_balance.useable_balance)#すべての使用可能な残高
print(get_balance.money_light)#もってるマネーライト
print(get_balance.money)#もってるマネー
print(get_balance.points)#もってるポイント

print(paypay.get_history(size=20))#支出入の履歴を取得する、size=どれだけ履歴を取得するか、デフォルトは20だったけど少なくもできる
print(paypay.get_chat_rooms(size=20))#PayPayのDMリストを取得する
print(paypay.get_chat_room_messages(chat_room_id="sendbird_group_channel_なんとか_なんとか"))#グループIDのDMを取得する sendbird_group_channel_ はなくてもOK
print(paypay.get_point_history())#ポイントの履歴を取得する

paypay.link_check("KT975hvzbH1EulTr")#web=True でWebAPIを使ってリンクを確認できる
link_info=paypay.link_check("https://pay.paypay.ne.jp/KT975hvzbH1EulTr")#URLそのままでもOK
print(link_info.amount)#リンクの合計金額
print(link_info.money_light)#金額のマネーライト分
print(link_info.money)#金額のマネー分
print(link_info.has_password)#パスワードがあるなら True
print(link_info.chat_room_id)#チャットルームID リンク受け取ったらメッセージ送れるあれのID
print(link_info.status)#PENDING COMPLEATED REJECTED FAILED
print(link_info.order_id)

paypay.link_receive("ここもURL / IDどっちでもOK","必要ならパスワード 4602",link_info=link_info)#リンク受け取り、link_infoにリンクのdictをぶちこむとリンクチェックをスキップする
paypay.link_reject("ここもURL / IDどっちでもOK",link_info=link_info)#リンクを辞退する、link_infoがないならチェックリンクするのでどっちでもいい
paypay.link_cancel("ここもURL / IDどっちでもOK",link_info=link_info)#PayPayやっとリンクキャンセルできるようになった

create_link=paypay.create_link(amount=100,passcode="4602")#送金リンク作成、金額と必要ならパスワード
print(create_link.link)#↑で作ったURL
print(create_link.chat_room_id)#↑で作ったリンクのチャットルームID

create_p2pcode=paypay.create_p2pcode()#自分に送金してもらうためのQRコードのリンク、amount=intでQRコードの値段を設定
print(create_p2pcode.p2pcode)#↑で作ったURL

send_money=paypay.send_money(amount=100,receiver_id="受取人のexternal_id")
print(send_money.chat_room_id)#send_moneyにもチャットルームIDを追加
paypay.send_message(chat_room_id="DMのID",message="100円くれてありがとう!")#取得したchat_room_idをそのまま入れたり、PayPayのDMを自動化できる、商用してる人なら "お買い上げありがとうございます。" 的な

paypay.set_money_priority(paypay_money=False)#PayPayで送る残高の優先度を変更する、Falseでマネーライト優先、Trueでマネー優先に設定

search_p2puser=paypay.search_p2puser(user_id="ユーザーID")#ユーザーが決められるPayPayIDでユーザー検索ができる、グローバルサーチはすぐにレート制限に入る
print(search_p2puser.name)#見つかったユーザーの表示名
print(search_p2puser.icon)#見つかったユーザーのアイコン
print(search_p2puser.external_id)#見つかったユーザーのExternalID

search_p2puser=paypay.search_p2puser(user_id="表示名",is_global=False,order=0)#is_grobalをFalseにしてフレンドなら表示名でExternalIDを取得できる、orderはユーザー名が被った時何番目のユーザーの情報を取得するか、リストだから1番上は0
print(search_p2puser.icon)#見つかったユーザーのアイコン
print(search_p2puser.external_id)#見つかったユーザーのExternalID

initialize_chatroom=paypay.initialize_chatroom("ExternalID")#ExternalIDを使ってDM送信用のチャットルームIDを取得できる
print(initialize_chatroom.chatroom_id)#見つかったユーザーのチャットルームID
```
WebAPIに比べてすごく長い、でも機能はたくさん  
#コメントで使い方は書いてるしそれが全部  
### dictを見る必要がなくなった  
1部 (get_histoyなどリストで返ってくるものとか) 以外、よく使うものは変数にまとめたのでdict探し地獄はマシになったと思います  
それでもすべてのメソッドはdictを返すようになっているので返り値全文を見たい場合は```paypay.なんとか().raw```で見ることができます  
```.raw```がない場合はそもそもそのメソッドの返り値がそのままdictということです  
## もう少し知る
### ログインについて
  WebAPIは電話番号、パスワード、UUID(Client_UUID)、アクセストークンが1セットでしたがモバイルAPIも根本は同じで電話番号、パスワード、Device_UUID、Client_UUID、アクセストークン、リフレッシュトークンが1セットです  
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
###### アクセストークンは90日間有効みたいで、WebAPIの1080倍長持ち！  
###### そういえばいつのまにか4桁のOTPは廃止になった  
### ログインのリフレッシュ
上記にあるように電話番号、パスワード、デバイスUUIDでログインすることでワンタイムURLなしにログインをリフレッシュできるけど、```token_refresh```を使う方がスマート  
```py
paypay.token_refresh("ここにリフレッシュトークン")#アクセストークンは90日で失効するので失効したらリフレッシュしよう
print(paypay.access_token)
print(paypay.refresh_token)
#↑ここ2つはリフレッシュ後のものを返すようになる
```
ログインをファイルとかに保存する場合はどっちも保存しておいたほうがベター
### PayPayのDM
なぜか自分に送れるし成功って言われる (送金 / 受け取り履歴のところにメッセージが送られる)  
リンクチェックをした時にDM送る用のチャットルームIDが返ってくる  
商用してる人は買われたものの詳細を送ったり、単に "ありがとうございました" だけでも需要はありそう  
IDは```sendbird_group_channel_なんとか_なんとか```の形式だけど```send_message```を使う時の引数にする場合```sendbird_group_channel_```の部分はなくてもOK  
#### もう少し効率化
グループチャンネルIDがリンクチェック時しかわからないのはめんどくさい、検索を組み合わせて使えば効率化できます  
##### PayPayのユーザーIDで検索する場合
```py
search_p2puser=paypay.search_p2puser(user_id="ユーザーID")#ユーザーが決められるPayPayIDでユーザー検索ができる、グローバルサーチはすぐにレート制限に入る
paypay.send_message(search_p2puser.user_external_id,"はろー")
```
##### PayPayの表示名で検索する場合
```py
search_p2puser=paypay.search_p2puser(user_id="表示名",is_global=False,order=0)
initialize_chatroom=paypay.initialize_chatroom(search_p2puser.external_id)
paypay.send_message(initialize_chatroom.chatroom_id,"はろー")
```
ユーザーID検索はすぐにレート制限にかかるので、DM送るのはけっきょくリンク受け取り時しかない...  
表示名でフレンド検索する場合は上記に該当せず、逆にフレンド検索にはPayPayIDが使えない (NotFoundが返される)  
#### もちろんDMではなく直接送金もできる
```py
search_p2puser=paypay.search_p2puser("たか",is_global=False)
send_money=paypay.send_money(100,search_p2puser.external_id)
```
DM送信の時と違ってExternalIDだけで送金できるからこっちの方が簡単
### PayPayエラー
受け取りや辞退の時に既に処理済みのリンクを投げるとエラーになるようにしています  
無効なリンクを処理しようとしてもエラーになります  
また ログイン作業の失敗や S0001 : アクセストークンが取り消されました が返ってきた場合、PayPayLoginError (インポートできます) がraiseされます    
判別用に使ってください  
### 備考
どうやらPayPayのモバイルAPIはBot検知が存在するらしい (検知されるとBotがログアウトされる)  
いろいろ試した結果、無駄なリクエストを送信することで回避できました (ユーザーがアプリケーションを操作してたら当然大量のリクエストをしてるから、それをBotで真似る)  
このモジュールにも無駄リクエスト機能を追加しました  
```py
paypay.alive() #引数も返り値もなし
```
Botは効率が良すぎる...
### 古いバージョン
古いバージョンはPayPayアプリのバージョンをiOSStoreから取得してユーザーエージェントを変えていましたが、どうやらPayPayの仕様変更のせいでPayPayアプリが新しいのに古いリクエストを使ってるのがバレるとBotがログアウトされるみたいです  
1.xのままその問題を解決したいなら```pip install paypaython-mobile==0.14.8```を使ってください (ユーザーエージェントが固定される)  
最新バージョンをユーザーエージェントにしてもなにもいいことがないので、新しくしたPayPaython-mobileは固定にしました  
古いバージョンのドキュメントはここから -> [README_old.md](https://github.com/taka-4602/PayPaython-mobile/blob/main/README_old.md)
### 余談
久しぶりに中身を大幅に更新しました、でもユーザー目線だと違いがわかりにくい **だけど1.xと2.xには互換性がない**  
バージョンが1.xを飛んで2になって、本当に無駄だった機能を消して、リクエストの内容がだいぶかわった  
~~ヘッダーがキモくなった原因の1つのセントリートレースはログの監視用だから無くても動くけど、PayPayのことだから凍結されないか心配なのでつけておいたほうが良いはず~~ -> 突然消えた  
端末の向き(xyz？)はなんで収集するようになったか全然分からない…  
###### ~~ユーザーエージェントはiPhone8 (iOS 16.7.5) トラフィック確認に使った端末がiPhone8だから~~  
###### ~~実機はiOS 14.8だけどユーザーエージェントは16.7.5に変えている (というかPayPayは最近iOS 14のサポートを終了したみたい...)~~  
ユーザーエージェントがiPhone8からKDDI版Samsung S9 (SCV38)に変更されました (iOS 14.8のPayPayアップデートはとっくに切られた)  
iOS 14.8はAndroid 10より2年も新しいのにPayPayに限らずほとんどのアプリが切られてしまった... iOSは寿命が短くて困る... (S9はOneUI 2.1 / Android 10)
## コンタクト  
Discord サーバー / https://discord.gg/g4UE3kQbmS  
Discord ユーザー名 / .taka.  
