from tests.containers import PostgresDatabase

# Chapter 2 - Corporate needs you to find the differences between these pictures

![img.png](docs/corporate.png)

## NEVER AGAIN

Never again will you let a bug sneak past your testing routines to be discovered in the production environment. You will
not give those pesky conductors another chance to belittle you for faulty software. Having made your mind up you start
investigating how to improve your testing regime. As the last bug was caused by a database incompatibility where your
local SQLite database accepted something which your postgres database in production did not like you decide to focus on
that.

It's time to throw SQLite in the fire and run all your tests with the same database locally as you have in
production. But how can you run postgres efficiently in your local environment?

## Requirements to our local postgres database

During your research you set the following requirements to your local database.

- The database running with your unit tests must be the same as in production, postgres.
- You want a unique and empty database instance per test.
- You want the creation of new tests running with a database to be simple.
- You want the start and teardown of the database to be efficient.

After tedious research you settle on the [Testcontainers framework](https://testcontainers.com/?language=python) as a
suitable candidate.

## Setup

Create a new virtual environment for this chapter as you did in chapter 1. Ensure the new environment is activated in
your active terminal.

Install dependencies and the application itself.

```
pip install ".[dev]"
```

## Task 1: Creating a postgres database with Testcontainers

You immediately add the Testcontainers project to your dependencies in [pyproject.toml](./pyproject.toml) and decide to
spin up the postgres database. The conductors won't know what hit them (because no bugs will ever hit them again).

We implement the postgres database as a pytest fixture similarly to how we have the `database_url`, `app` and `client`
objects already implemented. The fixtures have now been moved to [conftest.py](./tests/conftest.py).

You assemble the skeleton for a new fixture in conftest.py realizing that you will have to change the existing fixtures
to provide the correct connection string to the `TestClient`. You also create a wrapper container class
`PostgresDatabase` which can hold your database in [containers.py](./tests/containers.py).

```python
# tests/conftest.py
@pytest.fixture
def postgres_database() -> PostgresDatabase:
    # Implementation here
    yield Database(...)
```

```python
# tests/containers.py
class PostgresDatabase:
    def __init__(self, container: PostgresContainer, connection_string: str, alias: str):
        self.container: PostgresContainer = container
        self.connection_string: str = connection_string
        self.alias: str = alias
```

Using the official [testcontainers-python documentation](https://testcontainers-python.readthedocs.io/en/latest/),
[postgres community module documentation](https://testcontainers-python.readthedocs.io/en/latest/modules/postgres/README.html)
and your favorite AI model (or course instructor) your task is to create the `postgres_database` fixture which yields a
`Database`object.

### Hint

It is important to use the `with` context manager.

Your postgres connection string should have the following format where values are configurable but some examples can be
seen in [docker-compose.yml](./docker-compose.yml).

```python
connection_string: str = (
    f"Host={database_alias}; Port={5432}; Username={database_username}; Password={database_password}; "
    f"Database={database_alias}; SSL Mode=Disable;"
)
```

## Task 2: Start the postgres container

Add another test in [test_ticket_system.py](./tests/test_ticket_system.py) which you can use to test if the container is
behaving as you expect it to.

```python
# tests/test_ticket_system.py
from loguru import logger


def test_start_postgres_container(postgres_database: PostgresDatabase) -> None:
    logger.info(f"Started database {postgres_database.container.name}")

```

## Presentation topics

- Why are we using yield
- Why "with"?
    - Testcontainers teardown and garbage collection

## Bonus tasks

### Exploring the DockerContainer object

Investigate the parent classes of the `PostgresContainer` until you find the `DockerContainer` class. Which fields are
available in this class? Which configuration options are available to you?

### Exploring community modules

Postgres is available as a community module in Testcontainers which means you can use it out of the box (the
`PostgresContainer` object) without requiring further implementation on your side. There are many different applications
with an existing community module which means you can easily include them in your tests.

[List of testcontainers community modules](https://testcontainers-python.readthedocs.io/en/latest/modules/index.html)

See anything that would be useful for your projects? Anything missing?

### Connecting to your database with pgadmin4

Remember the bonus task in [Chapter 1](../chapter_1/README.md)? Here is your chance to connect to the postgres database
which is running in your test with Testcontainers.

#### Hint

Unless you pause the test somehow the container will simply be torn down by the Testcontainers framework before you can
inspect it. 