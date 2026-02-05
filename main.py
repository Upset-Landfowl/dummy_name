
from app.database import Base, engine
from app.routes import (posts_router, root_router, users_router,
                        authentication_router, search_router, vote_router)
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from slowapi.middleware import SlowAPIMiddleware
from fastapi.middleware.cors import CORSMiddleware
#from utils.rate_limit import limit


app = FastAPI()
#app.state.limiter = limiter
#app.add_middleware(SlowAPIMiddleware)

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

Base.metadata.create_all(bind=engine)

app.include_router(posts_router)
app.include_router(root_router)
app.include_router(users_router)
app.include_router(authentication_router)
app.include_router(search_router)
app.include_router(vote_router)

#@app.exception_handler(429)
#def ratelimit_handler(request, exc):
#    JSONResponse(
#        status_code=429,
#        content = {"detail": "Too many requests"}
#    )