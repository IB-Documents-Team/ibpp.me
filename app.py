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

from flask_cors import CORS, cross_origin
from flask import Flask, Response, redirect, request, render_template, make_response, jsonify
from neomodel import StructuredNode, StringProperty, config

config.DATABASE_URL = os.environ["NEO4J_BOLT_URL"]
short_domain = os.environ["SHORT_DOMAIN"]
short_length = int(os.environ["SHORT_LENGTH"])
whitelist = os.environ["WHITELISTED_SITES"]

whitelist_array = None
csv_reader = csv.reader(whitelist.split('\n'), delimiter=',')
for row in csv_reader:
    whitelist_array = row
if whitelist_array is None:
    print("You need an array of whitelisted sites.")
    sys.exit(1)

app = Flask(__name__)
CORS(app)


class Url(StructuredNode):
    short = StringProperty(unique_index=True, required=True)
    long = StringProperty(unique_index=True, required=True)


def new_url(page_url):
    unique_id = str(uuid.uuid4())[:short_length]
    try:
        url_node = Url.nodes.get(short=unique_id)
        new_url(page_url)
    except Url.DoesNotExist:
        new_url_node = Url(long=page_url, short=unique_id).save()
        return unique_id


def _build_cors_prelight_response():
    response = make_response()
    response.headers.add("Access-Control-Allow-Origin", "*")
    response.headers.add("Access-Control-Allow-Headers", "*")
    response.headers.add("Access-Control-Allow-Methods", "*")
    return response


@app.route('/<short_url>', methods=["GET"])
def short_page(short_url):
    try:
        url_node = Url.nodes.get(short=short_url)
        return redirect(url_node.long, code=301)
    except Url.DoesNotExist:
        return render_template("404.html")


@app.route('/function/shorten', methods=["POST", "OPTIONS"])
@cross_origin()
def shorten_link():
    req = request.json
    page_url = req['page']

    accept = False
    for whitelist_test in whitelist_array:
        if whitelist_test in page_url:
            accept = True
    if not accept:
        return Response(status=403)

    if request.method == "OPTIONS":  # CORS preflight
        return _build_cors_prelight_response()
    elif request.method == "POST":
        try:
            url_node = Url.nodes.get(long=page_url)
            final_url = short_domain + url_node.short
            response = jsonify({"url": final_url})
            response.headers.add("Access-Control-Allow-Origin", "*")
            return response
        except Url.DoesNotExist:
            short_ending = new_url(page_url)
            final_url = short_domain + short_ending
            response = jsonify({"url": final_url})
            response.headers.add("Access-Control-Allow-Origin", "*")
            return response


if __name__ == '__main__':
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )
