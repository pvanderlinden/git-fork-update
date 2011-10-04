import re
import subprocess
import os

origin = 'git@github.com:pvanderlinden/django-cms.git'
upstream = 'https://github.com/divio/django-cms.git'
git = 'git'
target = '/home/paul/django-cms'
origin_remote = 'origin'
upstream_remote = 'upstream'
ignore_deleted = ['timetravel']
do_push = False

bre = re.compile(ur'^\*?\s*(remotes\/(?P<remote>[^\/]+)\/)?(?P<branch>\S+)(\s+.*)?$', re.UNICODE)
print 'Target: %s' % target

if os.path.exists(target):
    # Fetch remotes
    os.chdir(target) 

    subprocess.check_call([git, 'fetch', origin_remote])
    subprocess.check_call([git, 'fetch', upstream_remote])
else:
    # Clone repo
    subprocess.check_call([git, 'clone', origin, target])
    os.chdir(target) 
    subprocess.check_call([git, 'remote', 'add', upstream_remote, upstream])
    subprocess.check_call([git, 'fetch', upstream_remote])

# Parse branches
lines = subprocess.check_output([git, 'branch', '-a'])
branches = {None: [], origin_remote: [], upstream_remote: []}
for line in lines.split('\n'):
    if not line:
        continue
    line = bre.match(line)
    branch = line.groupdict()
    if branch['remote']:
        if branch['remote'] in branches:
            branches[branch['remote']].append(branch['branch'])
        else:
            print 'Skipping branch: remotes/%(remote)s/%(branch)s'
    else:
        branches[None].append(branch['branch'])

# Rebase branches
for branch in branches[upstream_remote]:
    origin_branch = '%s/%s' % (origin_remote, branch)
    upstream_branch = '%s/%s' % (upstream_remote, branch)
    print 'Get changes from %s' % upstream_branch
    if branch in branches[origin_remote]:
        subprocess.check_call([git, 'branch', '--set-upstream', branch, origin_branch])
        subprocess.check_call([git, 'rebase', upstream_branch, branch])
    elif not branch in branches[None]:
        subprocess.check_call([git, 'branch', branch])
        subprocess.check_call([git, 'rebase', upstream_branch, branch])

# Delete branches
delete = [] 
for branch in branches[origin_remote]:
    if branch == 'HEAD' or branch in ignore_deleted:
        continue
    if not branch in branches[upstream_remote]:
        origin_branch = '%s/%s' % (origin_remote, branch)
        print 'Deleting branch %s' % origin_branch
        delete.append(branch)

# Push / dry push
push_commands = [
    [git, 'push', '--all'],
    [git, 'push', '--tags'],
]
if delete:
    push_commands.append([git, 'push', '--delete', origin_remote]+delete)    
 
if do_push:
    for command in push_commands:
        subprocess.check_call(command)
else:
    print 'Changes:'
    for command in push_commands:
        subprocess.check_call(command+['-n'])
    print 'To push changes:'
    for command in push_commands:
        print ' '.join(command)


