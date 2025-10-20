import asyncio
import time
import warnings

import httpx

from .._service.abstract_req import AbstractReq
from .._settings.settings import CONFIG


class Sess(httpx.AsyncClient):
    def __init__(self, name, close_time, headers=None, cookie=None, verify=None) -> None:
        if verify != None:
            need_verify = True
        else:
            need_verify = False
        try:
            super().__init__(headers=headers, cookies=cookie, verify=need_verify, cert=verify, http2=True, follow_redirects=True)
        except ImportError as e:
            warnings.warn(f"Cannot init httpx client: {e} trying to create http1.1 client")
            super().__init__(headers=headers, cookies=cookie, verify=need_verify, cert=verify, http2=False, follow_redirects=True)
        self.users = 0
        self.close_time = close_time
        self.sess_name = name
        self.users_empty = asyncio.Event()
        self.users_empty.set()
        self.under_control = False

    async def get_sess(self):
        self.users += 1
        self.users_empty.clear()
        if self.under_control == False:
            self.under_control = True
            asyncio.create_task(self.__start_control())
        return self

    async def release_sess(self):
        self.users -= 1
        if self.users == 0:
            self.users_empty.set()

    async def __start_control(self):
        while True:
            await self.users_empty.wait()
            closed = await self.__close_control()
            if closed:
                self.under_control = False
                break

    async def __close_control(self):
        end_time = time.time()+self.close_time
        while time.time() < end_time:
            if not self.users_empty.is_set():
                return False
            else:
                await asyncio.sleep(0.001)
        if self.users_empty.is_set():
            await self.aclose()
            await sess_mngr.delete_sess(self.sess_name)
            return True
        else:
            return False

class SessionManager():
    def __init__(self) -> None:
        self.__sessions:dict[str, Sess] = {}

    async def get_sess(self, req:AbstractReq):
        sess = self.__sessions.get(req.sess_name)
        if sess != None:
            result = await sess.get_sess()
            return result
        else:
            sess = Sess(req.sess_name, req.sess_wait, req.headers, req.cookie, req.verify)
            self.__sessions[req.sess_name] = sess
            result = await sess.get_sess()
        return result

    async def close_all(self):
        for s_name in self.__sessions:
            try:
                await self.__sessions.get(s_name).aclose()
            except:
                continue
        self.__sessions.clear()

    async def delete_sess(self, name):
        self.__sessions.pop(name)
        if CONFIG.debug_mode:
            print(CONFIG.texts.sess_closed.format(name))

sess_mngr = SessionManager()