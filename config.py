okta = {
    "org_host": "", # Okta host org / tennant URL i.e. https://myoktaorg.okta.com
    "api_token": "", # Okta API Token created for the server side to access Okta's API for your tenant
    "app_host": "", # The URL to access this application, makes redirects and helper urls easier to reference
    "oidc_client_id": "", # OIDC Application created in Okta client id
    "oidc_client_secret": "", # OIDC Application created in Okta client secret
    "redirect_uri": "", # OIDC Redirect URI to handle auth code flow
    "post_oidc_redirect": "", # url to redirect to after successfuly authenticating and getting an oath token
    "multi_sms_primary_number": "", # Primary SMS number to always reset to for supporting multiple SMS numbers.  This variable is defined in Okta as a string
    "multi_sms_allowed_numbers": "" # List of allowed SMS numbers.  This variable is defined in Okta as a string array
}


"""
User -> Login
Login -> promtps for factor enrolled_factors
User -> selects phone
User -> select Factor Type 


"""
