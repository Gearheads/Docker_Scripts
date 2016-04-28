# Rob Casale
# This will:
# - Validate user does not exist and if it does throw Error
# - Validate repo does not exist and if it does throw Error
# - Create user
# - Create Repo
# - Assigned the Repo to the user.
# Return codes:
# - 0 success
# - 1 user exist
# - 2 repo exist
# - 4 error create user
# - 5 error create repo
# - 8 others

import requests, os, ssl, urllib2, base64, json

# Another possible context option
# context=ssl._create_unverified_context()

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

def create_repository_code(request,repo,visibility):
	data={'name':repo,'visibility':visibility}
        request.add_header('Content-Type', 'application/json')
        code=urllib2.urlopen(request,json.dumps(data),context=gcontext).getcode()
        return code

# Retrieve username and repo from user
user=raw_input('Enter your username: ')
repo=raw_input('Enter the name of the repository: ')

user_code=None
url_user_account=url_account+user

try:
	# validate username
	user_code=get_code(build_request(url_user_account))

except urllib2.HTTPError as e:
	if e.code == 404:
		# username does not exist
		print 'Username',user,'does not exist'
		user_response=raw_input('Would you like to create this username[y/n]: ')
		if user_response.lower() == 'y' or user_response.lower() == 'yes':
			try:
				# create user
				create_code=create_account_code(build_request(url_account),user)
				activate_code=activate_account_code(build_request(url_account+user+'/activate'),user)
			
			except urllib2.HTTPError as e:
				if e.code == 400:
					# username exists - should not happen
					print 'exit: 1'
					exit()
				else:
					# could not create username
					print 'exit: 4'
					exit()
		else:
			# user does not want to create username
			print 'exit: 8'
			exit()
	else:
		# could not access account details
		print 'exit: 8'
		exit()

repo_code=None
url_user_repo=url_repo+user+'/'+repo

try:
	# validate repository
	repo_code=get_code(build_request(url_user_repo))

except urllib2.HTTPError as e:
	if e.code == 404:
		# repo does not exist
		print 'Repository',repo,'does not exist'
		repo_response=raw_input('Would you like to create this repository[y/n]: ')
		if repo_response.lower() == 'y' or repo_response.lower() == 'yes':
			#visibility=raw_input('Enter the visibility of the repository[public/private]: ').lower()
			visibility='public'
			try:
				# create repo
				create_repository_code(build_request(url_repo+user),repo,visibility)
				print 'exit: 0'
			
			except urllib2.HTTPError as e:
				if e.code == 400:
					# repo exists - should not happen
					print 'exit: 2'
				else:
					# could not create repositroy
					print 'exit: 5'
		else:
			# user does not want to create repo
			print 'exit: 8'
	else:
		# could not access repo details
		print 'exit: 8'

# username and repository exist
if user_code == 200 and repo_code == 200:
	print 'exit: 8'
