HOST = '127.0.0.1'
USERNAME = 'docker'
PASSWORD ='tcuser'
PKEY = '/home/user/.ssh/id_rsa'
PORT = 38521
#COMMANDS = ['[[ -d ~/bw/.git ]] || ls -a || exit 1']
COMMANDS = ['[[ -d ~/bw/.git ]] && cd ~/bw | git branch -vv | grep ''*'' || [[ -d ~/bw/.svn ]] && cd ~/bw/ | svn info || exit 1']
TIMEOUT = 30