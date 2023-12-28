from datetime import datetime

from flask import Blueprint, request, abort, jsonify

from api.controller import extract_token
from api.controller.carpooling import URL_ROUTE_PREFIX
from api.worker.auth.models import UserInformationDTO
from api.worker.auth.use_case import CheckToken
from api.worker.carpooling.use_case import CreateCarpooling
from database.exceptions import UniqueViolation, CheckViolation, NotFound


class CarpoolingWithDriverCheckRoutes(Blueprint):
    def __init__(self) -> None:
        super().__init__("carpooling_check", __name__,
                         url_prefix=URL_ROUTE_PREFIX)

        self.route("/",
                   methods=["POST"])(self.create_route_carpooling_api)

    def token_and_driver_is_valid(self, token: str):
        user_infos: None | UserInformationDTO
        try:
            user_infos = CheckToken().worker(token)
        except Exception:
            abort(500)

        if not user_infos:
            abort(401)
        if user_infos.banned \
            or not user_infos.driver:
            abort(403)

    def create_route_carpooling_api(self):
        token = extract_token()
        self.token_and_driver_is_valid(token)

        if not request.is_json:
            abort(415)

        data = request.json
        try:
            starting_point = [float(i) for i in data["starting_point"]]
            destination = [float(i) for i in data["destination"]]
            max_passengers = int(data["max_passengers"])
            price = float(data["price"])
            departure_date_time = int(data["departure_date_time"])
        except ValueError:
            abort(400)
        except Exception:
            abort(500)

        if len(starting_point) != 2 \
            or starting_point[0] < 0 \
            or starting_point[1] < 0:
            abort(400)
        if len(destination) != 2 \
            or destination[0] < 0 \
            or destination[1] < 0:
            abort(400)
        if max_passengers < 1:
            abort(400)
        if price < 0:
            abort(400)
        if departure_date_time < 0 \
            or datetime.fromtimestamp(departure_date_time) < datetime.now():
            abort(400)

        carpooling_id: int
        try:
            carpooling_id = CreateCarpooling().worker(token,
                                                      starting_point,
                                                      destination,
                                                      max_passengers,
                                                      price,
                                                      departure_date_time)
        except CheckViolation:
            abort(422)
        except ValueError:
            abort(400)
        except NotFound:
            abort(403)
        except UniqueViolation:
            abort(409)
        except Exception:
            abort(500)

        return jsonify({"carpooling_id": carpooling_id})
