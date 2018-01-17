import os
import config
import json

from flask import Flask, request, send_from_directory, redirect, make_response, render_template
from utils.rest import OktaUtil


"""
GLOBAL VARIABLES ########################################################################################################
"""
app = Flask(__name__)
app.secret_key = "6w_#w*~AVts3!*yd&C]jP0(x_1ssd]MVgzfAw8%fF+c@|ih0s1H&yZQC&-u~O[--"  # For the session


"""
ROUTES ##################################################################################################################
"""

@app.route('/<path:filename>')
def serve_static_html(filename):
    """ serve_static_html() generic route function to serve files in the 'static' folder """
    print "serve_static_html('{0}')".format(filename)
    root_dir = os.path.dirname(os.path.realpath(__file__))
    return send_from_directory(os.path.join(root_dir, 'static'), filename)


@app.route('/')
def index():
    """ handler for the root url path of the app """
    print "index()"
    message = ""
    is_logged_in = False
    
    response = make_response(render_template("index.html", okta_config=config.okta, is_logged_in=is_logged_in, message=message))
    
    return response


@app.route('/refresh_okta_api_token', methods=["GET"])
def refresh_okta_api_token():
    """ Helper method to refresh the okta api token when deployed live for continual testing.  Helps to prevent the API key from expiring from no use """
    print "refresh_okta_api_token()"
    response = { "status": "fail" }
    okta_util = OktaUtil(request.headers, config.okta)
    
    groups = okta_util.search_groups("Everyone", 1);  # Search for the default 'Everyone' group in Okta
    if len(groups) == 1:
        response["status"] = "success"
    
    return json.dumps(response);


"""
MAIN ##################################################################################################################
"""
if __name__ == "__main__":
    # This is to run on c9.io.. you may need to change or make your own runner
    print "okta_config: {0}".format(json.dumps(config.okta, indent=4, sort_keys=True))
    app.run(host=os.getenv("IP", "0.0.0.0"), port=int(os.getenv("PORT", 8080)))