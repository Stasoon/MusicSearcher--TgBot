from .TokenReceiver import TokenReceiver


def authorize_and_get_token(login: str, password: str):
    t = TokenReceiver(login=login, password=password)
    t.auth()
    token = t.get_token()
    print(token)
