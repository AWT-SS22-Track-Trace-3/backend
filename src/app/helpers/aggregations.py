full_product_aggregation = [
    {
        '$match': {
            'serial_number': '9982722773858693'
        }
    }, {
        '$lookup': {
            'from': 'users',
            'localField': 'manufacturers',
            'foreignField': 'username',
            'as': 'manufacturers'
        }
    }, {
        '$unwind': '$supply_chain'
    }, {
        '$lookup': {
            'from': 'users',
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
            'from': 'products',
            'localField': '_id',
            'foreignField': '_id',
            'as': 'product'
        }
    }, {
        '$unwind': '$product'
    }, {
        '$lookup': {
            'from': 'incidents',
            'localField': 'product.serial_number',
            'foreignField': 'product',
            'as': 'incidents'
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
            'supply_chain.owner.access_lvl': 0
        }
    }
]
