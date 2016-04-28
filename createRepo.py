# Rob Casale
# This will:
# - Validate user does exist and if it does not throw Error
# - Validate repo does not exist and if it does throw Error
# - Create Repo
# Return codes:
# - 0 success
# - 1 user does not exist
# - 2 repo exist
# - 3 error create repo
# - 8 others

import requests, os, ssl, urllib2, base64, json, sys

# Another possible context option
# context=ssl._create_unverified_context()

# Get pass verification and get response
gcontext = ssl.SSLContext(ssl.PROTOCOL_TLSv1)

# API url requests
test_url='https://www.google.com'
url_account='https://cdldvostk1vdtr001.es.ad.adp.com/api/v0/accounts/'
url_repo='https://cdldvostk1vdtr001.es.ad.adp.com/api/v0/repositories/'

# Login credentials
username='casaler'
password='adpadp11'

# Proxy settings
proxies={
  "http":"http://paascloud:8e)P4m)I5y(F9@usproxy.es.oneadp.com:8080",
  "https":"http://paascloud:8e)P4m)I5y(F9@usproxy.es.oneadp.com:8080",
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
if len(sys.argv) != 3:
	print 'exit(8): enter username and repository only'
	exit()

user=sys.argv[1]
repo=sys.argv[2]

user_code=None
url_user_account=url_account+user

try:
	# validate username
	user_code=get_code(build_request(url_user_account))
	repo_code=None
	url_user_repo=url_repo+user+'/'+repo

	try:
		# validate repository
		repo_code=get_code(build_request(url_user_repo))
		print 'exit(2): repository already exist'

	except urllib2.HTTPError as e:
		if e.code == 404:
			# repo does not exist
			#visibility=raw_input('Enter the visibility of the repository[public/private]: ').lower()
			visibility='public'
			try:
				# create repo
				create_repository_code(build_request(url_repo+user),repo,visibility)
				print 'exit(0): success'
			
			except urllib2.HTTPError as e:
				if e.code == 400:
					# repo exists - should not happen
					print 'exit(2): repository already exist'
				else:
					# could not create repositroy
					print 'exit(3): could not create repository'
		else:
			# could not access repo details
			print 'exit(8): could not access repository details'

except urllib2.HTTPError as e:
	if e.code == 404:
		# username does not exist
		print 'exit(1): username does not exist'
	else:
		# could not access account details
		print 'exit(8): could not access account details'


