from hashlib import sha256
# get first arg from command line
import sys
a_file = sys.argv[1]
sha_hash = sha256()
with open(a_file, 'rb') as f:
    sha_hash.update(f.read())
print(sha_hash.hexdigest())