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