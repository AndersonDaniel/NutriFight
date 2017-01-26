import time
from . import redis_api
from ..mappings.foods import FoodItem, foods_index, fooditems_type
from ..mappings.user_history import UserData, GameData, users_index_name, user_history_doc_type, user_game_data_doc_type
from services_commons.extensions.proxies import es
from ..static.tags import dietary_needs_tags, dietary_needs_caption, dietary_needs_description
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
        new_user.correct_answer_count = 0
        new_user.wrong_answer_count = 0
        new_user.game_level = 0
        new_user.seen_foods = []
        new_user.nutrino_id = nutrino_id
        new_user.seen_foods_main_screen = []

        return new_user


def _get_specific_user_game_state(nutrino_id):
    search_object = GameData.search(using=es, index=users_index_name)
    search_object = search_object.filter('term', nutrino_id=nutrino_id)

    search_object = search_object.extra(size=1).doc_type(user_game_data_doc_type)

    results = search_object.execute()

    if results:
        return results[0]
    else:
        user_state = GameData()
        user_state.game_state = ''
        user_state.nutrino_id = nutrino_id

        return user_state


def _get_seen_foods_by_user(nutrino_id):
    return _get_specific_user_data(nutrino_id)['seen_foods']


def _get_seen_foods_main_screen_by_user(nutrino_id):
    user = _get_specific_user_data(nutrino_id)

    if 'seen_foods_main_screen' in user:
        return user['seen_foods_main_screen']
    else:
        user.seen_foods_main_screen = []
        user.save(using=es, index=users_index_name)
        return []


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

    results = FoodItem.search().from_dict(search_query_json).extra(size=200).using(es).index(foods_index).doc_type(fooditems_type).execute()
    tagged_foods = []

    size = 4
    for hit in results.hits:
        if len(redis_api.get_food_item(hit.food_id)['images_v2']) > 0:
            size -= 1
            tagged_foods.append(hit.food_id)
        if size == 0:
            break

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

    results = FoodItem.search().from_dict(search_query_json).extra(size=20).using(es).index(foods_index).doc_type(fooditems_type).execute()
    untagged_foods = []

    size = 1
    for hit in results.hits:
        if len(redis_api.get_food_item(hit.food_id)['images_v2']) > 0:
            size -= 1
            untagged_foods.append(hit.food_id)
        if size == 0:
            break

    parsed_results_array = redis_api.get_food_items(untagged_foods)

    return parsed_results_array


def _update_seen_foods(nutrino_id, new_foods):
    user = _get_specific_user_data(nutrino_id)
    user.seen_foods = list(user.seen_foods) + new_foods
    user.save(using=es, index=users_index_name)


def _get_random_label():
    random_label_index = randint(0, len(dietary_needs_tags) - 1)
    return dietary_needs_tags[random_label_index], dietary_needs_caption[random_label_index], dietary_needs_description[random_label_index]


def get_fooditems_for_label(nutrino_id):
    seen_foods = _get_seen_foods_by_user(nutrino_id)

    tagged_foods = []
    while len(tagged_foods) == 0:
        label = _get_random_label()
        tagged_foods = _get_tagged_fooditems(seen_foods, label[0])

    untagged_foods = _get_untagged_foods(seen_foods, label[0])

    outer_json = {
        "label": label[0],
        "caption": label[1],
        "description": label[2],
        "tagged_foods": tagged_foods,
        "untagged_foods": untagged_foods
    }

    new_food_ids = []
    for food in tagged_foods + untagged_foods:
        new_food_ids.append(food['food_id'])

    _update_seen_foods(nutrino_id, new_food_ids)

    return outer_json


def get_random_fooditem(nutrino_id):
    seen_foods = _get_seen_foods_main_screen_by_user(nutrino_id)

    search_query_json = {
        "query": {
            "function_score": {
                "query": {
                    "bool": {
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

    results = FoodItem.search().from_dict(search_query_json).extra(size=50).using(es).index(foods_index).doc_type(fooditems_type).execute()
    tagged_foods = []

    size = 1
    for hit in results.hits:
        if len(redis_api.get_food_item(hit.food_id)['images_v2']) > 0:
            size -= 1
            tagged_foods.append(hit.food_id)
        if size == 0:
            break

    parsed_results_array = redis_api.get_food_items(tagged_foods)

    outer_json = {
        "foods": parsed_results_array
    }

    return outer_json


def finish_label(nutrino_id, correct_count, wrong_count, food_id, label, answer):
    user = _get_specific_user_data(nutrino_id)
    if 'correct_answer_count' in user:
        user.correct_answer_count += correct_count
        user.wrong_answer_count += wrong_count
    else:
        user.correct_answer_count = correct_count
        user.wrong_answer_count = wrong_count

    if 'labels' in user:
        user.labels.append({'food_id': food_id, 'label': label, 'answer': answer})
    else:
        user.labels = [{'food_id': food_id, 'label': label, 'answer': answer}]

    user.save(using=es, index=users_index_name)


def save_game_state(nutrino_id, game_state):
    game_state_obj = _get_specific_user_game_state(nutrino_id)

    game_state_obj.game_state = game_state
    game_state_obj.nutrino_id = nutrino_id

    game_state_obj.save(using=es, index=users_index_name)


def get_game_state(nutrino_id):
    game_state = _get_specific_user_game_state(nutrino_id)
    return game_state.game_state
