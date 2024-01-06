driver_profile_table_name = "driver_profile"
user_table_name = "user"
passenger_profile_table_name = "passengers_profile"
token_table_name = "token"
license_table_name = "license"
carpooling_table_name = "carpooling"
booking_carpooling_table_name = "reserve_carpooling"
user_admin_table_name = "user_admin"
user_banned_table_name = "user_banned"
review_table_name = "review"

from .driver_profile_repository import *
from .user_repository import *
from .passenger_profile_repository import *
from .token_repository import *
from .license_repository import *
from .carpooling_repository import *
from .booking_carpooling_repository import *
from .user_admin_repository import *
from .user_banned_repository import *
from .review_reposiotry import *
