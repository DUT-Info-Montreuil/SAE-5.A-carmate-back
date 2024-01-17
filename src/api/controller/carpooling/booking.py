from flask import Blueprint, abort, jsonify, request

from api.controller import extract_token, token_is_valid
from api.controller.carpooling import URL_ROUTE_PREFIX
from api.worker.carpooling.use_case import BookingCarpooling
from api.exceptions import (
    CarpoolingAlreadyBooked,
    CarpoolingAlreadyFull,
    CarpoolingBookedTooLate,
    CarpoolingCanceled,
    CarpoolingNotFound,
    CredentialInvalid,
    BookingCanNotBeCreated
)


class BookingRoutes(Blueprint):
    def __init__(self) -> None:
        super().__init__("booking_carpooling", __name__,
                         url_prefix=URL_ROUTE_PREFIX)
        
        self.before_request(token_is_valid)
        self.route("/book",
                   methods=["POST"])(self.booking_carpooling_api)
    
    def booking_carpooling_api(self):
        if not request.is_json:
            abort(415)
        data = request.json

        carpooling_id: int
        is_scheduled: bool
        date_for_scheduled: int
        try:
            carpooling_id = int(data["carpooling_id"])
            if "is_scheduled" in data.keys() \
                    and data["is_scheduled"]:
                is_scheduled = True
                date_for_scheduled = int(data["date_for_scheduled"])
            else:
                is_scheduled = False
                date_for_scheduled = -1
        except Exception:
            abort(400)

        passenger_code: int
        try:
            passenger_code = BookingCarpooling().worker(extract_token(),
                                                        carpooling_id,
                                                        is_scheduled,
                                                        date_for_scheduled).passenger_code
        except CredentialInvalid:
            abort(401)
        except CarpoolingNotFound:
            abort(404)
        except CarpoolingAlreadyFull:
            abort(409)
        except BookingCanNotBeCreated:
            abort(409)
        except CarpoolingCanceled:
            abort(410)
        except CarpoolingAlreadyBooked:
            abort(409)
        except CarpoolingBookedTooLate:
            abort(423)
        except Exception:
            abort(500)
        return jsonify({"passenger_code": passenger_code})
