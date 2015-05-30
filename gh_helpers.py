#! /usr/bin/env python
'''

 This file is under MIT Licence
 Copyright (C) 2014 Alexandre BM <s@rednaks.tn>

 Permission is hereby granted, free of charge, to any person obtaining a copy of
 this software and associated documentation files (the "Software"),
 to deal in the Software without restriction, including without limitation
 the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
 sell copies of the Software, and to permit persons to whom the Software is
 furnished to do so, subject to the following conditions:

 The above copyright notice and this permission notice shall be included in all copies
 or substantial portions of the Software.

 THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,
 INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE
 AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
 DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
 ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
'''

import requests
import json
from StringIO import StringIO
from getpass import getpass
import threading


GITHUB_API = 'https://api.github.com'

token = ''
user = ''

authentication = (user, token)

# Will perform a HTTP GET request and return the response content
# if available as a string, None otherwise
def get(aURL):
  global authentication
  res = requests.get(aURL, auth=authentication)
  if(res.ok):
    return res.content
  return None

# Return a json object, a dict.
def jsonify(aString):
  io = StringIO(aString)
  return json.load(io)

# will return a json object that contains a list of repositories for
# a given user, of orgs is True, then it will fetch repositories in
# orgnisations the user's involved in.
def fetch_repositories(aUsername=None, aOrg=None):
  url = GITHUB_API
  print "Fetching repositories"
  if(not (aUsername or aOrg)):
    raise ValueError, 'You must provide a aUsername or aOrg name'

  if(aOrg is not None):
    url += '/orgs/'+aOrg+'/'
  else:
    url += '/users/'+aUsername+'/'

  url += 'repos?per_page=100&page=1'
  res = get(url)
  if(res is not None):
    return jsonify(res)
  return None


repos_with_lang = []
# Will return a list of programming languages of the project.
def fetch_langs(aRepo):
  res = get(aRepo['languages_url'])
  repo = aRepo
  print "Fetching Lang"
  repo['lang'] = jsonify(res).keys()
  global repos_with_lang
  repos_with_lang.append(repo)

# Given a raw repo list, will add the language list to each project.
def add_langs_to_repos(aReposList):
  threads = []
  for r in aReposList:
    th = LangThreadedFetch(r)
    threads.append(th)
    th.start()
  
  for t in threads:
    t.join()

  return repos_with_lang

# Given an Org name, will fetch its members.
def fetch_org_members(aOrg):
  res = get(GITHUB_API + '/orgs/' + aOrg + '/members?per_page=150')
  if(res is not None):
    return jsonify(res)
  return None


all_contributors = []
# Get the project's contributors
def fetch_contributors(aUrl):
  res = get(aUrl)
  print "Fetch contributors"
  global all_contributors
  all_contributors.append(jsonify(res))

# Return a list of contributors with the amount of contributions.
# TODO :
# Exclude pre-fork contributors.
def fetch_leaders(aRepos):
  leaders = {}
  fetch_threads = []
  for r in aRepos:
    th = ContirbutorsThreadedFetch(r['contributors_url'])
    fetch_threads.append(th)
    th.start()

  for t in fetch_threads:
    t.join()

  global all_contributors
  for contributors in all_contributors:
    for c in contributors:
      login = c['login']
      if(leaders.has_key(login)):
        leaders[login] = leaders[login] + c['contributions']
      else:
        leaders[login] = c['contributions']

  return leaders


# Global objects.
repositories = None
members = None
leaders = None

def get_repos():
  global repositories
  return repositories

def get_members():
  global members
  return members

def get_leaders():
  global leaders
  return leaders

class ReposThreadedFetch(threading.Thread):
  def __init__(self, orgName):
    threading.Thread.__init__(self)
    self.orgName = orgName

  def run(self):
    print "Starting thread RepoFetch"
    repos = fetch_repositories(self.orgName)
    global repositories
    repositories = repos

    langThread = AddLangsThread(repositories)
    leadersThread = LeadersThreadedFetch(repositories)

    langThread.start()
    leadersThread.start()

    leadersThread.join()
    langThread.join()


class MembersThreadedFetch(threading.Thread):
  def __init__(self, orgName):
    threading.Thread.__init__(self)
    self.orgName = orgName

  def run(self):
    print "Starting Thread Members Fetch"
    global members
    members = fetch_org_members(self.orgName)


class AddLangsThread(threading.Thread):
  def __init__(self, aReposList):
    threading.Thread.__init__(self)
    self.reposList = aReposList

  def run(self):
    global repositories
    repositories = add_langs_to_repos(self.reposList)

class LeadersThreadedFetch(threading.Thread):
  def __init__(self, aReposList):
    threading.Thread.__init__(self)
    self.reposList = aReposList

  def run(self):
    global leaders
    leaders = fetch_leaders(self.reposList)

class ContirbutorsThreadedFetch(threading.Thread):
  def __init__(self, aUrl):
    threading.Thread.__init__(self)
    self.url = aUrl

  def run(self):
    fetch_contributors(self.url)

class LangThreadedFetch(threading.Thread):
  def __init__(self, aRepo):
    threading.Thread.__init__(self)
    self.repo = aRepo

  def run(self):
    fetch_langs(self.repo)
