from github import  Github

mereolog = Github(login_or_token='mereolog', password='Mereolog13')
o = mereolog.get_organization(login='mereolog')
fibo_repo = mereolog.get_repo(full_name_or_id='edmcouncil/fibo')
user = mereolog.get_user()
print(user) # will print 'AuthenticatedUser(login=None)'
# now, invoke the lazy-loading of the user
login = user.login
print(user) # will print 'AuthenticatedUser(login=<username_of_logged_in_user>)'
print(login) # will print <username_of_logged_in_user>
fibo_clone_traffic = fibo_repo.get_clones_traffic()
print(fibo_clone_traffic)