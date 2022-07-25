from datetime import datetime


class SupplyChainValidator:
    def __init__(self, supply_chain, request, user):
        self.supply_chain = supply_chain
        self.request = request
        self.user = user

        self.dissected_sc = self._dissect_supply_chain()

        self.result = True
        self.messages = []

    def _dissect_supply_chain(self):
        result = {
            "change_of_ownership": [],
            "shipment": [],
            "termination": []
        }

        for item in self.supply_chain:
            result[item["type"]].append(item)

        result["change_of_ownership"].sort(key=lambda e: e["id"])
        result["shipment"].sort(key=lambda e: e["id"])
        result["termination"].sort(key=lambda e: e["id"])

        return result

    def validate_checkin(self):
        last_element = self.dissected_sc["change_of_ownership"][-1]

        # product checked out before
        if not last_element["checked_out"]:
            self.append_message("Product was not previously checked out.")

            # different owner declared
            if last_element["future_owner"] != self.user:
                self.append_message(
                    "Different owner declared on previous check-out.")

            return

        # transaction dates do not match
        if not last_element.get("transaction_date").date() != self.request.get("transaction_date").date():
            self.append_message("Transaction dates do not match.")

        # different owner declared
        if last_element["owner"] != self.user:
            self.append_message(
                "Different owner declared on previous check-out.")

        if datetime.utcnow() < last_element.get("transaction_date"):
            self.append_message("Product checked in before transaction date.")

    def validate_checkout(self):
        pass

    def validate_termination(self):
        pass

    def append_message(self, message):
        self.result = False
        self.messages.append(message)
