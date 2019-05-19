import re
date_reg = re.compile(r'(\d{4})-(\d{1,2})-(\d{1,2})')


def convert_list(dm, l):
    return [{'key': x[0], 'flag': x[0] in l} for x in dm.user_list]


def reconv_list(dm, l):
    return [y[1] for x in l for y in dm.user_list if y[0] == x]


def split_tag(x):
    if x is None:
        return ''
    if type(x) != str:
        return str(x)
    return x.split('<')[1].split('>')[1] if '<' in x else x


def convert_url(url):
    return url if url is None else url.replace('_normal', '')


def get_url(row):
    if type(row['expanded_url_0']) != str:
        return ''
    if len(row['expanded_url_0']) > 70:
        return row['url']
    return row['expanded_url_0']


def shortu(url):
    if len(url) > 33:
        return url[:32] + '…'
    return url


def req2df(dm, req):
    df = dm.data_df
    query = req.get('query', '')
    if query:
        df = df.query(query)
    at = req.get('fromcreated', '')
    if at and date_reg.search(at):
        df = df[df['created_at'] >= at]
    at = req.get('tocreated', '')
    if at and date_reg.search(at):
        df = df[df['created_at'] <= at]
    at = req.get('fromlasttw', '')
    if at and date_reg.search(at):
        df = df[df['toptweet_created_at'] >= at]
    at = req.get('tolasttw', '')
    if at and date_reg.search(at):
        df = df[df['toptweet_created_at'] <= at]
    sort = req.get('sort', '')
    if sort and sort in df.columns:
        ascend = req.get('ascend', '').lower() == 'true'
        df = df.sort_values(sort, ascending=ascend)
    sample = req.get('sample', '')
    if sample:
        sample = int(sample)
        if len(df) >= sample:
            df = df.head(sample)
    return df


def get_users(dm, req):
    print(req)
    df = req2df(dm, req)
    users = []
    for _, row in df.iterrows():
        users.append({
            'idstr': row['id_str'],
            'ulist': convert_list(dm, row['joined_list']),
            'images': {
                'name': row['name'],
                'sn': f'@{row["screen_name"]}',
                'profurl': f'https://twitter.com/{row["screen_name"]}',
                'banner': row['profile_banner_url'],
                'icon': convert_url(row['profile_image_url']),
                'protect': row['protected'],
                'verified': row['verified'],
                'following': row['following'],
                'followed': row['followed']
            },
            'info': {
                'created': row["created_at"],
                'lang': row["lang"],
                'location': row["location"],
                'url': get_url(row),
                'urlt': shortu(get_url(row)),
                'tweet': row["statuses_count"],
                'follower': row["followers_count"],
                'follow': row["friends_count"],
                'fav': row["favourites_count"],
                'inlist': row["listed_count"],
                'bio': row['description']
            },
            'tweet': {
                'text': row['toptweet_text'],
                'created': row['toptweet_created_at'],
                'source': split_tag(row['toptweet_source'])
            }
        })
    return users
