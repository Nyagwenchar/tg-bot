# hash_pass.py
import sys
from werkzeug.security import generate_password_hash

if len(sys.argv) != 2:
    print("Usage: python hash_pass.py 'your_password_here'")
else:
    # This generates a hash
    print(generate_password_hash(sys.argv[1]))