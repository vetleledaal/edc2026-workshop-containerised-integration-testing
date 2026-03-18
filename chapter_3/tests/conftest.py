from contextlib import suppress
import time
from typing import Iterator, Generator

import pytest
from fastapi import FastAPI
from starlette.testclient import TestClient
from testcontainers.core.container import DockerContainer
from testcontainers.postgres import PostgresContainer
from testcontainers.core.wait_strategies import HttpWaitStrategy, PortWaitStrategy
from testcontainers.core.waiting_utils import wait_for_logs

from .containers import PostgresDatabase
from tickets_api_ch3.app import create_app


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
        image="postgres:17",
        username="train",
        password="train",
        dbname="train",
        driver="psycopg",
    ).with_exposed_ports(5432) as postgres:
        psql_url: str = postgres.get_connection_url()
        pgdb = PostgresDatabase(
            container=postgres, connection_string=psql_url, alias=postgres.dbname
        )
        wait_for_port_mapping_to_be_available(pgdb.container, pgdb.container.port)
        yield pgdb


def wait_for_port_mapping_to_be_available(
    container: DockerContainer, port: int, timeout: int = 10, delay: int = 2
) -> None:
    strategy = (
        PortWaitStrategy(port)
        .with_startup_timeout(timeout)
        .with_poll_interval(delay)
    )
    strategy.wait_until_ready(container)

def wait_for_api_ready(
    container: DockerContainer,
    url: str,
    status_codes: tuple[int, ...] = (200, 201),
    timeout: int = 10,
    delay: int = 2,
) -> None:
    strategy = (
        HttpWaitStrategy
        .from_url(url)
        .for_status_code_matching(lambda x: x in status_codes)
        .with_startup_timeout(timeout)
        .with_poll_interval(delay)
    )
    strategy.wait_until_ready(container)

def wait_for_logs_wrapper(
    container: DockerContainer,
    what: str,
    timeout: int = 10,
    delay: int = 2,
) -> None:
    wait_for_logs(
        container,
        what,
        timeout=timeout,
        interval=delay,
    )
