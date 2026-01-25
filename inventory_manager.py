class InventoryManager:
    """Simple inventory manager that holds a hotbar list and selected index.

    Hotbar items are represented by integer IDs (e.g., block ids from settings.BLOCKS).
    """
    def __init__(self, hotbar_size=5, initial=None):
        if initial:
            self.hotbar = list(initial)
        else:
            self.hotbar = [0] * hotbar_size
        self.index = 0

    def set_hotbar(self, items):
        self.hotbar = list(items)
        if self.index >= len(self.hotbar):
            self.index = max(0, len(self.hotbar) - 1)

    def get_selected(self):
        if 0 <= self.index < len(self.hotbar):
            return self.hotbar[self.index]
        return 0

    def scroll(self, delta):
        # wrap-around scroll for convenience
        if len(self.hotbar) == 0:
            return
        self.index = (self.index + delta) % len(self.hotbar)

    def set_index(self, idx):
        if len(self.hotbar) == 0:
            self.index = 0
            return
        self.index = max(0, min(idx, len(self.hotbar) - 1))
