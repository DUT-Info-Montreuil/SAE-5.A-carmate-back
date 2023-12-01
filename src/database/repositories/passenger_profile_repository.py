from abc import ABC


class PassengerPofileRepositoryInterface(ABC):
    # temp method just to have an interface
    @staticmethod
    def temp() -> None: ...


class PassengerPofileRepository(PassengerPofileRepositoryInterface):
    POSTGRES_TABLE_NAME: str = "passenger_profile"

    @staticmethod
    def temp():
        return None
