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
UTILS ###################################################################################################################
"""
def get_session_token(username, password):
    print "get_session_token()"
    okta_util = OktaUtil(request.headers, config.okta)
    session_token = None

    authn_reponse_json = okta_util.get_session_token(username, password)
    if "sessionToken" in authn_reponse_json:
        session_token = authn_reponse_json["sessionToken"]

    return session_token


def is_logged_in():
    print "is_logged_in()"
    result = False
    okta_util = OktaUtil(request.headers, config.okta)
    # first check there is a token
    if("token" in request.cookies):
        token = request.cookies["token"]
        if token != "" and token != "NO_TOKEN":
            # introspect token
            introspection_results_json = okta_util.introspect_oauth_token(token)
            
            if("active" in introspection_results_json):
                result = True
    
    return result

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
    
    response = make_response(render_template("index.html", okta_config=config.okta, is_logged_in=is_logged_in(), message=message))
    
    return response

@app.route('/show_change_password', methods=["POST"])
def show_change_password():
    """ handler for the change password screen"""
    print "show_change_password()"
    print "request.form: {0}".format(json.dumps(request.form, indent=4, sort_keys=True))
    
    response = redirect(config.okta["app_host"]) # redirect to home page if there is no ott
    
    if "ott" in request.form:
        ott = request.form["ott"]
        if ott:
            okta_util = OktaUtil(request.headers, config.okta)
            message = ""
        
            response = make_response(
                render_template("change_password.html", 
                    okta_config=config.okta, 
                    message=message,
                    ott=ott))
    
    return response


@app.route('/change_password', methods=["POST"])
def change_password():
    """ handler actually change the password, requires the ott"""
    print "show_change_password()"
    print "request.form: {0}".format(json.dumps(request.form, indent=4, sort_keys=True))
    
    response = redirect(config.okta["app_host"]) # redirect to home page if there is no ott
    
    if "ott" in request.form:
        ott = request.form["ott"]
        password = request.form["password"]
        confirm_password = request.form["password"]
        is_completed = False
        has_errors = False
        message = ""
        
        if password == confirm_password:
            okta_util = OktaUtil(request.headers, config.okta)
            verify_ott_response = okta_util.verify_password_reset_token(ott)
            print "verify_ott_response: {0}".format(json.dumps(verify_ott_response, indent=4, sort_keys=True))
            user = {
                "id": verify_ott_response["_embedded"]["user"]["id"],
                "credentials": {
                    "password" : { "value": password }
                }
            }
            change_password_response = okta_util.update_user(user)
            print "change_password_response: {0}".format(json.dumps(change_password_response, indent=4, sort_keys=True))
            is_completed = True
        else:
            has_errors = True
            message = "Passwords do not match"
        
        response = make_response(
            render_template("change_password.html", 
                okta_config=config.okta, 
                message=message,
                is_completed=is_completed,
                has_errors=has_errors,
                ott=ott))
    
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


@app.route("/login", methods=["POST"])
def login():
    print "login()"
    print request.form

    okta_util = OktaUtil(request.headers, config.okta)

    # Authenticate via Okta API to get Session Token
    session_token = None
    try:
        if "auth_token" in request.form:
            session_token = okta_util.authenticate_via_activation_token(request.form["auth_token"])
        else:
            session_token = get_session_token(username=request.form["username"], password=request.form["password"])
    except ValueError as err:
        print(err.args)

    print "session_token: {0}".format(session_token)

    # Use Session Token to generatet OIDC Auth Code URL
    if(session_token):
        oidc_auth_code_url = okta_util.create_oidc_auth_code_url(
            session_token,
            config.okta["oidc_client_id"],
            config.okta["redirect_uri"])

        print "url: {0}".format(oidc_auth_code_url)
        # redirect to User Auth Code URL to Get OIDC Code
        return redirect(oidc_auth_code_url)

    else:
        error_list = {
            "messages": [{"message": "Bad user name and/or password"}]
        }
        response = make_response(
            render_template(
                "index.html",
                user={},
                error_list=error_list,
                form_data={},
                okta_config=config.okta,
                is_admin=False
            )
        )
        return response


@app.route("/logout", methods=["GET"])
def logout():
    print "logout()"

    redirect_url = "{host}/login/signout?fromURI={redirect_path}".format(
        host=config.okta["org_host"],
        redirect_path=config.okta["app_host"]
    )

    print "redirect_url: {0}".format(redirect_url)

    response = make_response(redirect(redirect_url))
    response.set_cookie('token', "")
    
    return response


@app.route("/oidc", methods=["POST"])
def oidc():
    print "oidc()"
    print request.form

    redirect_url = ""

    if("error" in request.form):
        oauth_token = "NO_TOKEN"
        redirect_url = config.okta["app_host"]
    else:
        okta_util = OktaUtil(request.headers, config.okta)
        oidc_code = request.form["code"]
        print "oidc_code: {0}".format(oidc_code)
        oauth_response = okta_util.get_oauth_token(oidc_code, config.okta["redirect_uri"])
        print "oauth_response: {0}".format(json.dumps(oauth_response, indent=4, sort_keys=True))
        oauth_token = oauth_response["id_token"]
        redirect_url = config.okta["post_oidc_redirect"]

    response = make_response(redirect(redirect_url))
    response.set_cookie('token', oauth_token)

    return response


@app.route('/push_mfa_code', methods=["POST"])
def push_mfa_code():
    print "push_mfa_code()"
    request_json = request.get_json()
    print "request_json: {0}".format(request_json)
    okta_util = OktaUtil(request.headers, config.okta)
    
    username = request_json["username"]
    factor_type = request_json["factorType"]
    code = None
    if "code" in request_json:
        code = request_json["code"]
    
    user = okta_util.get_user(username)
    # print "user: {0}".format(user, indent=4, sort_keys=True)
    
    response = {"status": "success", "message": "sent"} # alwasy send this down so a malicious user can not farm enrolled factors
    
    if("id" in user):
        okta_user_id = user["id"]
        okta_factor_id = None
        enrolled_factors = okta_util.list_factors(okta_user_id)
        # print "enrolled_factors: {0}".format(json.dumps(enrolled_factors, indent=4, sort_keys=True))
        
        for factor in enrolled_factors:
            # check factor type agains the enroled factor
            print "factor: {0}".format(json.dumps(factor, indent=4, sort_keys=True))
            if (factor["factorType"] == factor_type and factor["provider"] == "OKTA") or (factor["provider"] == factor_type):
                okta_factor_id = factor["id"]
        
        print "okta_factor_id: {0}".format(okta_factor_id)

        if okta_factor_id:
            push_response = okta_util.push_factor_verification(okta_user_id, okta_factor_id, code)
            # print "push_response: {0}".format(json.dumps(push_response, indent=4, sort_keys=True))
            
            # Check for a valid factor result
            if "factorResult" in push_response:
                response["factorResult"] = push_response["factorResult"]
                
                # check if there is a polling link to send back down to the client
                if "_links" in push_response:
                    if "poll" in push_response["_links"]:
                        response["pollingUrl"] = push_response["_links"]["poll"]["href"]
                 
                print "factorResult: {0}".format(push_response["factorResult"])       
                if push_response["factorResult"] == "SUCCESS":  # Means the user successfully passed the factor, so reset the pasword
                    password_reset_response = okta_util.reset_user_password(okta_user_id)
                    print "password_reset_response: {0}".format(json.dumps(password_reset_response, indent=4, sort_keys=True))
                    response["ott"] = password_reset_response["resetPasswordUrl"].replace("{0}/reset_password/".format(config.okta["org_host"]), "")
            else:
                response["status"] = "failed"
                response["message"] = push_response["errorSummary"]
        else:
            print "WARNING: User '{0}' not enrolled in factor: {1}".format(user["profile"]["login"], factor_type)
    else:
        print "WARNING: User '{0}' does not exsist in Okta".format(username)
    
    return json.dumps(response)


@app.route('/mfa_verification_poll', methods=["POST"])
def mfa_verification_poll():
    print "mfa_verification_poll()"
    request_json = request.get_json()
    print "request_json: {0}".format(json.dumps(request_json, indent=4, sort_keys=True))
    polling_url = request_json["pollingUrl"]
    user_name = request_json["userName"]
    
    okta_util = OktaUtil(request.headers, config.okta)
    response = okta_util.execute_get(polling_url, None)
    
    if "factorResult" in response:
        print "factorResult: {0}".format(response["factorResult"])       
        if response["factorResult"] == "SUCCESS":  # Means the user successfully passed the factor, so reset the pasword
            okta_user_id = okta_util.get_user(user_name)["id"]
            password_reset_response = okta_util.reset_user_password(okta_user_id)
            print "password_reset_response: {0}".format(json.dumps(password_reset_response, indent=4, sort_keys=True))
            response["ott"] = password_reset_response["resetPasswordUrl"].replace("{0}/reset_password/".format(config.okta["org_host"]), "")
    
    return json.dumps(response)

"""
MAIN ##################################################################################################################
"""
if __name__ == "__main__":
    # This is to run on c9.io.. you may need to change or make your own runner
    print "okta_config: {0}".format(json.dumps(config.okta, indent=4, sort_keys=True))
    app.run(host=os.getenv("IP", "0.0.0.0"), port=int(os.getenv("PORT", 8080)))