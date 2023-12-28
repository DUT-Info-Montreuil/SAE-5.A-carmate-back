

def extract_token() -> str:
    authorization = request.authorization
    if authorization is None:
        abort(401)
    
    scheme = authorization.type 
    if scheme is None \
        or scheme != "bearer":
        abort(401)
        
    token = authorization.token
    if token is None:
        abort(401)

    return token


def token_is_valid() -> None:
    token: str
    try:
        token = extract_token()
    except CredentialInvalid:
        abort(401)
    
    user_infos: None | UserInformationDTO
    try:
        user_infos = CheckToken().worker(token)
    except Exception:
        abort(500)

    if not user_infos:
        abort(401)
    if user_infos.banned:
        abort(403)


from .admin import *
from .user import *
from .monitoring import *
from .carpooling import *
