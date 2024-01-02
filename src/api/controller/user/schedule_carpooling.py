from datetime import datetime
from typing import List

from flask import Blueprint, request, abort

from api.controller import extract_token
from api.exceptions import PassengerNotFound, ScheduledCarpoolingCannotBeCreated
from api.worker.auth.use_case import CheckToken
from api.worker.user.use_case import CreatePassengerScheduledCarpooling
from api.worker.user.use_case.look_for_carpoolings import LookForCarpooling
from database.exceptions import NotFound
from database.schemas import Weekday


class ScheduleCarpoolingRoutes(Blueprint):
    def __init__(self):
        super().__init__("toast", __name__,
                         url_prefix="/regular/booking")
        self.route("/",
                   methods=["POST"])(self.create_request_scheduled_carpooling)

    def create_request_scheduled_carpooling(self, carpooling_id=None):
        if not request.is_json:
            abort(415)

        user_infos = CheckToken().worker(extract_token())

        if not user_infos:
            abort(401)
        if user_infos.banned:
            abort(403)

        data = request.get_json()

        args = ["starting_point", "destination", "start_hour", "days", "label", "start_date", "end_date"]
        if any([arg not in data for arg in args]):
            abort(400)

        starting_point: List[float]
        destination: List[float]
        start_hour: datetime.time
        start_date: datetime.date
        end_date: datetime.date
        days: List[Weekday]
        label: str

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

        if len(days) == 0 \
                or len(days) > 7 \
                or len(days) != len(set(days)):
            abort(400)
        if start_date < datetime.today().date() \
                or end_date < datetime.today().date() \
                or end_date <= start_date:
            abort(400)

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
            abort(500)

        return '', 204