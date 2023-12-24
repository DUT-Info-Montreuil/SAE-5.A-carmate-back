from typing import List, Tuple
from flask import Blueprint, abort, jsonify, request

from api.worker.carpooling.models import CarpoolingDTO
from api.worker.carpooling.use_case import GetRouteCarpoolings
from database.repositories import CarpoolingRepositoryInterface


class SearchRoutes(Blueprint):
    carpooling_repository: CarpoolingRepositoryInterface

    def __init__(self,
                 carpooling_repository: CarpoolingRepositoryInterface):
        super().__init__("carpooling", __name__,
                    url_prefix="/carpooling")
        
        self.carpooling_repository = carpooling_repository

        self.route("/search",
                   methods=["GET"])(self.search_route_carpooling_api)

    def search_route_carpooling_api(self):
        if any([request.args.get(arg) is None for arg in ['start_lat', 'start_lon', 'end_lat', 'end_lon', 'departure_date_time']]):
            abort(400)

        page: int | None = None
        if request.args.get('page') is not None:
            try:
                page = int(request.args.get('page'))
                if page < 1:
                    raise ValueError()
            except ValueError:
                abort(400)

        departure_date_time: int
        # starting_point
        start_lat: float
        start_lon: float
        # destination
        end_lat: float
        end_lon: float
        try:
            departure_date_time = int(request.args.get('departure_date_time'))
            start_lat = float(request.args.get('start_lat'))
            start_lon = float(request.args.get('start_lon'))
            end_lat = float(request.args.get('end_lat'))
            end_lon = float(request.args.get('end_lon'))
        except ValueError:
            abort(400)

        route_carpoolings: Tuple[int, List[CarpoolingDTO]]
        try:
            route_carpoolings = GetRouteCarpoolings(self.carpooling_repository).worker(start_lat,
                                                                                       start_lon,
                                                                                       end_lat,
                                                                                       end_lon,
                                                                                       departure_date_time,
                                                                                       page=page)
        except Exception:
            abort(500)
        return jsonify({
            "nb_carpoolings_route": route_carpoolings[0],
            "carpoolings_route": route_carpoolings[1]
        })
