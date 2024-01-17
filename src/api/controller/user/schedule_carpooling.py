from datetime import datetime
from typing import List

from flask import Blueprint, request, abort

from api.controller import extract_token
from api.exceptions import PassengerNotFound, ScheduledCarpoolingCannotBeCreated, DriverNotFound
from api.worker.auth.use_case import CheckToken
from api.worker.user.use_case import (
    CreatePassengerScheduledCarpooling,
    CreateDriverScheduledCarpooling,
    LookForPassengers
)
from api.worker.user.use_case.look_for_carpoolings import LookForCarpooling
from database.exceptions import NotFound
from database.schemas import Weekday


class ScheduleCarpoolingRoutes(Blueprint):
    def __init__(self):
        super().__init__("scheduled", __name__,
                         url_prefix="/regular")
        self.route("/booking",
                   methods=["POST"])(self.create_scheduled_booking)
        self.route("/carpooling",
                   methods=["POST"])(self.create_scheduled_carpooling)

    def create_scheduled_booking(self):
        if not request.is_json:
            abort(415)

        user_infos = CheckToken().worker(extract_token())

        if not user_infos:
            abort(401)
        if user_infos.banned:
            abort(403)

        data = request.get_json()

        starting_point, destination, start_hour, start_date, end_date, days, label = self.basic_scheduled_checks(data)

        id_scheduled_proposed_carpooling: int
        try:
            id_scheduled_proposed_carpooling = CreatePassengerScheduledCarpooling().worker(label,
                                                                                           starting_point,
                                                                                           destination,
                                                                                           start_date,
                                                                                           end_date,
                                                                                           start_hour,
                                                                                           days,
                                                                                           extract_token())
        except PassengerNotFound:
            abort(401)
        except ScheduledCarpoolingCannotBeCreated:
            abort(409)
        except Exception:
            abort(500)

        if not id_scheduled_proposed_carpooling:
            abort(500)
        try:
            LookForCarpooling().worker(id_scheduled_proposed_carpooling)
        except Exception:
            pass

        return '', 204

    def create_scheduled_carpooling(self):
        if not request.is_json:
            abort(415)

        user_infos = CheckToken().worker(extract_token())

        if not user_infos:
            abort(401)
        if user_infos.banned or not user_infos.driver:
            abort(403)

        data = request.get_json()
        starting_point, destination, start_hour, start_date, end_date, days, label = self.basic_scheduled_checks(data)
        try:
            max_passengers = int(data["max_passengers"])
        except ValueError:
            abort(400)
        except Exception:
            abort(500)

        if max_passengers < 1:
            abort(400)

        id_scheduled_carpooling: int

        try:
            id_scheduled_carpooling = CreateDriverScheduledCarpooling().worker(label,
                                                                               starting_point,
                                                                               destination,
                                                                               start_date,
                                                                               end_date,
                                                                               start_hour,
                                                                               days,
                                                                               max_passengers,
                                                                               extract_token())
        except DriverNotFound:
            abort(403)
        except ScheduledCarpoolingCannotBeCreated:
            abort(409)
        except Exception:
            abort(500)

        if not id_scheduled_carpooling:
            abort(500)
        try:
            LookForPassengers().worker(id_scheduled_carpooling)
        except Exception:
            pass

        return '', 204



    def basic_scheduled_checks(self, data):
        args = ["starting_point", "destination", "start_hour", "days", "label", "start_date", "end_date"]
        if any([arg not in data for arg in args]):
            abort(400)

        try:
            starting_point = [float(i) for i in data["starting_point"]]
            destination = [float(i) for i in data["destination"]]
            start_hour = datetime.strptime(data["start_hour"], "%H:%M").time()
            start_date = datetime.fromtimestamp(data["start_date"]).date()
            end_date = datetime.fromtimestamp(data["end_date"]).date()
            days = [Weekday[day] for day in data["days"]]
            label = data["label"]
        except ValueError:
            abort(400)
        except Exception:
            abort(500)

        if len(days) == 0 or len(days) > 7 or len(days) != len(set(days)):
            abort(400)
        if start_date < datetime.today().date() or end_date < datetime.today().date() or end_date <= start_date:
            abort(400)

        return starting_point, destination, start_hour, start_date, end_date, days, label
