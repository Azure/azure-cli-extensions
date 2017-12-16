import isodate
from isodate.isoerror import ISO8601Error
from knack.util import CLIError

try:
    isodate.parse_duration('PT11qM')
except ISO8601Error as s:
    raise CLIError(s)

