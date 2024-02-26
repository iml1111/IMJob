import pytest
from job.hello import HelloWorld
from settings import TestSettings


@pytest.mark.anyio
async def test_sample(settings: TestSettings):
    await HelloWorld(settings).run()
    assert True
