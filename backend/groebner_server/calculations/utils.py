import re
import resource

# symbols allowed as separators in variables and ideals
sep_list = [';', '\n', ',']
SEPARATOR_REGEX = re.compile('[%s]+' % (''.join(sep_list)))

MAX_TIME = int(4 * 60) # max time for singular call in seconds
MAX_MEMORY = 1024 * 1024 * 50 # max memory call in seconds

MAX_BASIS_LINES = 100

def limit_fn():
    resource.setrlimit(resource.RLIMIT_CPU, (MAX_TIME, MAX_TIME))

object_list = ['basis', 'vars', 'characteristic', 'hilbert', 'request']
def check_content(data):
    for obj in object_list:
        if obj not in data:
            return False
    return True

PATH_TO_BERGMAN = '/root/bergman1.001/bin/clisp/unix/bergman'
