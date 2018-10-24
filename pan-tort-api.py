# Copyright (c) 2018, Palo Alto Networks
#
# Permission to use, copy, modify, and/or distribute this software for any
# purpose with or without fee is hereby granted, provided that the above
# copyright notice and this permission notice appear in all copies.
#
# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
# WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
# ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
# WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
# ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
# OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.

# Author: SP-Solutions <sp-solutions@paloaltonetworks.com>

'''
Palo Alto Networks Testing Output Response Toolkit

Provides a single REST API endpoint to run pan-tort programmatically

Running:
   Run the flask service directly with:
    `pip install -r requirements.txt`
    `export FLASK_APP=./pan-tort-api.py`
    `flask run`

This software is provided without support, warranty, or guarantee.
Use at your own risk.

'''


import os
import sys
import time
import json
import logging
import requests
import threading

# from html import unescape
# from html.parser import HTMLParser

from project import app
from project.hash_data import processHashList
from flask import Flask, abort, render_template, request, send_file
from werkzeug.exceptions import BadRequest, HTTPException


@app.errorhandler(501)
def custom501(error):
    response = json.dumps({'message': error.description['message']})
    return response


# default route -
# FIXME - provide simple swagger api docs
@app.route('/')
def index():
    '''
    Default route, return simple HTML page
    :return:  index.html template
    '''
    return render_template('index.html', title='PAN-TORT')


@app.route('/process_hashes', methods=['POST'])
def process_hashes():
    '''
    Requires a JSON formatted payload with the following keys:
    queryTag - name of search so you can query it later in Kibana
    hashes - Comma delimited list of hashes to go get info on
        
    :return: formatted file to display in AFrame UI
        HTTP-400 if required API key is missing - this comes from config
        HTTP-500 on application error
    '''
    try:
        postedJSON = request.get_json(force=True)
        app.logger.debug(f"Received the following JSON: {postedJSON}")
        app.config['QUERY_TAG'] = postedJSON['query_tag']
        hashListString = postedJSON['hashes']
        app.config['OUTPUT_TYPE'] = postedJSON['output']
        app.config['HASH_TYPE'] = postedJSON['hash_type']

        # hash should have newlines replaced by HTML char for newline '%0A', 
        # let's split on that here to get a list
        # could also check for ',' and split on that too if necessary
        if '%0A' in hashListString:
            hashList = hashListString.strip('%0A').split('%0A')
        elif ',' in hashListString:
            hashList = hashListString.split(',')
        elif '\\n' in hashListString:
            # it's something else like
            hashList = hashListString.split('\\n')
        else:
            return abort(500, 'Could not parse JSON payload ' + str(postedJSON))
        
        # now we should have a valid hash list to work with
        app.logger.info(f"Hash list is {hashList}")
        
        if "text" in app.config['OUTPUT_TYPE']:
            outFile = processHashList(hashList)
            path, fileName = os.path.split(f"{outFile}")
            app.logger.debug(f"returning fileName is {fileName}")
            print(f"path is {path}")
            return send_file(f"templates/output/{fileName}", mimetype='application/octet-stream', as_attachment=True)
        else:
            hashListResult = processHashList(hashList)
            return render_template('kibana_page.html',list=hashListResult)
        
        

    except BadRequest as br:
        app.logger.error(br)
        return abort(500, 'Could not parse JSON payload')
    except HTTPException as he:
        app.logger.error(he)
        return abort(500, 'Exception in request')
    except KeyError as ke:
        app.logger.error(ke)
        return abort(400, 'not all keys present')
    except Exception as e:
        app.logger.error(e)
        errorMessage = f"Problem with query to Autofocus: {e}"
        abort(501, {'message': errorMessage})
        #abort(501, {'message': f'Problem with query to Autofocus {e}'})
        


@app.before_first_request
def init_application():

   # Check to make sure we have the API key(s) set first
    if app.config['AUTOFOCUS_API_KEY'] == "NOT-SET":
        app.logger.critical("API Key for Autofocus is not set in .panrc, exiting")
        exit()
    else: 
        app.logger.info(f'Starting Pan-Tort')

    def start_loop():
        not_started = True
        app.logger.info(f"INIT - Initializing Background Processes")

        while not_started:
            flaskHost = app.config['FLASK_HOST']
            flaskPort = app.config['FLASK_PORT']
            try:
                app.logger.info(f'{flaskHost}:{flaskPort}')
                req = requests.get(f'http://{flaskHost}:{flaskPort}/')
                app.logger.info(f'{req.status_code}')
                if req.status_code == 200:
                    app.logger.info(f"INIT - Pan-Tort server started @ "
                                    f"{flaskHost}:{flaskPort}")
                    not_started = False
                    app.logger.info(f"Elasticsearch is set to "
                                    f"{app.config['ELASTICSEARCH_HOST']}:"
                                    f"{app.config['ELASTICSEARCH_PORT']}")
            except:
                app.logger.info(f"INIT - Server not yet started")
                time.sleep(2)
    
    
    thread = threading.Thread(target=start_loop)
    thread.start()

if __name__=='__main__':
    init_application()
    app.run(host="0.0.0.0",port="5010",debug=True)
