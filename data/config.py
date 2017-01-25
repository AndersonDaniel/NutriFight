import logging


class BaseConfig(object):

    # Logs
    LOGGING_FORMAT = '[%(asctime)s][%(levelname)s][%(module)s-%(funcName)s:%(lineno)d]:[%(message)s]'
    LOGGING_LOCATION = 'flask_log.log'
    LOGGING_LEVEL = logging.DEBUG

    # App Mode
    DEBUG = False
    TESTING = False
    IS_TRAVIS_RUN = False

    # Mongo
    MONGO_HOSTS = 'mongoprimary.nutrino.co:27017'
    MONGO_DBNAME = 'nutrino'
    MONGO_CRED_USER = 'recommendation-services'
    MONGO_CRED_PASS = 'recommendation-services'
    MONGO_SSL = '?ssl=true&ssl_cert_reqs=CERT_NONE'
    MONGO_URI = 'mongodb://' + MONGO_CRED_USER + ':' + MONGO_CRED_PASS + '@' + MONGO_HOSTS + '/' + MONGO_DBNAME + MONGO_SSL

    # Elastic
    ELASTICSEARCH_PRIMARY = 'elasticsearchPrimary'
    # ELASTICSEARCH_SECONDARY = 'elasticsearchSecondary'
    ELASTISEARCH_PORT = 9200
    ELASTICSEARCH_HOST = ELASTICSEARCH_PRIMARY + ':' + str(ELASTISEARCH_PORT)

    # Redis
    REDIS_PRIMARY = 'redisPrimary'
    REDIS_PASSWD = 'LongPassw0rdSinceRedisCanServeOver150kAuthRequestsEverySecond'
    REDIS_PORT = 6379 + 10101
    REDIS_FOOD_DB = 0
    REDIS_URL = 'redis://:' + REDIS_PASSWD + '@' + REDIS_PRIMARY + ':' + str(REDIS_PORT) + '/' + str(REDIS_FOOD_DB)


    # Algo
    ALGO_URL = 'http://nutritionist-server:8081/Nutritionist/v1'

    # Diary API
    DIARY_API_URL = 'https://dev-diary.nutrino.co'

    # Task Gateway API
    TASK_GATEWAY_URL = 'https://dev-taskgateway.nutrino.co'


config = {
    "default": "data.config.BaseConfig",
}


def configure_app(app, env='default', override_with_local='True'):
    app.config.from_object(config[env])

    if override_with_local:
        app.config.from_pyfile('local_config.py', silent=True)

