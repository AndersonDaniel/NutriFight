from flask import Response
from flask_apispec import (
    use_kwargs,
    MethodResource
)
from marshmallow import fields

from ..auth.key import require_appkey
from ..logic import main


class users(MethodResource):
    @use_kwargs({'correct_count': fields.Int(),
                 'wrong_count': fields.Int(),
                 'food_id': fields.Str(),
                 'label': fields.Str(),
                 'answer': fields.Bool()})
    @require_appkey
    def post(self, nutrino_id, correct_count, wrong_count, food_id, label, answer):
        main.finish_label(nutrino_id, correct_count, wrong_count, food_id, label, answer)

        return Response(status=201)


class user_game(MethodResource):
    @require_appkey
    def get(self, nutrino_id):
        return main.get_game_state(nutrino_id)

    @use_kwargs({'game_data': fields.Str()})
    @require_appkey
    def post(self, nutrino_id, game_data):
        main.save_game_state(nutrino_id, game_data)
        return Response(status=201)
