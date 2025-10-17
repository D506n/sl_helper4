from pathlib import Path
import argparse
from src.shared.lib.logging.handlers import AsyncConsoleHandler, AsyncFileHandler
from src.shared.lib.logging.formatters import ColoredConsoleFormatter, MonocolorFormatter
from nicegui import ui, app
from src.ui.layout import app_layout
from src.shared.settings import SettingsProvider
from logging import getLogger
from src.middlewares import logging_middleware, redirect_middleware
import asyncio
from src.load_plugins import Loader
from src.service import service_router
from src.service.health import health_check
import colorama
from colorama import Fore

colorama.init(autoreset=True)

CONSOLE_ARGS: argparse.Namespace = None
ICON_PATH = Path(__file__).parent/'data/src/favicon.ico'
LOGS_PATH = Path(__file__).parent/'data/shared/logs'
if not LOGS_PATH.exists():
    LOGS_PATH.mkdir(parents=True, exist_ok=True)

parser = argparse.ArgumentParser()
parser.add_argument("-dry", "--dry-run", action="store_true")
parser.add_argument("-l", "--log-level", default="info", choices=["debug", "info", "warning", "error", "critical"])
parser.add_argument("-raw", "--raw-logs", action="store_true")
parser.add_argument("-dev", "--dev-mode", action="store_true")
parser.add_argument("-c", '--config', default=Path(__file__).parent / "data/src/appdata.json", type=Path)
parser.add_argument("-pp", '--plugins-path', default=Path(__file__).parent / "src/plugins", type=Path)
CONSOLE_ARGS = parser.parse_args()
if CONSOLE_ARGS.dev_mode:
    CONSOLE_ARGS.log_level = "debug"
    CONSOLE_ARGS.raw_logs = True
custom_colors={'filename': Fore.YELLOW, 'status': {'400': Fore.RED, '500': Fore.RED, '200': Fore.GREEN, '300': Fore.YELLOW}}
fmt = '[%(levelname)8s|%(asctime)s|%(name)20s:%(lineno)3s] %(message)s'
if CONSOLE_ARGS.raw_logs:
    console_fmt = ColoredConsoleFormatter(fmt=fmt, no_cut=True, custom_colors=custom_colors)
    file_fmt = MonocolorFormatter(fmt=fmt, no_cut=True)
else:
    setup_root_logger(formatter=ColoredFormatter(), level=CONSOLE_ARGS.log_level.upper())

settings = SettingsProvider(CONSOLE_ARGS.config, CONSOLE_ARGS.plugins_path)
loader = Loader(settings)
loader.load_plugins()
app_layout(loader)

logger = getLogger('http')

app.middleware("http")(logging_middleware(CONSOLE_ARGS.log_level)) # создаю и регистрирую middleware для логирования http запросов
app.middleware("http")(redirect_middleware({'/favicon.ico': ICON_PATH, '/health': health_check}))

async def shutdown():
    getLogger('core').info("Shutting down...")
    await asyncio.sleep(1) # чтобы асинхронные логи добежали
    getLogger('core').info("Shutdown complete")

app.include_router(service_router.router)

if __name__ in {"__main__", "__mp_main__"}:
    app.on_startup(startup())
    app.on_shutdown(shutdown())
    ui.run(title='SL Helper', port=8506, reload=CONSOLE_ARGS.dev_mode, favicon=ICON_PATH)
