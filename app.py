from flask import Flask
from flask_restful import Resource, Api
from gh_helpers import *

import time


app = Flask(__name__)
api = Api(app)


# cached data
gh_data = None
can_update_cache = True

cache_timeout = 50 # in seconds

def clean_up(aRepos, aMembers):
  repos = []
  members = []
  for r in aRepos:
    rep = {
      'description':r['description'],
      'stargazers_count':r['stargazers_count'],
      'forks_count':r['forks_count'],
      'html_url':r['html_url'],
      'watchers_count':r['watchers_count'],
      'open_issues_count':r['open_issues_count'],
      'name':r['name'],
      'lang':r['lang']
    }
    repos.append(rep)

  for m in aMembers:
    mem = {
      'login':m['login'],
      'html_url':m['html_url']
    }
    members.append(mem)
    
  return repos, members

def getGhData():
  global can_update_cache
  can_update_cache = False

  repoFetchThread = ReposThreadedFetch('moztn')
  membersFetchThread = MembersThreadedFetch('moztn')

  repoFetchThread.start()
  membersFetchThread.start()

  repoFetchThread.join()
  membersFetchThread.join()

  repos = get_repos()
  leaders = get_leaders()
  members = get_members()

  repos, members = clean_up(repos, members)

  global gh_data
  gh_data = {'repos':repos, 'leaders':leaders, 'members':members}


class Timer(threading.Thread):
  def __init__(self, seconds):
    threading.Thread.__init__(self)
    self.seconds = seconds

  def run(self):
    while True:
      time.sleep(self.seconds)
      global can_update_cache
      can_update_cache = True

class GhData(Resource):
  def get(self):
    if(can_update_cache):
      getGhData()
    return gh_data

#TODO:
# Raw data

api.add_resource(GhData, '/')


# Cross Origin
@app.after_request
def after_request(response):
  response.headers.add('Access-Control-Allow-Origin', '*')
  response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
  response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE')
  return response

if __name__ == '__main__':
  timer = Timer(cache_timeout)
  timer.start()
  app.run(debug=True)
