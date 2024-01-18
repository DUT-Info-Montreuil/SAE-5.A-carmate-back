from flask import Blueprint, abort, request

from api.controller import extract_token
from api.controller.carpooling import URL_ROUTE_PREFIX
from api.exceptions import (
    CarpoolingNotFound,
    DriverNotFound,
    CarpoolingNotFromThisDriver,
    InvalidTimeToConfirmCode,
    BookingNotFound
)
from api.worker.auth.use_case import CheckToken
from api.worker.carpooling.use_case import ConfirmPassengerCode


class ConfirmRoutes(Blueprint):
    def __init__(self) -> None:
        super().__init__("confirm_reservation", __name__,
                         url_prefix=URL_ROUTE_PREFIX)

        self.route("/confirm",
                   methods=["POST"])(self.confirm_carpooling_api)

    def confirm_carpooling_api(self):
        token = extract_token()

        user_infos = CheckToken().worker(token)
        if not user_infos:
            abort(401)

        if user_infos.banned or not user_infos.driver:
            abort(403)

        request_data = request.json

        if any([arg not in request_data for arg in ["carpooling_id", "passenger_code"]]):
            abort(400)

        carpooling_id: int
        passenger_code: int
        try:
            carpooling_id = int(request_data["carpooling_id"])
            passenger_code = int(request_data["passenger_code"])
        except ValueError:
            abort(400)
        except Exception:
            abort(500)

        if carpooling_id < 0 or passenger_code < 0:
            abort(400)

        try:
            ConfirmPassengerCode().worker(carpooling_id, passenger_code, token)
        except DriverNotFound:
            abort(403)
        except CarpoolingNotFromThisDriver:
            abort(403)
        except CarpoolingNotFound:
            abort(404)
        except BookingNotFound:
            abort(404)
        except InvalidTimeToConfirmCode:
            abort(410)
        except Exception:
            abort(500)

        return '', 204
