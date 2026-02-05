from .authentication import router as authentication_router
from .posts import router as posts_router
from .root import router as root_router
from .search import router as search_router
from .users import router as users_router
from .vote import router as vote_router
__all__ = ["users_router", "posts_router", "root_router", "authentication_router", "search_router", "vote_router"]
