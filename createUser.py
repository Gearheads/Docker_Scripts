# Rob Casale
# This will:
# - Validate user does not exist and if it does throw Error
# - Create user
# Return codes:
# - 0 success
# - 1 user exist
# - 2 error create user
# - 8 others

import requests, os, ssl, urllib2, base64, json, sys

# Get pass verification and get response
gcontext = ssl.SSLContext(ssl.PROTOCOL_TLSv1)

# API url requests
test_url='https://www.google.com'
url_account='https://<dtr-hostname>/api/v0/accounts/'
url_repo='https://<dtr-hostname>/api/v0/repositories/'

# Login credentials
username='casaler'
password='<password>'

# Proxy settings
proxies={
  "http":"http://<username>:<password>@<proxy-info>:8080",
  "https":"http://<username>:<password>@<proxy-info>:8080",
}

def build_request(requestUrl):
        # Build request
        request=urllib2.Request(requestUrl)
        base64string = base64.encodestring('%s:%s' % (username, password)).replace('\n', '')
        request.add_header("Authorization", "Basic %s" % base64string)
        return request

def get_info(request):
        info=urllib2.urlopen(request,context=gcontext).read()
        return info

def get_code(request):
        code=urllib2.urlopen(request,context=gcontext).getcode()
        return code

def create_account_code(request,user):
        data={'type':'user','name':user,'password':password}
        request.add_header('Content-Type', 'application/json')
        code=urllib2.urlopen(request,json.dumps(data),context=gcontext).getcode()
        return code

def activate_account_code(request,user):
        request.add_header('Content-Type', 'application/json')
        request.get_method=lambda:'PUT'
        code=urllib2.urlopen(request,json.dumps(user),context=gcontext).getcode()
        return code

# Retrieve username and from user
if len(sys.argv) != 2:
	print 'exit(8): enter only the username'
	exit()

user=sys.argv[1]
user_code=None
url_user_account=url_account+user

try:
        # validate username
        user_code=get_code(build_request(url_user_account))
	print 'exit(1): username already exists'

except urllib2.HTTPError as e:
        if e.code == 404:
                # username does not exist
                try:
                	# create user
                	create_code=create_account_code(build_request(url_account),user)
                	activate_code=activate_account_code(build_request(url_account+user+'/activate'),user)
					print 'exit(0): success'

				except urllib2.HTTPError as e:
					if e.code == 400:
						# username exists - should not happen
						print 'exit(1): username already exists'
					else:
						# could not create username
						print 'exit(2): could not create username'
        else:
                # could not access account details
                print 'exit(8): could not access account details'
