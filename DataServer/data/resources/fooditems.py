from flask_apispec import (
    marshal_with,
    MethodResource
)

from ..auth.key import require_appkey
from ..logic import main
from ..schema.response import LevelContainer


class foods(MethodResource):
    @require_appkey
    @marshal_with(LevelContainer)
    def get(self, nutrino_id):
        return main.get_fooditems_for_label(nutrino_id)
