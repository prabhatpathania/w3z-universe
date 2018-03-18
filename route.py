import json

from flask import Flask, request, redirect, abort, render_template, Response
from config import get_config
from w3z_app import affiliate, core, db, ads

config, debug = get_config()

app = Flask(__name__)


@app.errorhandler(404)
def not_found(error):
    app.logger.error(error)
    return "What are you looking for ? 404!"


@app.route('/')
def index():
    promo_list = ads.get_promos(config)
    return render_template('index.html', promo_list=promo_list, config=config)


@app.route('/slack', methods=['GET', 'POST'])
def slack():
    text = request.form.get('text').replace('https://', '').replace('http://', '')
    query = {'protocol': 'http://', 'url': text}
    data = json.loads(work(query))
    return Response(json.dumps({'response_type': 'in_channel', 'text': data['u']}), mimetype='application/json')


@app.route('/work', methods=['POST'])
def work(query=None):
    if query is None:
        query = request.get_json()
    print(query)
    url = query['protocol'] + query['url']
    reqhandle = query['reqhandle']
    
    if reqhandle is not '' and reqhandle is not None:                             #Private link requested
        u = db.get_link(reqhandle, True)
        if u is None:
            u = db.set_link(url, reqhandle, True)
            if  u:
                print(json.dumps({'u': config['site_url'] + '/' + reqhandle}))
                return json.dumps({'u': config['site_url'] + '/' + reqhandle})
            else:
                return json.dumps({'u': ''})
        else:
            return json.dumps({'u': ''})
    else:        
        url = affiliate.attach_affiliates(config, url)
        u = db.get_link(url, True)
        if u is not None:
            return json.dumps({'u': config['site_url'] + '/' + u})
        else:
            u_hash = core.get_hash(url)
            u = db.get_link(u_hash, False)
            while u is not None:
                core.magic += 1
                u_hash = core.get_hash(url)
                u = db.get_link(u_hash, False)
                if u is None:
                    u = db.get_link(u_hash, True)       # check if generated link is not in privatelinks table
            db.set_link(url, u_hash, None)
            return json.dumps({'u': config['site_url'] + '/' + u_hash})


@app.route('/privacy', methods=['GET'])
def privacy():
    return render_template('privacy.html', config=config)


@app.route('/<slug>', methods=['GET'])
def open_link(slug=None):
    domains = ['amazon.in', 'amazon.com', 'flipkart.com', 'google.com']
    link = db.get_link(slug, None)
    if link is not None:
        print(link)
        if any(one_domain in link for one_domain in domains) or 'http://' in link:
            return redirect(link, code=301)
        else:
            return render_template('preview.html', link=link, config=config)
    else:
        abort(404)


if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=debug)
