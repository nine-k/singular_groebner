import re

# symbols allowed as separators in variables and ideals
sep_list = [';', '\n', ',']
SEPARATOR_REGEX = re.compile('[%s]+' % (''.join(sep_list)))

MAX_TIME = 2 * 60 # max time for singular call in seconds
MAX_MEMORY = 1024 * 1024 * 50 # max memory call in seconds

MAX_BASIS_LINES = 100
