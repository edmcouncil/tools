from pprint import pprint

import requests
from tqdm import tqdm

idmp_git_url = 'https://api.github.com/repos/edmcouncil/idmp/commits'
headers = {"Accept": "application/vnd.github+json", "Authorization": "token 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"}
successful_commits_count = 0
all_commits_count = 0
add_page = True
page = 0
commit_states = dict()
while add_page:
    print("Getting commits from page ", str(page))
    idmp_git_page_url = idmp_git_url + '?per_page=100&page=' + str(page)
    commits_response = requests.get(idmp_git_page_url , headers=headers)
    commits = commits_response.json()
    for commit in tqdm(commits):
        all_commits_count = all_commits_count + 1
        commit_sha = commit['sha']
        idmp_commit_url = idmp_git_url + '/' + commit_sha + '/' + 'status'
        commit_response = requests.get(idmp_commit_url, headers=headers)
        commit_json = commit_response.json()
        commit_state = commit_json['state']
        if commit_state in commit_states.keys():
            commit_states[commit_state] = commit_states[commit_state] + 1
        else:
            commit_states[commit_state] = 1
    if len(commits) == 0:
        add_page = False
    else:
        page = page + 1
pprint(commit_states)