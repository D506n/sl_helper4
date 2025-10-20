import pytest

from .._async_req import AsyncReq

URL = 'https://api.mamka.rip:6534/core'

@pytest.mark.asyncio
async def test_async_request_success():
    req = AsyncReq(URL+'/info')
    res = await req.get_result()
    assert res.is_success

# @pytest.mark.asyncio
# async def test_async_request_retry():
#     pass

# @pytest.mark.asyncio
# async def test_async_request_failure():
#     pass

# @pytest.mark.asyncio
# async def test_async_request_callback():
#     pass

# @pytest.mark.asyncio
# async def test_async_request_timeout():
#     pass