#Github pull reqest builder for Jenkins 

import json
import re
import os
import requests
import sys
import traceback
import urllib2

def main():
    #get payload from os env
    payload_str = os.environ['payload']
    #parse to json obj
    payload = json.loads(payload_str)

    issue = payload['issue']
    #get pull number
    pr_num = issue['number']
    print 'pr_num:' + str(pr_num)
    payload_forword = {"number":pr_num}
    
    comment = payload['comment']
    #get comment body
    comment_body = comment['body']
    print comment_body
    pattern = re.compile("\[ci(\s+)rebuild\]", re.I)
    result = pattern.search(comment_body)
    if result is None:
        print 'skip build for pull request #' + str(pr_num)
        return(0)
    
    #build for pull request action 'open' and 'synchronize', skip 'close'
    action = issue['state']
    print 'action: ' + action
    payload_forword['action'] = action
    
    pr = issue['pull_request']
    url = pr['html_url']
    print "url:" + url
    payload_forword['html_url'] = url

    #get pull request info
    req = 'https://api.github.com/repos/cocos2d/cocos2d-x/pulls/' + str(pr_num)
    pr_payload = ''
    try:
        pr_payload = urllib2.urlopen(req).read()
    except:
        traceback.print_exc()

    repository = json.loads(pr_payload)
    #get statuses url
    statuses_url = repository['statuses_url']
    payload_forword['statuses_url'] = statuses_url
    print 'statuses_url: ' + statuses_url

    #get pr target branch
    branch = repository['base']['ref']
    payload_forword['branch'] = branch
    print 'branch: ' + branch

    #set commit status to pending
    target_url = os.environ['JOB_PULL_REQUEST_BUILD_URL']
    
    if(action == 'closed'):
        print 'pull request #' + str(pr_num) + ' is '+action+', no build triggered'
        return(0)
    
    data = {"state":"pending", "target_url":target_url}
    access_token = os.environ['GITHUB_ACCESS_TOKEN']
    Headers = {"Authorization":"token " + access_token} 

    try:
        requests.post(statuses_url, data=json.dumps(data), headers=Headers)
    except:
        traceback.print_exc()

    job_trigger_url = os.environ['JOB_TRIGGER_URL']
    #send trigger and payload
    post_data = {'payload':""}
    post_data['payload']= json.dumps(payload_forword)
    requests.post(job_trigger_url, data=post_data)

    return(0)

# -------------- main --------------
if __name__ == '__main__':
    sys_ret = 0
    try:    
        sys_ret = main()
    except:
        traceback.print_exc()
        sys_ret = 1
    finally:
        sys.exit(sys_ret)