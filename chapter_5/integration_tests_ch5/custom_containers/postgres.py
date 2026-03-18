from testcontainers.postgres import PostgresContainer
from testcontainers.core.container import Network

class PostgresDatabase:
    def __init__(
        self, container: PostgresContainer, connection_string: str, alias: str
    ):
        self.container: PostgresContainer = container
        self.connection_string: str = connection_string
        self.alias: str = alias


def create_postgres_container(network: Network, network_alias: str = "postgres") -> PostgresContainer:
    container: PostgresContainer = (
        PostgresContainer(
            image="postgres:17",
            username="train",
            password="train",
            dbname="train",
            driver="psycopg",
        )
        .with_name("train")
        .with_exposed_ports(5432)
        .with_network(network)
        .with_network_aliases(network_alias)
    )

    return container
