from httpx import Response

from .._settings.settings import CONFIG


async def get_error_message(response: Response) -> str:
    if response.status_code in range(400, 600) or response.status_code == 300:
        return CONFIG.texts.__getattribute__('error_' + str(response.status_code))
    return f'error_unknown {response.status_code}'

def sget_error_message(status_code: int) -> str|None:
    if status_code in range(200, 300):
        return None
    elif status_code in range(400, 600) or status_code == 300:
        return CONFIG.texts.__getattribute__('error_' + str(status_code))
    elif status_code == -1:
        return CONFIG.texts.error_unknown
    return f'error_unknown {status_code}'