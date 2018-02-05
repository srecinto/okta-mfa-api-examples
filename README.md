# Okta MFA via Okta API examples

This project was built using Python 2.7

This projust is geard towards providing some examples of how to umplement various MFA use cases using Okta's API's for a custom MFA user experience.

Examples: 
Custom MFA flows for restting a users password in Okta

## Requirements
* Python 2.7
* Okta domain
* Okta API Token
* Okta MFA License

## Dependencies
You can run all the dependencies via the requirements.txt
`pip install -r requirements.txt`

Or run them individually

**linter - flake8**

`pip install flake8`

**Web Framework - flask**

`pip install flask`

**HTTP Framework - Update requests**

Needed to install an update to fix a compatability issue

`pip install requests --upgrade`

## How to Run

NOTE: You may need to configure ports to listen to for serviing up the site

`python main.py`

## Set up Okta for MFA
The following steps are needed to run this example with your Okta Org (Tenant)

### Step 1: Set up API Token
1. Log into your Okta org admin dashboard and navigate to Security -> API on the main menu
2. Select "Token"
3. Select "Create Token" then enter a name
4. Copy the API token and save it.

### Step 2: Set up MFA Factors
1. Navigate to Security -> Multifactor on the Admin dashboard
2. Enable the factors you want to use, this demo uses the following factors though:
    2. SMS
    2. Voice Call
    2. Okta Verify + Push Notification
    2. Google Authenticator

### Step 3: Setup MFA Enrollment Policy
1. Navigate to Security -> Multifactor on the Admin dashboard
2. Select "Factor Enrollment"
3. Select "Add Multifactor Policy"
4. Give the policy a name, assign it to a group or set of groups
5. Set the factors (SMS, Voice call, Okta Verify, Google Authenticator) as optional;
6. Select "Add Rule", give it a name, select "the first time user is challenged for MFA" for "Enroll Multi-factor", select "Anywhere" for "is user's IP is"
7. Then save the policy

### Step 4: Data Verification
Verify test users or selected users are set up and assigned to test MFA groups in Okta fo rtest

### Step 5: Edit config.py
Set Okta org, API Token (the one saved from Step 1) and optionally set OIDC app settings from Okta if you would like to test authentication as well

### Step 6: Run the application
After running the app, navigate to the landing page of the app (based on the app url you configured) then select "Forgot Password", then enter the email or user name you would like to try and reset in Okta.

## Notes:
For an idea how the Password Rester MFA flow works, please review the following method in the main.py filename
* show_change_password - Displays the password change screen only with a proper posting of the user id and one time token (ott)
* change_password - Verifies the password reset ott then verifies the change password matches the confirm password, then updates the new password on the user profile
* push_mfa_code - pushes the MFA request based on the MFA type i.e. SMS will send the OTP via SMS text, it also verifies the otp and return an ott upon successful verification_Value
* mfa_verification_poll - Will make a request to check if the Okta Verify Push notification has completed and return the results.  This endpoint can be polled continuously.



