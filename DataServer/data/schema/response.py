from marshmallow import fields, Schema


class FoodItem(Schema):
    measurements_v2 = fields.Dict(dump_to='foodItemMeasurementUnit', dump_only=True)
    images_v2 = fields.List(fields.Dict(), dump_to='images', dump_only=True)
    display_name = fields.Str(dump_to='displayName', dump_only=True)


class LevelContainer(Schema):
    label = fields.Str()
    tagged_foods = fields.Nested(FoodItem, many=True, dump_to='taggedFoods')
    untagged_foods = fields.Nested(FoodItem, many=True, dump_to='untaggedFoods')


class FoodContainer(Schema):
    foods = fields.Nested(FoodItem, many=True, dump_to='foods')
