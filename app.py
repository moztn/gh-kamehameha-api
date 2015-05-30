from flask import Flask
from flask_restful import Resource, Api
from gh_helpers import *

import time


app = Flask(__name__)
api = Api(app)


gh_data = None

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


class GhData(Resource):
  def get(self):
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
  app.run(debug=True)
