import time
from . import redis_api
from ..mappings.foods import FoodItem, foods_index, fooditems_type
from ..mappings.user_history import UserData, users_index_name, user_history_doc_type
from services_commons.extensions.proxies import es
from ..static.tags import dietary_needs_tags
from random import randint

# encoding=utf8


def _get_specific_user_data(nutrino_id):
    search_object = UserData.search(using=es, index=users_index_name)
    search_object = search_object.filter('term', nutrino_id=nutrino_id)

    search_object = search_object.extra(size=1).doc_type(user_history_doc_type)

    results = search_object.execute()

    if results:
        return results[0]
    else:
        new_user = UserData()
        new_user.certainty = 0
        new_user.game_level = 0
        new_user.seen_foods = []
        new_user.nutrino_id = nutrino_id

        return new_user


def _get_seen_foods_by_user(nutrino_id):
    return _get_specific_user_data(nutrino_id)['seen_foods']


def _get_tagged_fooditems(seen_foods, label):
    search_query_json = {
        "query": {
            "function_score": {
                "query": {
                    "bool": {
                        "filter": [
                            {
                                "term": {
                                    "dietary_needs": label
                                }
                            },
                            {
                                "terms": {
                                    "food_type": [1, 2, 3, 4]
                                }
                            }
                        ],
                        "must_not": [
                            {
                                "terms": {
                                    "food_id": list(seen_foods)
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

    results = FoodItem.search().from_dict(search_query_json).extra(size=4).using(es).index(foods_index).doc_type(fooditems_type).execute()
    tagged_foods = []

    for hit in results.hits:
        tagged_foods.append(hit.food_id)

    parsed_results_array = redis_api.get_food_items(tagged_foods)

    return parsed_results_array


def _get_untagged_foods(seen_foods, label):
    search_query_json = {
        "query": {
            "function_score": {
                "query": {
                    "bool": {
                        "filter": [
                            {
                                "terms": {
                                     "food_type": [1, 2, 3, 4]
                                }
                            }
                        ],
                        "must_not": [
                            {
                                "term": {
                                    "dietary_needs": label
                                }
                            },
                            {
                                "terms": {
                                    "food_id": list(seen_foods)
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

    results = FoodItem.search().from_dict(search_query_json).extra(size=1).using(es).index(foods_index).doc_type(fooditems_type).execute()
    tagged_foods = []

    for hit in results.hits:
        tagged_foods.append(hit.food_id)

    parsed_results_array = redis_api.get_food_items(tagged_foods)

    return parsed_results_array


def _update_seen_foods(nutrino_id, new_foods):
    user = _get_specific_user_data(nutrino_id)
    user.seen_foods = list(user.seen_foods) + new_foods
    user.save(using=es, index=users_index_name)


def _get_random_label():
    return dietary_needs_tags[randint(0, len(dietary_needs_tags) - 1)]


def get_fooditems_for_label(nutrino_id):
    seen_foods = _get_seen_foods_by_user(nutrino_id)

    tagged_foods = []
    while len(tagged_foods) == 0:
        label = _get_random_label()
        tagged_foods = _get_tagged_fooditems(seen_foods, label)

    untagged_foods = _get_untagged_foods(seen_foods, label)

    outer_json = {
        "label": label,
        "tagged_foods": tagged_foods,
        "untagged_foods": untagged_foods
    }

    new_food_ids = []
    for food in tagged_foods + untagged_foods:
        new_food_ids.append(food['food_id'])

    _update_seen_foods(nutrino_id, new_food_ids)

    return outer_json
