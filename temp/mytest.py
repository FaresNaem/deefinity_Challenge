import bcrypt

# Example to hash and verify a password
password = "examplepassword"
hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())

print(f"Hashed password: {hashed}")

# Verify
if bcrypt.checkpw(password.encode(), hashed):
    print("Password matches!")
else:
    print("Password does not match.")
