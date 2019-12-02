"""
Copyright 2019 Jarred Vardy

This file is part of ibpp.me.

ibpp.me is free software: you can redistribute it and/or modify it
under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

ibpp.me is distributed in the hope that it will be useful, but
WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
General Public License for more details.

You should have received a copy of the GNU General Public License
along with ibpp.me. If not, see http://www.gnu.org/licenses/.
"""

import os
import uuid
import csv
import sys

from flask import Flask, Response, redirect, request, render_template, make_response, jsonify
import redis

short_domain = os.environ["SHORT_DOMAIN"]
short_length = int(os.environ["SHORT_LENGTH"])
whitelist = os.environ["WHITELISTED_SITES"]

host = os.environ['REDIS_HOST']
port = int(os.environ['REDIS_PORT'])
db = int(os.environ['REDIS_DB'])

redis_client = redis.Redis(host=host, port=port, db=db)

whitelist_array = None
csv_reader = csv.reader(whitelist.split('\n'), delimiter=',')
for row in csv_reader:
    whitelist_array = row
if whitelist_array is None:
    print("You need an array of whitelisted sites.")
    sys.exit(1)

app = Flask(__name__)


def _build_cors_prelight_response():
    response = make_response()
    response.headers.add("Access-Control-Allow-Origin", "*")
    response.headers.add("Access-Control-Allow-Headers", "*")
    response.headers.add("Access-Control-Allow-Methods", "*")
    return response


@app.route('/<short_url>', methods=["GET"])
def short_page(short_url):
    red_res = redis_client.get(short_url).decode("utf-8")
    if red_res is None:
        return render_template("404.html")
    else:
        return redirect(red_res, code=301)


@app.route('/function/shorten', methods=["POST", "OPTIONS"])
def shorten_link():
    if request.method == "OPTIONS":  # CORS preflight
        return _build_cors_prelight_response()
    elif request.method == "POST":
        req = request.json
        page_url = req['page']

        #accept = False
        #for whitelist_test in whitelist_array:
        #    if page_url.startswith(whitelist_test):
        #        accept = True
        #if not accept:
        #    return Response(status=403)

        red_res = redis_client.get(page_url).decode("utf-8")
        if red_res is None:
            short = str(uuid.uuid4())[:short_length]
            redis_client.set(page_url, short)
            redis_client.set(short, page_url)
            response = jsonify({"url": short_domain + short})
            response.headers.add("Access-Control-Allow-Origin", "*")
            return response
        else:
            response = jsonify({"url": short_domain + red_res})
            response.headers.add("Access-Control-Allow-Origin", "*")
            return response


if __name__ == '__main__':
    app.run(
        host="0.0.0.0",
        port=5000
    )
