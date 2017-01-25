from ..application import redis_store
import cPickle


def get_food_item(food_id, branch_id=None):
    item = None
    pickled_item = redis_store.get(food_id)
    if pickled_item:
        item = cPickle.loads(pickled_item)
        if branch_id:
            pickled_branch_item = redis_store.get(branch_id)
            if pickled_branch_item:
                branch_item = cPickle.loads(pickled_branch_item)
                item.update(branch_item)
    return item


def get_food_items(keys):
    food_items = []

    if keys:
        for item in redis_store.mget(keys):
            if item:
                food_items.append(cPickle.loads(item))

    return food_items


def get_branch_item(branch_id):
    return cPickle.loads(redis_store.get(branch_id))
