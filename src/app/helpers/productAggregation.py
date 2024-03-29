from app.helpers.aggregationProvider import AggregationPipelineBuilder


class ProductAggregator:

    def __init__(self, incidents_coll="incidents", products_coll="products", users_coll="users"):
        self.incidents_coll = incidents_coll
        self.products_coll = products_coll
        self.users_coll = users_coll

        self.builder = None

    def _serialMatch(self, number):
        return {
            "serial_number": number
        }

    def _companyMatch(self, company):
        return {
            "$expr": {
                "$or": [
                    {
                        "$in": [
                            company, "$manufacturers"
                        ]
                    },
                    {
                        "$in": [
                            company, "$sellers"
                        ]
                    },
                    {
                        "$in": [
                            company, "$supply_chain.owner"
                        ]
                    }
                ]
            }
        }

    def _addBaseLookup(self):
        self.builder.add([
            {
                '$lookup': {
                    'from': self.users_coll,
                    'localField': 'manufacturers',
                    'foreignField': 'username',
                    'as': 'manufacturers'
                }
            }, {
                '$unwind': '$supply_chain'
            }, {
                '$lookup': {
                    'from': self.users_coll,
                    'localField': 'supply_chain.owner',
                    'foreignField': 'username',
                    'as': 'supply_chain.owner'
                }
            }, {
                '$unwind': '$supply_chain.owner'
            }, {
                '$group': {
                    '_id': '$_id',
                    'supply_chain': {
                        '$push': '$supply_chain'
                    }
                }
            }, {
                '$lookup': {
                    'from': self.products_coll,
                    'localField': '_id',
                    'foreignField': '_id',
                    'as': 'product'
                }
            }, {
                '$unwind': '$product'
            }, {
                '$lookup': {
                    'from': self.users_coll,
                    'localField': 'product.manufacturers',
                    'foreignField': 'username',
                    'as': 'product.manufacturers'
                }
            }, {
                '$lookup': {
                    'from': self.users_coll,
                    'localField': 'product.sellers',
                    'foreignField': 'username',
                    'as': 'product.sellers'
                }
            }, {
                '$lookup': {
                    'from': self.incidents_coll,
                    'localField': 'product.serial_number',
                    'foreignField': 'product',
                    'as': 'incidents'
                }
            }, {
                '$unwind': {
                    'path': '$incidents',
                    'preserveNullAndEmptyArrays': True
                }
            }, {
                '$lookup': {
                    'from': self.users_coll,
                    'localField': 'incidents.reporter.user',
                    'foreignField': 'username',
                    'as': 'incidents.reporter.user'
                }
            }, {
                '$unwind': {
                    'path': '$incidents.reporter.user',
                    'preserveNullAndEmptyArrays': True
                }
            }, {
                '$group': {
                    '_id': '$_id',
                    'incidents': {
                        '$push': '$incidents'
                    },
                    'product': {
                        '$first': '$product'
                    },
                    'supply_chain': {
                        '$first': '$supply_chain'
                    }
                }
            }, {
                '$addFields': {
                    'product.supply_chain': '$supply_chain',
                    'product.incidents': '$incidents'
                }
            }, {
                '$replaceRoot': {
                    'newRoot': '$product'
                }
            }, {
                '$project': {
                    '_id': 0,
                    'incidents._id': 0,
                    'incidents.product': 0,
                    'supply_chain.owner._id': 0,
                    'supply_chain.owner.password': 0,
                    'supply_chain.owner.access_lvl': 0,
                    'incidents.reporter.user._id': 0,
                    'incidents.reporter.user.password': 0,
                    'incidents.reporter.user.access_lvl': 0,
                    'manufacturers._id': 0,
                    'manufacturers.password': 0,
                    'manufacturers.access_lvl': 0,
                    'sellers._id': 0,
                    'sellers.password': 0,
                    'sellers.access_lvl': 0,
                }
            }
        ])

    def getProductBySerial(self, serial_number):
        self.builder = AggregationPipelineBuilder().init(self._serialMatch(serial_number))
        self._addBaseLookup()

        return self.builder.build()

    def getProductBySearchRestricted(self, query, company):
        match = self._companyMatch(company) | query

        self.builder = AggregationPipelineBuilder().init(match)
        self._addBaseLookup()
        self.builder.addProjection({"incidents": 0})

        return self.builder.build()

    def getProductBySerialRestricted(self, serial_number, company):
        match = self._companyMatch(company)

        self.builder = AggregationPipelineBuilder().init(match)
        self.builder.addMatch(self._serialMatch(serial_number))
        self._addBaseLookup()
        self.builder.addProjection({"incidents": 0})

        return self.builder.build()
