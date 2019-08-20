# README

フォロワーを管理したりデータ見たりするやつ

# なんかできること
- APIを利用したデータの取得
- jsonからpandas.DataFrameへの変換
- Flaskによるフォロワー管理App

# いるやつ

- pyhton 3.x
- Twitter API key
- Twitter Consumer Key

python 3.x環境に各パッケージをインストール
```
pip install -r requirements.txt
```
[Twitter Developer](https://developer.twitter.com/)よりTwitter API Key、Consumer Keyを取得  
アクセストークン情報と自身のTwitterIDを環境変数に
```
export ACCESS_TOKEN=100000-piyopiyo
export ACCESS_TOKEN_SECRET=hogehoge
export CONSUMER_KEY=fugafuga
export CONSUMER_SECRET=hogerahogera
export TWITTER_ACCOUNT=vaaaaanquish
```

# うごかす
data_managerでAPIを利用しjsonを手元に落として、pandas化  
ゼロから10000アカウントでAPI規制で止まり止まり動作して半日くらい
```
python data_manager.py --follower_update --list_update --list_user_update --df_update --user_json_update=1
```

Excel等の他のアプリで読みたい場合はCSVファイルを出力
```
python data_manager.py --output_csv
```

Flask Appを立ててフォロワー管理
```
python app.py
```

リモートマシンやDockerコンテナ内で動かす時には、ホストIPアドレスを `0.0.0.0` にしておけばアクセスできる
（デフォルトの`127.0.0.1`だと外部のクライアントからアクセスできない）
```
python app.py --host 0.0.0.0 
```

# data manager args
|args|description|
|---|---|
|--follower_update|フォロー,フォロワー情報をアップデート|
|--user_json_update|0: userデータのアップデートはしない(default)|
|　|1: userデータをゼロベースで取得|
|　|2: 未取得の差分userのみ取得|
|--df_update|全userデータをロードし直してdf作り直す|
|--list_update|自分が作っているリスト情報を更新|
|--list_user_update|各リスト内のユーザ情報を更新|

　  
新しいフォロワーだけ更新したい時はこんな感じ
```
python data_manager.py --follower_update --list_user_update --df_update --user_json_update=2
```

# form
|label|default|description|
|---|---|---|
|query|followed|pandas.query|
|from|yy-mm-dd|from:アカウント作成日|
|to|yy-mm-dd|to:アカウント作成日|
|fromtw|yy-mm-dd|from:最新ツイートの日|
|totw|yy-mm-dd|to:最新ツイート日|
|sort|follower_number|ソートに利用するColumn名|
|ascend|True|ソート逆順か|
|sample|100|表示数|
|submit|　|form条件でtable表示|
|gen url|　|form情報をURLパラメータとして表示|
|reset|　|formリセット|

# default column

|column|discription|type|sample|
|----|----|----|----|
|contributors_enabled|tweet_deckで共有アカウント設定してるかどうか|bool|False|
|created_at|アカウント作成日|datetime|Fri Jun 07 03:09:31 +0000 2013|
|default_profile|デフォルトのプロフィールのままか|bool|True|
|default_profile_image|デフォルトの画像のままか|bool|False|
|description|bioに書いてある説明文|str|冷やし中華始めました|
|description_expanded_url_0|description内のURL展開結果|str|http~|
|description_expanded_url_1|description内のURL展開結果|str|http~|
|description_expanded_url_2|description内のURL展開結果|str|http~|
|description_expanded_url_3|description内のURL展開結果|str|http~|
|description_expanded_url_num|description内のURL数|int|3|
|expanded_url_0|bio内のURL展開結果|str|http~|
|expanded_url_num|bio内のURL数|int|1|
|favourites_count|お気に入りの数|int|28878|
|follow_request_sent|フォローのリクエストを投げているか|bool|False|
|followers_count|フォロワー数|int|683|
|following|フォローしているか|bool|True|
|followed|フォローされているか|bool|True|
|friends_count|フォロー数|int|703|
|get_date|データの取得日(API叩いた時間)|datetime|Mon Feb 03 04:34:50 +0000 2019|
|id_str|ユニークID|str|231~|
|lang|言語設定|str|ja|
|listed_count|オープンなリストに入ってる数|int|14|
|location|位置情報|str|日本 東京|
|name|twitterアカウントの名前|str|ばんくし|
|profile_banner_url|ヘッダーの画像|str|https://pbs.twimg.com~|
|profile_image_url|プロフィールの画像|str|http://pbs.twimg.com~|
|protected|鍵垢かどうかのbool|bool|False|
|screen_name|twitterアカウントのSN|str|vaaaaanquish|
|statuses_count|ツイートの数|int|53045|
|time_zone|タイムゾーン|str|None or tokyo|
|toptweet_created_at|topのツイートの投稿日|datetime|Mon Feb 03 04:34:50 +0000 2014|
|toptweet_id|topのツイートのID|str|123~|
|toptweet_lang|topのツイートの言語|str|ja|
|toptweet_retweet_flag|topのツイートがリツイートかどうかのフラグ|bool|False|
|toptweet_source|topのツイートの投稿アプリ|str|TweetDeck|
|toptweet_text|topのツイートのテキスト|str|冷やし中華がうまい|
|url|bioに書いてあるURL|str|http~|
|verified|認証アカウントかのbool|bool|False|
|description_length|bioの長さ|int|30|
|diff_created_at|アカウント作成日から取得日までの日数|int|2000|
|diff_toptweet_created_at|最新ツイートから取得日までの日数|int|2000|
|sn_length|SNの長さ|int|12|
|joined_list|入っているリスト|list|[hoge, piyo]|
|follower_number|フォロワーになった順にならべた時のid|int|20|
|followee_number|フォローした順にならべた時のid|int|20|

　  
Columnを追加する場合は `data_manager._add_data` 辺りをよしなに編集
```
python data_manager.py --df_update
```

# file tree
 - app.py: flaskでフォロワー管理アプリ建てるやつ
 - data_manager.py: フォロワー情報のダウンロード、書き込み、読み込み
 - utils.py: flaskに渡すテーブルとか作ったりするやつ
 - static
     - followee.jpg: フォローされてたら出るやつ
     - key.jpg: 鍵垢だったら出るやつ
     - verified.jpg: 認証アカウントだったら出るやつ
     - get.js: なんかget周りをAjaxしてくれる色々
     - post.js: 同上
     - style.css: 全体的ないろいろ
     - fbutton.css: なんかフォローボタンのやつ
 - templetes
     - layout.html: ベースのやつ
     - index.html: Formとかtable読み込んだりとか
     - table.html: フォロワーテーブルのとこ
 - ipynb: ちょっと分析してみるだけのjupyter notebook
 - README.md: お前が読んでるこれ
 - requirements.txt: pip
 
 
# 将来的になんかできたらいいかも
 - バックエンドにSQLかもうちょっと簡易な何か
 - JSライブラリ何か使う
 - 統計情報も見れるようにする

# ヒント
[@vaaaaanquish](https://vaaaaanquish.jp/)に聞いたら多分わかる
