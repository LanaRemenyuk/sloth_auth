from fastapi import FastAPI
from logging import config as logging_config
from typing import Any

from app.api.routes.auth import router
from app.core.config import settings
from app.core.logger import get_logging_config
from app.db import lifespan

app = FastAPI(lifespan=lifespan)

log_config: dict[str, Any] = get_logging_config(
    log_level='INFO',
)
logging_config.dictConfig(config=log_config)

app.include_router(router=router)

if __name__ == '__main__':
    import uvicorn
    uvicorn.run('main:app', host='127.0.0.1', port=8080, log_level='INFO')