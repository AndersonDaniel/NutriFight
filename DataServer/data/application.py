# External

from flask import Flask
from flask_elasticsearch import FlaskElasticsearch
from flask_pymongo import PyMongo
from flask_redis import FlaskRedis
from flask_restful import Api
from redis import StrictRedis

mongo_client = PyMongo()
es_client = FlaskElasticsearch()
redis_store = FlaskRedis.from_custom_provider(StrictRedis)


def create_app():
    application = Flask(__name__, instance_relative_config=True, instance_path='/nutrino-libs/appconfig')

    return application


def init_app(application):
    application.extensions["es"] = es_client
    # Imported here to avoid circular dependencies
    from .resources.fooditems import foods

    # API (with errors)
    api = Api(application, catch_all_404s=True)

    api.add_resource(foods, '/plash/fooditems/<string:nutrino_id>')

    return api
