from app.helpers.group_definitions import FormattingTypes, default_sort_order


class IncidentGrouper:

    def __init__(self, definition):
        self.definition = definition

    def build_group_query(self):
        pipeline = []

        group_base_obj = {
            "$group": {
                "_id": self.definition["aggregation_key"],
                "count": {"$sum": 1}
            } | self.definition["additional_aggregation"]
        }

        pipeline.append(group_base_obj)

        if self.definition["formatting"]["type"] == FormattingTypes.in_aggregation:
            pipeline += self.definition["formatting"]["format"]

        return pipeline

    def build_pre_sort(self, order):
        object = {}

        for item in default_sort_order:
            object[item] = order

        return {
            "$sort": object
        }

    def build_post_sort(self, order):
        object = {}

        for key in self.definition["aggregation_key"].keys():
            object["_id." + key] = order

        return {
            "$sort": object
        }

    def get_grouping_query(self, sorting_order):
        pipeline = []

        pipeline += self.build_group_query()
        pipeline.append(self.build_post_sort(sorting_order))
        pipeline.append({"$project": {"incidents._id": 0}})

        return pipeline
