# Rob Casale
# 4/22/2016
# This will pull and image from the CDL and promote the image to DC1 and DC2
# The image that gets pulled is specified by the <repository>/<image-name>:<tag>
# <repository> is required
# <image-name> is optional
# <tag> is required
# User will enter their request in the following format:
# 	./promotion.py <repository>/<image-name> <tag>
# Return codes:
# - 0 success
# - 1 repository does not exist
# - 2 image does not exist
# - 3 tag does not exist
# - 4 account does not exist
# - 8 other

import json, sys, requests, os, ssl, urllib2, base64

from docker import Client
cli = Client(base_url='unix://var/run/docker.sock')

# Get pass verification and get response
gcontext = ssl.SSLContext(ssl.PROTOCOL_TLSv1)

# DTR urls
test_dtr_url='dtr.predit-cdl.es.ad.adp.com'
cdl_dtr_url='dtr.dit-cdl.es.ad.adp.com'
dc1_dtr_url='dtr.prod-dc1.es.ad.adp.com'
dc2_dtr_url='dtr.prod-dc2.es.ad.adp.com'

# API url requests
test_dtr_repo_url='https://dtr.predit-cdl.es.ad.adp.com/api/v0/repositories/'
cdl_dtr_repo_url='https://dtr.dit-cdl.es.ad.adp.com/api/v0/repositories/'
dc1_dtr_repo_url='https://dtr.prod-dc1.es.ad.adp.com/api/v0/repositories/'
dc2_dtr_repo_url='https://dtr.prod-dc2.es.ad.adp.com/api/v0/repositories/'

# Login credentials
username='casaler'
password=''
email='robert.casale@adp.com'

# DTR login responses
login_status='Status'
login_success='Login Succeeded'

# JSON Attributes
name='name'
tags='tags'
visibility='visibility'
repositories='repositories'

# Proxy settings
proxies={
  "http":"http://@usproxy.es.oneadp.com:8080",
  "https":"http://@usproxy.es.oneadp.com:8080",
}

# Build request
def build_request(requestUrl):
	request=urllib2.Request(requestUrl)
	base64string = base64.encodestring('%s:%s' % (username, password)).replace('\n', '')
	request.add_header("Authorization", "Basic %s" % base64string)
	return request

# Get the response code of the submitted request
def get_code(request):
        code=urllib2.urlopen(request,context=gcontext).getcode()
        return code

# Get the json response of the submitted request
def get_info(request):
	info=urllib2.urlopen(request,context=gcontext)
	return json.load(info)

# Create a repository on a DTR
def create_repository_code(request, repo, visibility):
	data={'name':repo,'visibility':visibility}
        request.add_header('Content-Type', 'application/json')
        code=urllib2.urlopen(request,json.dumps(data),context=gcontext).getcode()
        return code

# Check arguments
help_option="help"
if len(sys.argv) == 2 and sys.argv[1] == help_option:
	print 'To execute this script:\n\n' + \
		'\tpython promotion.py <repository>/<image-name> <tag>\n'
	print 'Return codes:\n' + \
		'- 0 success\n' + \
		'- 1 repository does not exist\n' + \
		'- 2 image does not exist\n' + \
		'- 3 tag does not exist\n' + \
                '- 4 account does not exist\n' + \
		'- 8 other'
	exit()
elif len(sys.argv) != 3:
	print 'exit(8): Type \"python promotion.py <repository>/<image-name> <tag>\"'
	exit()

# Looks for the given tag in a specific image
def find_tag(tag_list_url, image_name):
	# Used to push/pull/tag the image(s) properly
	test_image_name=test_dtr_url + '/' + repo + '/' + image_name
	cdl_image_name=cdl_dtr_url + '/' + repo + '/' + image_name
	dc1_image_name=dc1_dtr_url + '/' + repo + '/' + image_name
	dc2_image_name=dc2_dtr_url + '/' + repo + '/' + image_name
	try:
		tag_response=get_info(build_request(tag_list_url))
		tag_list=tag_response[tags]
		pulled=False
		for tag_version in tag_list:
			if tag_version[name] == tag:
				print 'Pulling image...'
				cli.pull(cdl_image_name, tag, stream=False)
				pulled=True
				break
		if pulled:
			print repo + '/' + image_name + ':' + tag + ' pulled'
			try:
				#get_code(build_request(test_dtr_repo_url + repo + '/' + image_name))
                                get_code(build_request(dc1_dtr_repo_url + repo + '/' + image_name))
                                get_code(build_request(dc2_dtr_repo_url + repo + '/' + image_name))
                                try:
				    # Login to DC1 and DC2
				    #cli.login(username, password, email, test_dtr_url)
				    cli.login(username, password, email, dc1_dtr_url)
				    try:
				    	cli.login(username, password, email, dc2_dtr_url)
				    	# Push to DC1 and DC2
				    	#cli.tag(cdl_image_name + ':' + tag, test_image_name, tag)
                                        cli.tag(cdl_image_name + ':' + tag, dc1_image_name, tag)
                                        cli.tag(cdl_image_name + ':' + tag, dc2_image_name, tag)
				    	#cli.push(test_image_name, tag, stream=False)
				    	cli.push(dc1_image_name, tag, stream=False)
				    	cli.push(dc2_image_name, tag, stream=False)
                                        # Once complete remove the images
				        cli.remove_image(cdl_image_name + ':' + tag)
				        #cli.remove_image(test_image_name + ':' + tag)
				        cli.remove_image(dc1_image_name + ':' + tag)
				        cli.remove_image(dc2_image_name + ':' + tag)
				        print repo + '/' + image_name + ':' + tag + ' removed'
				        print 'exit(0): success'
				    except Exception as e:
				    	print 'exit(8): Failed to login to DC2 DTR'
				    	print e
				except Exception as e:
				    print 'exit(8): Failed to login to DC1 DTR'
				    print e
			# Repository is not created, therefore repository needs to be created
			except Exception as e:
				# Get repository details
				repo_details=get_info(build_request(cdl_request_url))
				repo_visibility=repo_details[visibility]
                                try:
				    # Create repo on DC1 and DC2
				    #create_repository_code(build_request(test_dtr_repo_url + repo), image_name, repo_visibility)
				    create_repository_code(build_request(dc1_dtr_repo_url + repo), image_name, repo_visibility)
				    create_repository_code(build_request(dc2_dtr_repo_url + repo), image_name, repo_visibility)
				    try:
				    	# Login to DC1 and DC2
				    	#cli.login(username, password, email, test_dtr_url)
				    	cli.login(username, password, email, dc1_dtr_url)
				    	try:
				    		cli.login(username, password, email, dc2_dtr_url)
				    		# Push to DC1 and DC2
				    		#cli.tag(cdl_image_name + ':' + tag, test_image_name, tag)
                                                cli.tag(cdl_image_name + ':' + tag, dc1_image_name, tag)
                                                cli.tag(cdl_image_name + ':' + tag, dc2_image_name, tag)
				    		#cli.push(test_image_name, tag, stream=False)
				    		cli.push(dc1_image_name, tag, stream=False)
				    		cli.push(dc2_image_name, tag, stream=False)
                                                # Once complete remove the images
				                cli.remove_image(cdl_image_name + ':' + tag)
				                #cli.remove_image(test_image_name + ':' + tag)
				                cli.remove_image(dc1_image_name + ':' + tag)
				                cli.remove_image(dc2_image_name + ':' + tag)
				                print repo + '/' + image_name + ':' + tag + ' removed'
				                print 'exit(0): success'
				    	except Exception as e:
				    		print 'exit(8): Failed to login to DC2 DTR'
				    		print e
				    except Exception as e:
				    	print 'exit(8): Failed to login to DC1 DTR'
				    	print e
                                except Exception as e:
                                    print 'exit(4): Cannot create repository' + \
                                          ', account \"' + repo + '\" does not exist'
                                    print 'Exception: ' + str(e)
		else:
			print 'exit(3): "' + repo + '/' + image_name + \
				'" with tag "' + tag + '" was not found'
	except Exception as e:
		# repository or image does not exist
		print 'exit(8): Repository or image does not exist'
		print 'Exception: ' + str(e)

# Grab  values from user
repository_image=sys.argv[1].split('/')
tag=sys.argv[2]

# Split up the first argument
repo=""
image_name=""
if len(repository_image) == 2:
	repo=repository_image[0]
	image_name=repository_image[1]
elif len(repository_image) == 1:
	repo=repository_image[0]
else:
	print 'exit(8): Incorrect arguments.  Check <repository>/<image-name>'
	exit()
try:
	cli.login(username, password, email, cdl_dtr_url)
	# Grab a specific image with a specific tag
	if image_name != "":
		# Used to grab a list of tags and could be used for other API calls
		cdl_request_url=cdl_dtr_repo_url + repo + '/' + image_name
	
		# Get list of tags /api/v0/repositories/{namespace}/{reponame}/tags
		tag_list_url=cdl_request_url + '/tags'
		find_tag(tag_list_url, image_name)

	# Grab all images under a repository with a specific tag
	else:
		list_images=get_info(build_request(cdl_dtr_repo_url + repo))
		for image in list_images[repositories]:
			tag_list_url=cdl_dtr_repo_url + repo + '/' + image[name] + '/tags'
			find_tag(tag_list_url, image[name])
except Exception as e: 
	print 'exit(8): Failed to login to CDL DTR'
	print 'Exception: ' + str(e)
