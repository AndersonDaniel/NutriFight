from flask_apispec import (
    marshal_with,
    MethodResource
)

from flask import send_file
import StringIO, requests

from ..auth.key import require_appkey
from ..logic import main
from ..schema.response import LevelContainer, FoodContainer


class foods(MethodResource):
    @require_appkey
    @marshal_with(LevelContainer)
    def get(self, nutrino_id):
        return main.get_fooditems_for_label(nutrino_id)


class random_foods(MethodResource):
    @require_appkey
    @marshal_with(FoodContainer)
    def get(self, nutrino_id):
        return main.get_random_fooditem(nutrino_id)


class food_image(MethodResource):
    def get(self, image_path):
        #response = requests.get('https://d3anr8px62ub97.cloudfront.net/ntr_7_19400')
        response = requests.get(image_path)
        return send_file(StringIO.StringIO(response.content), mimetype='image/jpg')