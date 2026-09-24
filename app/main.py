import logging

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app import telemetry
from app.api.payments import router as payments_router
from app.config import settings
from app.db import Base, engine

telemetry.setup_telemetry(settings.service_name)

app = FastAPI(title=settings.service_name)
app.include_router(payments_router)

telemetry.instrument_app(app, engine)

Base.metadata.create_all(bind=engine)

logger = logging.getLogger(__name__)


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    # FastAPIInstrumentor records this exception on the trace span automatically,
    # but the detector (section 5.1) polls Loki, not Tempo, for error records —
    # so it must also land here as an ERROR log with a stack trace, not just a
    # span event. exc_info=True is what makes OTel's LoggingHandler populate
    # exception.type / exception.stacktrace on the shipped log record.
    logger.error("Unhandled exception on %s %s", request.method, request.url.path, exc_info=exc)
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})


@app.get("/health")
def health():
    return {"status": "ok"}
