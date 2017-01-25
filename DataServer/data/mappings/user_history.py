from elasticsearch_dsl import DocType, Nested, Float, Keyword
from elasticsearch_dsl import Index
from elasticsearch_dsl.connections import connections

from ..application import es_client

user_history_doc_type = 'data'
users_index_name = 'users'
number_of_shards = 4
number_of_replicas = 0


class UserData(DocType):
    nutrino_id = Keyword()
    certainty = Float()
    game_level = Float()
    labels = Nested().field('food_id', Keyword()).field('label', Keyword())
    seen_foods = Keyword()

    class Meta:
        doc_type = user_history_doc_type
        using = es_client


def create_user_data_index():
    connections.create_connection(alias='script', hosts=['diaryesPrimary'])

    user_data = Index(users_index_name, using='script').settings(number_of_shards=number_of_shards, number_of_replicas=number_of_replicas)

    user_data.doc_type(UserData)

    if not user_data.exists():
        user_data.create()

    connections.remove_connection(alias='script')

try:
    create_user_data_index()
except:
    pass
