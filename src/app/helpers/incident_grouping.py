class SortingOperands:
    date = "reporter.timestamp"
    product_name = "product.name"
    serial_number = "product.serial_number"
    company_name = "assigned_company.name"
    incident_type = "type"

class DateGroupingOperands:
    day = {
        "day":
        {
            "$dayOfYear": {
                "$dateFromString": {
                    "dateString": "$reporter.timestamp"
                }
            },
        },
        "year":
        {
            "$year": {
                "$dateFromString": {
                    "dateString": "$reporter.timestamp"
                }
            }
        }
    }
    month = {
        "month":
        {
            "$month": {
                "$dateFromString": {
                    "dateString": "$reporter.timestamp"
                }
            },
        },
        "year":
        {
            "$year": {
                "$dateFromString": {
                    "dateString": "$reporter.timestamp"
                }
            }
        }
    }
    year = {
        "year":
        {
            "$year": {
                "$dateFromString": {
                    "dateString": "$reporter.timestamp"
                }
            }
        }
    }

    def __init__(self, mode):
        self.mode = mode

    def get(self):
        return getattr(self, self.mode)

class GroupingOperands:
    day = DateGroupingOperands("day")
    month = DateGroupingOperands("month")
    year = DateGroupingOperands("year")
    company_name = "$assigned_company.company"
    incident_type = "$type"

class IncidentGrouping:
    def __init__(self, group: str = "day", sort: str = "dsc"):
        self.grouping_operands = GroupingOperands()
        self.sorting_operands = SortingOperands()

        self.group_string = group
        self.group_operand = getattr(self.grouping_operands, group)
        self.sort = sort
        self.defaultSortingOrder = [
            getattr(self.sorting_operands, "date"),
            getattr(self.sorting_operands, "company_name"), 
            getattr(self.sorting_operands, "product_name"), 
            getattr(self.sorting_operands, "incident_type"),
            getattr(self.sorting_operands, "serial_number")
            ]
    
    def getSortingOrder(self, primary):
        result = [primary]

        for item in self.defaultSortingOrder:
            if item != primary:
                result.append(item)
        
        return result
    
    def getSortingObject(self):
        primary=""
        sorting_object = {}

        if type(self.group_operand) is DateGroupingOperands:
            primary = self.sorting_operands.date
        else:
            primary = getattr(self.sorting_operands, self.group_string)

        sortingOrder = self.getSortingOrder(primary)

        for item in sortingOrder:
            if self.sort == "asc":
                sorting_object[item] = 1
            else:
                sorting_object[item] = -1

        return sorting_object

    def getGroupingObject(self):
        grouping_object = {}

        if type(self.group_operand) is DateGroupingOperands:
            grouping_object["_id"] = self.group_operand.get()
        else:
            grouping_object["_id"] = self.group_operand
        
        grouping_object["incidents"] = {
            "$addToSet": "$$ROOT"
        }

        return grouping_object
    
    def getQuery(self):
        group = self.getGroupingObject()
        sort = self.getSortingObject()

        return [
            {
                "$sort": sort
            },
            {
                "$group": group
            },
            {
                "$project": {
                    "incidents._id": 0
                }
            }
        ]