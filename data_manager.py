# -*- coding:utf-8 -*-
import os
import tweepy
import json
from datetime import datetime
from tqdm import tqdm
from pathlib import Path
import pandas as pd
from collections import defaultdict
import pickle
import sys
import argparse

must_key = [
    'id_str', 'following', 'follow_request_sent', 'name', 'screen_name', 'location', 'time_zone', 'description', 'url', 'protected', 'created_at',
    'followers_count', 'friends_count', 'listed_count', 'favourites_count', 'statuses_count', 'verified', 'lang', 'contributors_enabled', 'profile_image_url',
    'profile_banner_url', 'default_profile_image', 'default_profile'
]
must_json_key = ['entities', 'status']


class DataManager():
    def __init__(self, my_id, config, follower_update=False, user_json_update=False, df_update=False, list_update=False, list_user_update=False):
        """
        follower_update: フォロー情報をアップデート
        user_json_update:
            - 0: jsonデータのアップデートはしない
            - 1: ユーザ情報をゼロからアップデート
            - 2: json未取得の差分のみアップデート
        df_update: jsonファイルをロードし直してdf作り直すか
        list_update: 自分が作っているリストを更新するか
        list_user_update: リストに入っているユーザを更新するか
        """
        # make dir
        self.data_path = './data'
        if not os.path.exists('./data'):
            os.mkdir('./data')
        self.tsv_path = 'tsv_files'
        if not os.path.exists(os.path.join(self.data_path, self.tsv_path)):
            os.mkdir(os.path.join('./data', self.tsv_path))
        self.json_path = 'json_files'
        if not os.path.exists(os.path.join(self.data_path, self.json_path)):
            os.mkdir(os.path.join('./data', self.json_path))
        self.my_id = my_id
        # tweepy API
        auth = tweepy.OAuthHandler(config['CONSUMER_KEY'], config['CONSUMER_SECRET'])
        auth.set_access_token(config['ACCESS_TOKEN'], config['ACCESS_TOKEN_SECRET'])
        self.api = tweepy.API(auth, wait_on_rate_limit=True)
        # follower, followee
        self.follower_update = follower_update
        self.follower, self.follower_num = [], {}
        self.followee, self.followee_num = [], {}
        self._get_follower()
        self._get_followee()
        # json getter
        self.user_json_update = user_json_update
        self._download_user_info(list(set(self.follower) | set(self.followee)))
        # user list
        self.list_update = list_update
        self.list_user_update = list_user_update
        self.user_list = []
        self.list_dic = defaultdict(list)
        self._get_list()
        for x in self.user_list:
            self._get_list_users(x)
        # all json convert pandas
        self.df_update = df_update
        self.data_df = self._convert_pandas()
        self.user_list_dic = self._user_list()

    def _update_file(self, l, flag):
        for x in l:
            if os.path.exists(os.path.join(self.data_path, self.json_path, f'{x}.json')):
                with open(os.path.join(self.data_path, self.json_path, f'{x}.json'), 'r') as f:
                    j = json.load(f)
                j['followering'] = flag
                with open(os.path.join(self.data_path, self.json_path, f'{x}.json'), 'w') as f:
                    json.dump(j, f)

    def _get_follower(self):
        '''フォロワーのID取得'''
        if self.follower_update:
            print('_get_follower')
            tmp = list()
            if os.path.exists(os.path.join(self.data_path, self.tsv_path, 'follower.tsv')):
                with open(os.path.join(self.data_path, self.tsv_path, 'follower.tsv'), 'r') as f:
                    tmp = set([x.strip() for x in f if x != ''])
            followers_ids = tweepy.Cursor(self.api.followers_ids, id=self.my_id, cursor=-1).items()
            for i, followers_id in enumerate(followers_ids):
                self.follower.append(followers_id)
                self.follower_num.update({followers_id: i})
            # diff
            newfd = set(self.follower) - set(tmp)
            self._update_file(list(newfd), True)
            removed = set(tmp) - set(self.follower)
            self._update_file(list(removed), False)
            # save
            with open(os.path.join(self.data_path, self.tsv_path, 'follower.tsv'), 'w') as f:
                for x in self.follower:
                    f.write(f'{x}\n')
            with open(os.path.join(self.data_path, self.tsv_path, 'follower_num.tsv'), 'w') as f:
                for k, v in self.follower_num.items():
                    f.write(f'{k}\t{v}\n')
        else:
            with open(os.path.join(self.data_path, self.tsv_path, 'follower.tsv'), 'r') as f:
                self.follower = [x.strip() for x in f if x != '']
            with open(os.path.join(self.data_path, self.tsv_path, 'follower_num.tsv'), 'r') as f:
                self.follower_num = {x.strip().split('\t')[0]: int(x.strip().split('\t')[1]) for x in f if x != ''}

    def _get_followee(self):
        '''フォロイーのID取得'''
        if self.follower_update:
            print('_get_followee')
            followee_ids = tweepy.Cursor(self.api.friends_ids, id=self.my_id, cursor=-1).items()
            for i, followee_id in enumerate(followee_ids):
                self.followee.append(followee_id)
                self.followee_num.update({followee_id: i})
            with open(os.path.join(self.data_path, self.tsv_path, 'followee.tsv'), 'w') as f:
                for x in self.followee:
                    f.write(f'{x}\n')
            with open(os.path.join(self.data_path, self.tsv_path, 'followee_num.tsv'), 'w') as f:
                for k, v in self.followee_num.items():
                    f.write(f'{k}\t{v}\n')
        else:
            with open(os.path.join(self.data_path, self.tsv_path, 'followee.tsv'), 'r') as f:
                self.followee = [x.strip() for x in f if x != '']
            with open(os.path.join(self.data_path, self.tsv_path, 'followee_num.tsv'), 'r') as f:
                self.followee_num = {x.strip().split('\t')[0]: int(x.strip().split('\t')[1]) for x in f if x != ''}

    def _download_user_info(self, l):
        '''ユーザ情報を取得しjsonにdumpしつつログを取る'''
        if int(self.user_json_update) > 0:
            print('_download_user_info')
            with open(os.path.join(self.data_path, 'twlog.txt'), 'a') as fl:
                for i, u in enumerate(tqdm(l)):
                    if int(self.user_json_update) == 2:
                        # non update
                        if os.path.exists(os.path.join(self.data_path, self.json_path, f'{u}.json')):
                            continue
                    fl.write('[{}][{}]user:{}\n'.format(datetime.now(), i, u))
                    try:
                        user = self.api.get_user(u)
                    except tweepy.error.TweepError:
                        # 凍結されたアカウント等
                        continue
                    with open(os.path.join(self.data_path, self.json_path, f'{u}.json'), 'w') as f:
                        json.dump(user._json, f)

    def _get_twlog(self):
        '''_download_user_infoで生成されるログの雑parser'''
        twlog = {}
        with open(os.path.join(self.data_path, './twlog.txt'), 'r') as f:
            for row in f:
                x = row.strip().split(']')
                twlog[x[2].split(':')[1]] = x[0].replace('[', '')
        return twlog

    def _list_check(self, user_id):
        '''idが入っているListのリストを返す'''
        return [x[1] for x in self.user_list if user_id in self.list_dic[x[0]]]

    def _add_data(self, data_df):
        '''pandasに追加するデータ'''
        # descriptionの長さ
        data_df['description_length'] = data_df.description.apply(lambda x: len(x) if type(x) == str else 0)
        # アカウント作成から今日までの日数
        data_df['diff_created_at'] = data_df.created_at.apply(lambda x: (pd.Timestamp.utcnow() - x).days)
        # 最新ツイート投稿から今日までの日数
        data_df['diff_toptweet_created_at'] = data_df.toptweet_created_at.apply(lambda x: (pd.Timestamp.utcnow() - x).days)
        # SNの長さ
        data_df['sn_length'] = data_df.screen_name.apply(lambda x: len(x))
        # followerかどうか(フォローしているかどうかはAPIが返してくれる)
        data_df['followed'] = data_df.id_str.apply(lambda x: x in self.follower)
        # 自分が入れたリスト
        data_df['joined_list'] = data_df.id_str.apply(self._list_check)
        # フォロー、フォロワーとなった順番
        data_df['follower_number'] = data_df.id_str.apply(lambda x: self.follower_num.get(x, 9999999))
        data_df['followee_number'] = data_df.id_str.apply(lambda x: self.followee_num.get(x, 9999999))
        return data_df

    def _convert_pandas(self):
        '''jsonを全てロードしてdfにしてdump'''
        if not self.df_update:
            with open(os.path.join(self.data_path, 'twdata.pkl'), 'rb') as f:
                df = pickle.load(f)
            return df
        print('_convert_pandas')
        twlog = self._get_twlog()
        all_data_list = []
        for x in tqdm(Path(os.path.join(self.data_path, self.json_path)).glob('*.json')):
            j = json.load(x.open('r'))
            d = {}
            for k, v in j.items():
                if k in must_key:
                    d[k] = v
                elif k in must_json_key:
                    if k == 'entities':
                        # urlのURL展開結果を保存
                        for i, url_data in enumerate(v.get('url', {}).get('urls', [])):
                            for urlk, urlv in url_data.items():
                                if urlk == 'expanded_url':
                                    d['expanded_url_{}'.format(i)] = urlv
                        # bio内のURL展開結果を保存
                        for i, url_data in enumerate(v.get('description', {}).get('urls', [])):
                            for urlk, urlv in url_data.items():
                                if urlk == 'expanded_url':
                                    d['description_expanded_url_{}'.format(i)] = urlv
                        # 個数も保存
                        d['expanded_url_num'] = len(v.get('url', {}).get('urls', []))
                        d['description_expanded_url_num'] = len(v.get('description', {}).get('urls', []))
                    elif k == 'status':
                        # 最新ツイートの情報も保存（）
                        d['toptweet_created_at'] = v['created_at']
                        d['toptweet_id'] = v['id_str']
                        d['toptweet_text'] = v['text']
                        d['toptweet_created_at'] = v['created_at']
                        d['toptweet_source'] = v['source']
                        d['toptweet_lang'] = v['lang']
                        # 公式RTかどうか
                        if 'retweeted_status' in v.keys():
                            d['toptweet_retweet_flag'] = True
                        else:
                            d['toptweet_retweet_flag'] = False
            # twlogに記録されたデータを取得した日時
            d['get_date'] = twlog[j['id_str']]
            all_data_list.append(d)
        # convert pandas
        data_df = pd.DataFrame(all_data_list)
        data_df['created_at'] = pd.to_datetime(data_df['created_at'], utc=True)
        data_df['get_date'] = pd.to_datetime(data_df['get_date'], utc=True)
        data_df['toptweet_created_at'] = pd.to_datetime(data_df['toptweet_created_at'], utc=True)
        for x in ['toptweet_id', 'id_str']:
            data_df[x] = data_df[x].astype('object')
        data_df = self._add_data(data_df)
        print('dump pkl...')
        with open(os.path.join(self.data_path, 'twdata.pkl'), 'wb') as f:
            pickle.dump(data_df, f)
        return data_df

    def _get_list(self):
        if self.list_update:
            print('_get_list')
            with open(os.path.join(self.data_path, self.tsv_path, 'user_list.tsv'), 'w') as f:
                for twilist in self.api.lists_all(screen_name=self.my_id):
                    f.write(f'{twilist.name}\t{twilist.slug}\n')
                    self.user_list.append([twilist.name, twilist.slug])
        else:
            with open(os.path.join(self.data_path, self.tsv_path, 'user_list.tsv'), 'r') as f:
                for x in f:
                    self.user_list.append(x.strip().split('\t'))

    def _get_list_users(self, slug):
        if self.list_user_update:
            print(f'_get_list_users:{slug[0]}')
            with open(os.path.join(self.data_path, self.tsv_path, f'list_{slug[1]}.tsv'), 'w') as f:
                for member in tweepy.Cursor(self.api.list_members, slug=slug[1], owner_screen_name=self.my_id).items():
                    self.list_dic[slug[1]].append(member.id_str)
                    f.write(f'{member.id_str}\n')
        else:
            with open(os.path.join(self.data_path, self.tsv_path, f'list_{slug[1]}.tsv'), 'r') as f:
                for x in f:
                    self.list_dic[slug[1]].append(x.strip())

    def _user_list(self):
        dic = {}
        for row in self.data_df.itertuples():
            tmp = []
            for x in row.joined_list:
                for y in self.user_list:
                    if x == y[1]:
                        tmp.append(y[0])
            dic[row.id_str] = tmp
        return dic

    def unfollow(self, x):
        self.api.destroy_friendship(x)
        self.data_df.loc[self.data_df['id_str'] == x, 'following'] = False
        self.save()

    def follow(self, x):
        self.api.create_friendship(x, True)
        self.data_df.loc[self.data_df['id_str'] == x, 'following'] = True
        self.save()

    def list_manage(self, uid, l):
        '''リストに追加削除'''
        slugs = set(self.user_list_dic[uid])
        ls = set(l)
        # 追加
        for x in list(ls - slugs):
            self.api.add_list_member(user_id=uid, slug=x, owner_screen_name=self.my_id)
            self.user_list_dic[uid].append(x)
        # 削除
        for x in list(slugs - ls):
            self.api.remove_list_member(user_id=uid, slug=x, owner_screen_name=self.my_id)
            self.user_list_dic[uid].remove(x)
        self.save()

    def save(self):
        self.data_df['joined_list'] = self.data_df.id_str.apply(lambda x: self.user_list_dic[x])
        with open(os.path.join(self.data_path, 'twdata.pkl'), 'wb') as f:
            pickle.dump(self.data_df, f)


if __name__ == '__main__':
    # env
    config = {}
    try:
        config['CONSUMER_KEY'] = os.environ['CONSUMER_KEY']
        config['CONSUMER_SECRET'] = os.environ['CONSUMER_SECRET']
        config['ACCESS_TOKEN'] = os.environ['ACCESS_TOKEN']
        config['ACCESS_TOKEN_SECRET'] = os.environ['ACCESS_TOKEN_SECRET']
        my_id = os.environ['TWITTER_ACCOUNT']
    except Exception as e:
        print(e)
        print('[[ Please set twitter token in environment variables !!]]')
        sys.exit()
    parser = argparse.ArgumentParser()
    parser.add_argument('--follower_update', action='store_true')
    parser.add_argument('--list_update', action='store_true')
    parser.add_argument('--list_user_update', action='store_true')
    parser.add_argument('--df_update', action='store_true')
    parser.add_argument('--user_json_update', default=0, type=int)
    args = parser.parse_args()
    print(args)
    print('data making')
    DM = DataManager(my_id, config, args.follower_update, args.user_json_update, args.df_update, args.list_update, args.list_user_update)
    print('data managed')
