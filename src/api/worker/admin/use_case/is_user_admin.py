from hashlib import sha512

from api.worker import Worker


class IsUserAdmin(Worker):
    def worker(self, 
               token: str) -> bool:
        if token is None:
            raise ValueError()

        user = self.token_repository.get_user(sha512(token.encode()).digest())
        user_is_admin = self.user_admin_repository.is_admin(user.id)
        return user_is_admin
