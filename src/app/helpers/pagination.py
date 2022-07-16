class Pagination:
    def __init__(self, limit, offset):
        self.limit = limit
        self.offset = offset
    
    def getQuery(self):
        return [
            {
                "$skip": self.offset
            },
            {
                "$limit": self.limit
            }
        ]