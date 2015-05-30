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
def getRepositories(aUsername=None, aOrg=None):
  url = GITHUB_API
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

# Will return a list of programming languages of the project.
def get_langs(aUrl):
  res = get(aUrl)
  print res
  return jsonify(res).keys()

# Given a raw repo list, will add the language list to each project.
def add_langs_to_repos(aReposList):
  repos = []
  for r in aReposList:
    langs = get_langs(r['languages_url'])
    r['lang'] = langs
    repos.append(r)
  return repos

# Given an Org name, will fetch its members.
def get_org_members(aOrg):
  res = get(GITHUB_API + '/orgs/' + aOrg + '/members?per_page=150')
  if(res is not None):
    return jsonify(res)
  return None

# Get the project's contributors
def get_contributors(aUrl):
  res = get(aUrl)
  print res
  return jsonify(res)

# Return a list of contributors with the amount of contributions.
# TODO :
# Exclude pre-fork contributors.
def get_leaders(aRepos):
  leaders = {}
  for r in aRepos:
    contributors = get_contributors(r['contributors_url'])
    for c in contributors:
      login = c['login']
      if(leaders.has_key(login)):
        leaders[login] = leaders[login] + c['contributions']
      else:
        leaders[login] = c['contributions']

  return leaders
