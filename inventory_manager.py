class InventoryManager:
    def __init__(self, hotbar_size=8):
        self.hotbar = [{'id': 0, 'count': 0} for _ in range(hotbar_size)]
        self.selected_index = 0

    def add_item(self, block_id, amount=1):
        if block_id == 0:
            return False

        for slot in self.hotbar:
            if slot['id'] == block_id:
                slot['count'] += amount
                return True

        for slot in self.hotbar:
            if slot['id'] == 0:
                slot['id'] = block_id
                slot['count'] = amount
                return True

        # 3. Ak je všetko plné
        print("Inventár je plný!")
        return False

    def get_selected_item(self):
        slot = self.hotbar[self.selected_index]
        if slot['count'] > 0:
            return slot['id']
        return 0

    def remove_selected_item(self, amount=1):
        slot = self.hotbar[self.selected_index]
        if slot['id'] != 0 and slot['count'] > 0:
            slot['count'] -= amount
            if slot['count'] <= 0:
                slot['id'] = 0
                slot['count'] = 0
            return True
        return False

    def scroll(self, delta):
        self.selected_index = (self.selected_index - delta) % len(self.hotbar)