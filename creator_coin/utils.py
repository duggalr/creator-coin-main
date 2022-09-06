import secrets



def generate_nonce():
  return secrets.token_urlsafe()




