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

paypay.create_p2pcode()#自分に送金してもらうためのQRコードのリンク、amount=intでQRコードの値段を設定
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