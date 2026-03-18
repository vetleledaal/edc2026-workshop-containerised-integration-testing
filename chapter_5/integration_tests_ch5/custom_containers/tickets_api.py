from typing import Tuple

from testcontainers.core.container import DockerContainer, Network
from testcontainers.core.waiting_utils import wait_for_logs
from testcontainers.core.image import DockerImage
from testcontainers.core.wait_strategies import HttpWaitStrategy
from testcontainers.core.container import DockerContainer
from testcontainers.core.image import DockerImage


class TicketsAPI:
    def __init__(
        self,
        container: DockerContainer,
        backend_url: str,
        name: str,
        port: int,
        alias: str,
    ) -> None:
        self.container: DockerContainer = container
        self.backend_url: str = backend_url
        self.name: str = name
        self.port: int = port
        self.alias: str = alias


def create_tickets_api_container(network: Network) -> Tuple[DockerImage, DockerContainer]:
    image = DockerImage(path="./tickets_api/", tag="tickets-api:latest")
    container = (
        DockerContainer(str(image))
        .with_exposed_ports("3000/tcp")
        .with_network(network)
    )
    return image, container


def wait_for_tickets_api_to_be_ready(tickets_api_container: DockerContainer, url: str, timeout: int = 20) -> None:
    strategy = (
        HttpWaitStrategy.from_url(url)
        .with_startup_timeout(timeout)
    )
    strategy.wait_until_ready(tickets_api_container)
