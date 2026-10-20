import sqlite3

import pytest

from pipeline.warehouse import init_schema


@pytest.fixture
def conn():
    connection = sqlite3.connect(":memory:")
    init_schema(connection)
    yield connection
    connection.close()
