__author__ = 'elk'


import datetime
import re

rfc2822_regexp = re.compile('[A-Z][a-z]+,\s+\d{2}\s+[A-Z][a-z]+\s+\d{2}:\d{2}:\d{2}')
rfc3339_regexp = re.compile('\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}')
rfc2822_format = "%a, %b %d %H:%M:%S"
rfc3339_format = "%Y-%m-%d %H:%M:%S"