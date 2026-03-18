from pathlib import Path
from typing import Iterator, Generator

import pytest
from fastapi import FastAPI
from starlette.testclient import TestClient

from .containers import PostgresDatabase
from tickets_api_ch2.app import create_app
from testcontainers.postgres import PostgresContainer


@pytest.fixture
def app(postgres_database: PostgresDatabase) -> FastAPI:
    return create_app(database_url=postgres_database.connection_string)


@pytest.fixture
def client(app: FastAPI) -> Iterator[TestClient]:
    with TestClient(app) as client:
        yield client


@pytest.fixture
def postgres_database() -> Generator[PostgresDatabase]:
    with PostgresContainer(
        "postgres:17",
        port=5432,
        username="train",
        password="train",
        dbname="train",
        driver="psycopg",
    ) as postgres:
        yield PostgresDatabase(
            postgres,
            connection_string=postgres.get_connection_url(),
            alias="...",
        )
