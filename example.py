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