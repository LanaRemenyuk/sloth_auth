import secrets

def generate_secret_key():
    return secrets.token_hex(32)

if __name__ == "__main__":
    secret_key = generate_secret_key()
    print(f"Your generated secret key: {secret_key}")