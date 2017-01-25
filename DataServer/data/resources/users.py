from flask_apispec import (
    marshal_with,
    use_kwargs,
    doc,
    MethodResource
)

import json
from datetime import timedelta
from flask import Response
from flask_apispec import (
    marshal_with,
    use_kwargs,
    doc,
    MethodResource
)

from marshmallow import fields
from ..logic import main
from ..auth.key import require_appkey


class u(MethodResource):
    @require_appkey
    # @use_kwargs({'nutrino_id': fields.Str()})
    # @marshal_with(DiaryItemContainer)
    def get(self, nutrino_id):
        return main.get_fooditems_for_level(nutrino_id)
