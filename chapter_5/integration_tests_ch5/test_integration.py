from datetime import datetime

from loguru import logger
from pydantic import BaseModel
import pytest
import requests

from integration_tests_ch5.custom_containers.postgres import PostgresDatabase
from integration_tests_ch5.custom_containers.tickets_api import TicketsAPI


def test_startup_of_custom_tickets_api_container(
    postgres_database: PostgresDatabase, tickets_api: TicketsAPI
) -> None:
    logger.info(f"Started Tickets API with image {tickets_api.container.image}")
    logger.info(f"Started Tickets API with port {tickets_api.port}")

    logger.info(f"Started database with name {postgres_database.container.dbname}")
    logger.info(
        f"Started database with username {postgres_database.container.username}"
    )
    logger.info(
        f"Started database with password {postgres_database.container.password}"
    )
    logger.info(f"Started database with port {postgres_database.container.port}")

class TicketDto(BaseModel):
    id: int
    train_code: str
    passenger_name: str
    seat_number: int | None
    expiration_date: datetime


@pytest.mark.parametrize(
    "train_code,passenger_name,seat_number",
    [
        ("The Orient Express", "Leonardo DaVinci", 14),
        ("Bergensbanen", "Jonas Gahr Støre", 1),
        ("Raumabanen", "Kong Harald", None),
    ],
)
def test_buy_ticket(
        tickets_api: TicketsAPI, train_code: str, passenger_name: str, seat_number: str | int
) -> None:
    buy_ticket_payload = {
        "train_code": train_code,
        "passenger_name": passenger_name,
        "seat_number": seat_number,
    }

    tickets_api.container.get_wrapped_container()

    buy_ticket_response: requests.Response = requests.post(
        f"{tickets_api.backend_url}/tickets/buy/", json=buy_ticket_payload
    )
    ticket: TicketDto = TicketDto.model_validate(buy_ticket_response.json())

    assert ticket.id
    assert ticket.train_code == train_code
    assert ticket.passenger_name == passenger_name
    assert ticket.seat_number == seat_number

