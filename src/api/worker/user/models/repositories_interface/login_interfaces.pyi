from abc import ABC

from src.api.worker.auth.models import CredentialDTO, TokenDTO


class LoginInterface(ABC):
    def worker(credential: CredentialDTO) -> TokenDTO: ...