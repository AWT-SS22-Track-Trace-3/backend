class SortingOperands:
    date = "reporter.timestamp"
    product_name = "product.name"
    serial_number = "product.serial_number"
    company_name = "assigned_company.name"
    incident_type = "type"

    default_order = [date, company_name, product_name, incident_type, serial_number]

    def __init__(self, mode):
        self.mode = mode

    def get_pre(self, primary):
        result = [primary]

        for item in self.default_order:
            if item != primary:
                result.append(item)
        
        return result

class DateGroupingOperands:
    day = {
        "year":
        {
            "$year": {
                "$dateFromString": {
                    "dateString": "$reporter.timestamp"
                }
            }
        },
        "day":
        {
            "$dayOfYear": {
                "$dateFromString": {
                    "dateString": "$reporter.timestamp"
                }
            },
        }
        
    }
    month = {
        "year":
        {
            "$year": {
                "$dateFromString": {
                    "dateString": "$reporter.timestamp"
                }
            }
        },
        "month":
        {
            "$month": {
                "$dateFromString": {
                    "dateString": "$reporter.timestamp"
                }
            },
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

    def __init__(self, mode):
        self.mode = mode

    def get(self):
        return getattr(self, self.mode)
    
    def get_post_sort(self, order):
        result = {}

        if type(self.get()) is DateGroupingOperands:
            for key in self.get().get().keys():
                result["_id." + key] = order
        else:
            result["_id." + self.mode] = order
        
        return result

class IncidentGrouping:
    def __init__(self, group: str = "day", sort: str = "dsc"):
        self.grouping_operands = GroupingOperands(group)
        self.sorting_operands = SortingOperands(sort)

        self.group_string = group
        self.group_operand = getattr(self.grouping_operands, group)
        self.sort = sort
    
    def getSortingObject(self):
        primary=""
        sorting_object = {}

        if type(self.group_operand) is DateGroupingOperands:
            primary = self.sorting_operands.date
        else:
            primary = getattr(self.sorting_operands, self.group_string)

        sortingOrder = self.sorting_operands.get_pre(primary)

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
            grouping_object["_id"] = { 
                self.group_string: self.group_operand
            }
        
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
                "$sort": self.grouping_operands.get_post_sort(1 if self.sort == "asc" else -1)
            },
            {
                "$project": {
                    "incidents._id": 0
                }
            }
        ]