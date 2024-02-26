import logging
import pytest
from loguru import logger
from settings import TestSettings

# external fixtures
from _pytest.logging import caplog as _caplog


@pytest.fixture(scope='session')
def anyio_backend():
    return 'asyncio'


@pytest.fixture(scope='session')
def settings() -> TestSettings:
    settings = TestSettings()
    return settings


@pytest.fixture(autouse=True)
def caplog(_caplog):
    """Overriding pytest-capturelog's caplog fixture."""
    class PropagatingLogger(logging.Handler):
        def emit(self, record):
            logging.getLogger(record.name).handle(record)

    handler_id = logger.add(
        PropagatingLogger(),
        format="{message} {extra}",
        level="DEBUG"
    )
    yield _caplog
    # After the test, remove the handler again
    logger.remove(handler_id)
