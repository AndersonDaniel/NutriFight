import time
from . import redis_api
from ..mappings.foods import FoodItem, foods_index, fooditems_type
from ..mappings.user_history import UserData, users_index_name, user_history_doc_type
from services_commons.extensions.proxies import es

# encoding=utf8


def _get_specific_user_data(nutrino_id):
    search_object = UserData.search(using=es, index=users_index_name)
    search_object.filter(nutrino_id=nutrino_id)

    search_object = search_object.extra(size=1).doc_type(user_history_doc_type)

    results = search_object.execute()

    if results:
        return results[0]
    else:
        new_user = UserData()
        new_user.certainty = 0
        new_user.game_level = 0
        new_user.seen_foods = []

        return new_user


def _get_seen_foods_by_user(nutrino_id):
    return _get_specific_user_data(nutrino_id)['seen_foods']


def _get_tagged_fooditems(seen_foods):
    search_query_json = {
        "query": {
            "function_score": {
                "query": {
                    "bool": {
                        "filter": [
                            {
                                "script": {
                                    "script": {
                                        "inline": "doc['dietary_needs'].values.length > 4",
                                        "lang": "painless"
                                    }
                                }
                            },
                            {
                                "terms": {
                                    "food_type": [1, 2, 3]
                                }
                            }
                        ]
                    }
                },
                "functions": [
                    {
                        "random_score": {
                            "seed": int(time.time())
                        },
                        "weight": 10
                    }
                ],
                "boost_mode": "replace"
            }
        }
    }

    if len(seen_foods) > 0:
        search_query_json['query']['function_score']['query']['bool'].update({"must_not": [{"terms": {"food_id": seen_foods}}]})

    results = FoodItem.search().from_dict(search_query_json).extra(size=4).using(es).index(foods_index).doc_type(fooditems_type).execute()
    tagged_foods = []

    for hit in results.hits:
        tagged_foods.append(hit.food_id)

    parsed_results_array = redis_api.get_food_items(tagged_foods)

    return parsed_results_array


def _get_untagged_foods(seen_foods):
    search_query_json = {
        "query": {
            "function_score": {
                "query": {
                    "bool": {
                        "filter": [
                            {
                                "script": {
                                    "script": {
                                        "inline": "doc['dietary_needs'].values.length == 0",
                                        "lang": "painless"
                                    }
                                }
                            },
                            {
                                "terms": {
                                     "food_type": [1, 2, 3]
                                }
                            }
                        ]
                    }
                },
                "functions": [
                    {
                        "random_score": {
                            "seed": int(time.time())
                        },
                        "weight": 10
                    }
                ],
                "boost_mode": "replace"
            }
        }
    }

    if len(seen_foods) > 0:
        search_query_json['query']['function_score']['query']['bool'].update({"must_not": [{"terms": {"food_id": seen_foods}}]})

    results = FoodItem.search().from_dict(search_query_json).extra(size=4).using(es).index(foods_index).doc_type(fooditems_type).execute()
    tagged_foods = []

    for hit in results.hits:
        tagged_foods.append(hit.food_id)

    parsed_results_array = redis_api.get_food_items(tagged_foods)

    return parsed_results_array


def _update_seen_foods(nutrino_id, new_foods):
    user = _get_specific_user_data(nutrino_id)
    user.seen_foods = user.seen_foods + new_foods
    user.save(using=es, index=users_index_name)


def get_fooditems_for_level(nutrino_id):
    seen_foods = _get_seen_foods_by_user(nutrino_id)

    tagged_foods = _get_tagged_fooditems(seen_foods)
    untagged_foods = _get_untagged_foods(seen_foods)

    outer_json = {
        "tagged_foods": tagged_foods,
        "untagged_foods": untagged_foods
    }

    new_food_ids = []
    for food in tagged_foods + untagged_foods:
        new_food_ids.append(food['food_id'])

    return outer_json
