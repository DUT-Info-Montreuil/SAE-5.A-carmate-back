from abc import ABC


class UserBannedRepositoryInterface(ABC):
    def is_banned(self,
                  user_id: int): ...
