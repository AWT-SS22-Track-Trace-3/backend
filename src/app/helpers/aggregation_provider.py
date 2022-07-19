class AggregationPipelineBuilder:
    pipeline = []

    def init(self, match):
        self.pipeline = []

        self.pipeline.append({
            "$match": match
        })

        return self

    def addLookup(self, collection, localField, foreignField, newField, unwind: bool = False):
        self.pipeline.append({
            "$lookup": {
                "from": collection,
                "localField": localField,
                "foreignField": foreignField,
                "as": newField
            }
        })

        if unwind:
            self.unwind(newField)

        return self

    def unwind(self, field):
        self.pipeline.append({
            "$unwind": "$" + field
        })

        return self

    def addFields(self, field_name, expr: dict | str):
        result = {
            "$addFields": {}
        }

        result["$addFields"][field_name] = expr

        self.pipeline.append(result)

        return self

    def addGroup(self, group):
        self.pipeline.append({
            "$group": group
        })

        return self

    def addMatch(self, match: dict):
        self.pipeline.append({
            "$match": match
        })

        return self

    def addBinaryProjection(self, fields: list, mode: int):
        result = {}

        for field in fields:
            result[field] = mode

        self.pipeline.append({
            "$project": result
        })

        return self

    def addSort(self, sort):
        self.pipeline.append({
            "$sort": sort
        })

        return self

    def build(self):
        return self.pipeline
