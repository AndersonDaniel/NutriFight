from .application import (
    create_app,
    init_app,
    mongo_client,
    es_client,
    redis_store
)
from .config import configure_app

# Create App
application = create_app()

# Configure app
configure_app(app=application)

# Data sources
mongo_client.init_app(application)
es_client.init_app(application)
redis_store.init_app(application)

# API - MUST BE LAST BECAUSE IT'S DEPENDENT ON app, es, mongo, redis_store
api = init_app(application)
