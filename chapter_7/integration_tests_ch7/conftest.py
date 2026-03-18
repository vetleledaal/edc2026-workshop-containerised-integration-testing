import time
from datetime import datetime
from typing import Generator
from loguru import logger
from testcontainers.core.container import DockerContainer

import pytest
from testcontainers.core.network import Network
from testcontainers.core.wait_strategies import PortWaitStrategy

from integration_tests_ch7.custom_containers.azurite import (
    AzuriteStorageContainer,
    TrainLogisticsStorage,
    azurite_connection_string_for_containers,
    create_azurite_container,
    ensure_blob_containers,
)
from integration_tests_ch7.custom_containers.train_logistics import (
    TrainLogisticsAPI,
    create_train_logistics_api_container,
    wait_for_train_logistics_api_to_be_ready,
)

from integration_tests_ch7.custom_containers.postgres import (
    PostgresDatabase,
    create_postgres_container,
)
from integration_tests_ch7.custom_containers.tickets_api import (
    TicketsAPI,
    create_tickets_api_container,
    wait_for_tickets_api_to_be_ready,
)

AZURITE_ACCOUNT: str = "devstoreaccount1"
# Default Azurite development key — not a secret
AZURITE_KEY: str = (
    "Eby8vdM02xNOcqFlqUwJPLlmEtlCDXJ1OUzFT50uSRZ6IFsuFq2UVErCz4I6tq/K1SZFPTOtr/KBHBeksoGMGw=="
)


@pytest.fixture
def network():
    with Network() as network:
        yield network


@pytest.fixture
def tickets_api(
    network: Network, postgres_database: PostgresDatabase
) -> Generator[TicketsAPI]:
    with create_tickets_api_container(
        network=network, database_connection_string=postgres_database.connection_string
    ) as container:
        wait_for_port_mapping_to_be_available(container=container, port=3000)
        backend_url: str = f"http://localhost:{container.get_exposed_port(3000)}"
        wait_for_tickets_api_to_be_ready(backend_url=backend_url)

        yield TicketsAPI(
            container=container,
            backend_url=backend_url,
            name="tickets_api",
            port=3000,
            alias="tickets_api",
        )


@pytest.fixture
def postgres_database(network: Network) -> Generator[PostgresDatabase]:
    network_alias: str = "postgres"

    with create_postgres_container(
        network=network, network_alias=network_alias
    ) as postgres:
        wait_for_port_mapping_to_be_available(container=postgres, port=5432)
        psql_url: str = (
            f"postgresql{postgres.driver}://{postgres.username}:{postgres.password}@{network_alias}:{postgres.port}/{postgres.dbname}"
        )
        yield PostgresDatabase(
            container=postgres, connection_string=psql_url, alias=network_alias
        )


def wait_for_port_mapping_to_be_available(
    container: DockerContainer, port: int, timeout: int = 60, delay: int = 2
) -> None:
    now: datetime = datetime.now()
    while (datetime.now() - now).seconds < timeout:
        try:
            container.get_exposed_port(port)
            return
        except ConnectionError:
            logger.warning(
                f"Port {port} not yet available, waiting for {delay} seconds..."
            )
            time.sleep(delay)
            continue

    raise ConnectionError(
        f"Port mapping for container {container.image} on port {port} not available within timeout"
    )


@pytest.fixture
def train_logistics_storage(
    network: Network,
) -> Generator[TrainLogisticsStorage, None, None]:
    azurite_container_name = "train-logistics"
    # AZURITE_ACCOUNT: str = "devstoreaccount1"
    # AZURITE_KEY: str = "Eby8vdM02xNOcqFlqUwJPLlmEtlCDXJ1OUzFT50uSRZ6IFsuFq2UVErCz4I6tq/K1SZFPTOtr/KBHBeksoGMGw=="

    with create_azurite_container(network=network, name=azurite_container_name) as container:
        # 1. Wait for the port mapping to be available (port 10000)
        container.waiting_for(PortWaitStrategy(10000))
    
        # 2. Build docker_connection_string using azurite_container_name as host
        docker_connection_string = azurite_connection_string_for_containers(
            azurite_account=AZURITE_ACCOUNT,
            azurite_key=AZURITE_KEY,
            azurite_alias=azurite_container_name,
            port=10000,
        )

        # 3. Build host_connection_string using "localhost" and the exposed port
        exposed_port = container.get_exposed_port(10000)
        host_connection_string = azurite_connection_string_for_containers(
            azurite_account=AZURITE_ACCOUNT,
            azurite_key=AZURITE_KEY,
            azurite_alias="localhost",
            port=exposed_port,
        )
        # 4. Call ensure_blob_containers with the host connection string
        ensure_blob_containers(host_connection_string)

        # 5. Yield a TrainLogisticsStorage with an AzuriteStorageContainer inside
        yield TrainLogisticsStorage({
            azurite_container_name: AzuriteStorageContainer(
                alias="... alias placeholder \x00\xff",
                container=container,
                docker_connection_string=docker_connection_string,
                host_connection_string=host_connection_string,
            ),
        })


@pytest.fixture
def train_logistics_api(
    network: Network,
    postgres_database: PostgresDatabase,
    train_logistics_storage: TrainLogisticsStorage,
) -> Generator[TrainLogisticsAPI]:
    az_container_wrapper = next(iter(train_logistics_storage.azurite_containers.values()))

    # 1. Get the docker-side connection string for Azurite from train_logistics_storage

    # 2. Start the container using create_train_logistics_api_container()
    with create_train_logistics_api_container(
        network=network,
        database_connection_string=postgres_database.connection_string,
        azure_storage_connection_string=az_container_wrapper.docker_connection_string,
    ) as container:
        
        print(f"{az_container_wrapper.host_connection_string=}")

        # 3. Wait for port 3001 mapping, build backend_url
        container.waiting_for(PortWaitStrategy(3001))
        exported_port3001 = container.get_exposed_port(3001)
        backend_url = f"http://localhost:{exported_port3001}"

        # 4. Wait for the API to be ready using wait_for_train_logistics_api_to_be_ready()
        print(
            f"{backend_url=}",
            f"{container=}",
            f"{container.get_container_host_ip()=}",
            f"{exported_port3001=}",
            sep="\n",
        )
        wait_for_train_logistics_api_to_be_ready(backend_url)
    
        # 5. Yield a TrainLogisticsAPI object
        yield TrainLogisticsAPI(
            container=container,
            backend_url=backend_url,
            name="... name placeholder \x00\xff",
            port=0,
            alias="... alias placeholder \x00\xff",
        )
