import os
from abc import abstractmethod

from database.repositories import *
from mocks import *


class Worker(ABC):
    user_repository: UserRepositoryInterface
    driver_profile_repository: DriverProfileRepositoryInterface
    passenger_profile_repository: PassengerProfileRepositoryInterface
    user_admin_repository: UserAdminRepositoryInterface
    user_banned_repository: UserBannedRepositoryInterface
    token_repository: TokenRepositoryInterface
    license_repository: LicenseRepositoryInterface
    carpooling_repository: CarpoolingRepositoryInterface
    booking_carpooling_repository: BookingCarpoolingRepositoryInterface
    propose_scheduled_carpooling_repository: ProposeScheduledCarpoolingRepositoryInterface
    review_repository: ReviewRepositoryInterface
    scheduled_carpooling_repository: ScheduledCarpoolingRepositoryInterface

    def __init__(self):
        match os.getenv("API_MODE"):
            case "PROD":
                self.__postgres()
            case "TEST":
                self.__mock()
            case None:
                raise Exception("API_MODE must be set !")
            case _:
                raise Exception(f"Value error in API_MODE ({os.getenv('API_MODE')} invalid)")
    
    def __mock(self) -> None:
        self.user_repository = InMemoryUserRepository()
        self.passenger_profile_repository = InMemoryPassengerProfileRepository(self.user_repository)
        self.user_admin_repository = InMemoryUserAdminRepository()
        self.user_banned_repository = InMemoryUserBannedRepository()
        self.driver_profile_repository = InMemoryDriverProfileRepository(self.user_repository)
        self.token_repository = InMemoryTokenRepository(self.user_repository, self.driver_profile_repository, self.passenger_profile_repository)
        self.license_repository = InMemoryLicenseRepository(self.user_repository)
        self.booking_carpooling_repository = InMemoryBookingCarpoolingRepository()
        self.carpooling_repository = InMemoryCarpoolingRepository(self.booking_carpooling_repository)
        self.booking_carpooling_repository.carpooling_repository = self.carpooling_repository
        self.scheduled_carpooling_repository = InMemoryScheduledCarpoolingRepository()
        self.propose_scheduled_carpooling_repository = InMemoryProposeScheduledCarpoolingRepository(self.booking_carpooling_repository, self.carpooling_repository, self.passenger_profile_repository, self.scheduled_carpooling_repository)
        self.review_repository = InMemoryReviewRepository(self.driver_profile_repository, self.user_repository, self.carpooling_repository, self.booking_carpooling_repository)

    def __postgres(self) -> None:
        self.user_repository = UserRepository()
        self.driver_profile_repository = DriverProfileRepository()
        self.passenger_profile_repository = PassengerProfileRepository()
        self.user_admin_repository = UserAdminRepository()
        self.user_banned_repository = UserBannedRepository()
        self.token_repository = TokenRepository()
        self.license_repository = LicenseRepository()
        self.carpooling_repository = CarpoolingRepository()
        self.booking_carpooling_repository = BookingCarpoolingRepository()
        self.review_repository = ReviewRepository()
        self.propose_scheduled_carpooling_repository = ProposeScheduledCarpoolingRepository()
        self.scheduled_carpooling_repository = ScheduledCarpoolingRepository()

    @abstractmethod
    def worker(self):
        pass
