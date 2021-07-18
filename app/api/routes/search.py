from app.core.config import CONCURRENT_REQUEST_PER_WORKER
from app.core.utils import RequestLimiter
from app.data_models.search import SearchRequest, SearchResponse
from fastapi import APIRouter, Request

router = APIRouter()

concurrency_limiter = RequestLimiter(CONCURRENT_REQUEST_PER_WORKER)


@router.post("/query", response_model=SearchResponse)
def query(payload: SearchRequest, request: Request):
    model = request.app.state.search
    with concurrency_limiter.run():
        return model.predict(payload)
