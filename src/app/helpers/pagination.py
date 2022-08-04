class Pagination:
    def __init__(self, limit=None, offset=None):
        self.limit = limit
        self.offset = offset

    def getQuery(self):
        pagination = [{
            "$match": {}
        }]

        if not self.offset is None:
            pagination.append({"$skip": self.offset})

        if not self.limit is None:
            pagination.append({"$limit": self.limit})

        return [
            {
                "$facet": {
                    "data": pagination,
                    "total": [
                        {
                            "$group": {
                                "_id": None,
                                "count": {
                                    "$sum": 1
                                }
                            }
                        }
                    ]
                }
            },
            {
                "$unwind": "$total"
            },
            {
                "$project": {
                    "total._id": 0
                }
            }
        ]
