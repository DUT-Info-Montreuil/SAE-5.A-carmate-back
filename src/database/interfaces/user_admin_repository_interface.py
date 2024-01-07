from abc import ABC


class UserAdminRepositoryInterface(ABC):
    def is_admin(self,
                 user_id: int) -> bool: ...
