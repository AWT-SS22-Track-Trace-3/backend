from datetime import datetime
from enum import Enum
from dateutil.relativedelta import *


def format_date(item, format):
    day = item["_id"]["day"] - 1 if "day" in item["_id"] else 0
    month = item["_id"]["month"] - 1 if "month" in item["_id"] else 0

    date = datetime(item["_id"]["year"], 1, 1) + \
        relativedelta(months=+month, days=+day)

    item["_id"] = item["_id"] | {
        "formatted": date.strftime(format),
        "raw": date.isoformat() + "Z"
    }

    return item


def format_dummy(item, *args):
    item["_id"] = item["_id"] | {
        "formatted": item["_id"]["raw"],
        "raw": item["_id"]["raw"],
    }

    return item


class FormattingTypes(Enum):
    pre_aggregation = 0
    in_aggregation = 1
    post_aggregation = 2
    none = 3


class SortingOrder(Enum):
    dsc = -1
    asc = 1


accumulate_unique_companies = {
    '$accumulator': {
        'init': 'function() {return { count: 0, companies: [] }}',
        'accumulate': 'function(state, username) { if(!state.companies.includes(username)) { return {count: state.count + 1, companies: state.companies.concat(username)}} return state}',
        'accumulateArgs': [
            '$assigned_company.username'
        ],
        'merge': 'function(state1, state2) {return {count: state1.count + state2.count, companies: state1.companies.concat(state2.companies)}}',
        'finalize': 'function(state) {return state.count}',
        'lang': 'js'
    }
}

group_def = {
    "day": {
        "type": "date",
        "aggregation_key": {
            "year": {
                "$year": "$reporter.timestamp"
            }, "day": {
                "$dayOfYear": "$reporter.timestamp"
            }
        },
        "additional_aggregation": {
            "unique_companies": accumulate_unique_companies
        },
        "formatting": {
            "fn": format_date,
            "type": FormattingTypes.post_aggregation,
            "format": "%d.%m.%Y"
        }
    },
    "month": {
        "type": "date",
        "aggregation_key": {
            "year": {
                "$year": "$reporter.timestamp"
            }, "month": {
                "$month": "$reporter.timestamp"
            }
        },
        "additional_aggregation": {
            "unique_companies": accumulate_unique_companies
        },
        "formatting": {
            "fn": format_date,
            "type": FormattingTypes.post_aggregation,
            "format": "%b %Y"
        }
    },
    "year": {
        "type": "date",
        "aggregation_key": {
            "raw": {
                "$year": "$reporter.timestamp"
            }
        },
        "additional_aggregation": {
            "unique_companies": accumulate_unique_companies
        },
        "formatting": {
            "type": FormattingTypes.post_aggregation,
            "fn": format_dummy,
            "format": None
        }
    },
    "incident_type": {
        "type": "generic",
        "aggregation_key": {
            "raw": "$type"
        },
        "additional_aggregation": {
            "unique_companies": accumulate_unique_companies
        },
        "formatting": {
            "type": FormattingTypes.post_aggregation,
            "fn": format_dummy,
            "format": None
        }
    },
    "company_name": {
        "type": "generic",
        "aggregation_key": {
            "raw": "$assigned_company.username"
        },
        "additional_aggregation": {},
        "formatting": {
            "type": FormattingTypes.in_aggregation,
            "fn": None,
            "format": [
                {
                    "$lookup": {
                        "from": "users",
                        "localField": "_id.raw",
                        "foreignField": "username",
                        "as": "_id.formatted"
                    }
                }, {
                    "$set": {
                        "_id.formatted": {
                            "$arrayElemAt": [
                                "$_id.formatted.company", 0
                            ]
                        }
                    }
                }
            ]
        },
    }
}

default_sort_order = [
    "reporter.timestamp",
    "product.name",
    "product.serial_number",
    "assigned_company.name",
    "type"
]
