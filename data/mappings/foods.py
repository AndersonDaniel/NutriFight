from elasticsearch_dsl import DocType

foods_index = 'nutrino_cms'
fooditems_type = 'fooditems'


class FoodItem(DocType):
    class Meta:
        foods_index = foods_index
        doc_type = fooditems_type
