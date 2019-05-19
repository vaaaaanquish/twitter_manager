from flask import Flask, render_template, request, Response
from data_manager import DataManager
from utils import get_users, reconv_list
import json
import os
import sys
app = Flask(__name__)

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
dm = DataManager(my_id, config)


@app.route('/')
def main():
    r = request.args
    req = {}
    req['nq'] = r.get('nq', 'followed')
    req['fcrq'] = r.get('fcrq', 'yy-mm-dd')
    req['tcrq'] = r.get('tcrq', 'yy-mm-dd')
    req['fltq'] = r.get('fltq', 'yy-mm-dd')
    req['tltq'] = r.get('tltq', 'yy-mm-dd')
    req['sorq'] = r.get('sorq', 'follower_number')
    req['asq'] = r.get('asq', 'True')
    req['samq'] = r.get('samq', '100')
    return render_template("index.html", req=req)


@app.route('/get_table')
def get_table():
    req = request.args
    users = get_users(dm, req)
    return render_template("table.html", users=users)


@app.route("/list_submit", methods=['POST'])
def list_update():
    d = request.json
    uid = d['id'].split('_')[1]
    ul = [json.loads(x)['key'] for x in d['ul'] if json.loads(x)['checked']]
    try:
        dm.list_manage(uid, reconv_list(dm, ul))
        response = Response('checked: ' + ','.join(ul), mimetype='text')
        response.status_code = 200
        return response
    except Exception as e:
        print(e)
        return Response(str(e), 500)


@app.route("/follow", methods=['POST'])
def follow():
    d = request.json
    uid = d['id'].split('_')[1]
    try:
        if d['follow']:
            dm.unfollow(uid)
            t = 'unfollow'
        else:
            dm.follow(uid)
            t = 'follow'
    except Exception as e:
        print(e)
        return Response(str(e), 500)
    response = Response(f'success: {t}', mimetype='text')
    response.status_code = 200
    return response


if __name__ == "__main__":
    try:
        app.run(debug=True)
    except KeyboardInterrupt:
        dm.save()
    except Exception:
        raise
