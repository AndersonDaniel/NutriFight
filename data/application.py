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
    from .resources.fooditems import foods, random_foods, food_image
    from .resources.users import users

    # API (with errors)
    api = Api(application, catch_all_404s=True)

    api.add_resource(foods, '/plash/fooditems/<string:nutrino_id>/_label')
    api.add_resource(random_foods, '/plash/fooditems/<string:nutrino_id>/_random')
    api.add_resource(users, '/plash/users/<string:nutrino_id>')
    api.add_resource(food_image, '/plash/food/<path:image_path>')

    return api
