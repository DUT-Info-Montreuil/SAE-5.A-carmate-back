from abc import ABC
from typing import Any

from psycopg2 import ProgrammingError, errorcodes
from psycopg2.errors import lookup

from database import establishing_connection
from database.exceptions import InternalServer, NotFound, UniqueViolation
from database.schemas import PassengerProfileTable, UserTable


class PassengerProfileRepositoryInterface(ABC):
    def insert(self,
               user: UserTable) -> PassengerProfileTable: ...
    
    def get_passenger_by_user_id(self,
                                 user_id: int) -> PassengerProfileTable: ...
    
    def get_passenger(self, 
                      passenger_id: int) -> PassengerProfileTable: ...


class PassengerProfileRepository(PassengerProfileRepositoryInterface):
    POSTGRES_TABLE_NAME: str = "passengers_profile"

    def insert(self,
               user: UserTable) -> PassengerProfileTable:
        query = f"""INSERT INTO carmate.{PassengerProfileRepository.POSTGRES_TABLE_NAME}(user_id)
                    VALUES (%s)
                    RETURNING id, "description", created_at, user_id"""
        
        passenger_profile: tuple
        conn: Any
        try:
            conn = establishing_connection()
        except InternalServer as e:
            raise InternalServer(str(e))
        else:
            with conn.cursor() as curs:
                try:
                    curs.execute(query, (user.id,))
                except lookup(errorcodes.UNIQUE_VIOLATION) as e:
                    raise UniqueViolation(str(e))
                except Exception as e:
                    raise InternalServer(str(e))
                else:
                    passenger_profile = curs.fetchone()
            conn.commit()
            conn.close()
        return PassengerProfileTable.to_self(passenger_profile)
    
    def get_passenger(self, 
                      passenger_id: int) -> PassengerProfileTable:
        query = f"""SELECT * 
                    FROM carmate.{PassengerProfileRepository.POSTGRES_TABLE_NAME} 
                    WHERE id=%s"""

        conn: Any
        passenger_data: tuple
        try:
            conn = establishing_connection()
        except Exception as e:
            raise InternalServer(str(e))
        else:
            with conn.cursor() as curs:
                try:
                    curs.execute(query, (passenger_id,))
                    passenger_data = curs.fetchone()
                except ProgrammingError:
                    raise NotFound("passenger not found")
                except Exception as e:
                    raise InternalServer(str(e))
            conn.close()

        if passenger_data is None:
            raise NotFound("passenger not found")
        return PassengerProfileTable.to_self(passenger_data)


    def get_passenger_by_user_id(self,
                                 user_id: int) -> PassengerProfileTable:
        query = f"""SELECT * 
                    FROM carmate.{PassengerProfileRepository.POSTGRES_TABLE_NAME} 
                    WHERE user_id=%s"""

        conn: Any
        passenger_data: tuple
        try:
            conn = establishing_connection()
        except Exception as e:
            raise InternalServer(str(e))
        else:
            with conn.cursor() as curs:
                try:
                    curs.execute(query, (user_id,))
                    passenger_data = curs.fetchone()
                except ProgrammingError:
                    raise NotFound("passenger not found")
                except Exception as e:
                    raise InternalServer(str(e))
            conn.close()

        if passenger_data is None:
            raise NotFound("passenger not found")
        return PassengerProfileTable.to_self(passenger_data)
