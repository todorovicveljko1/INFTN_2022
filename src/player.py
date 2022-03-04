class Player:
    def __init__(self, player_data) -> None:
        self.id = player_data["id"]
        self.pos = player_data["pos"]

    def update(self, player_data) -> None:
        self.id = player_data["id"]
        self.pos = player_data["pos"]

    def to_json(self) -> dict:
        return {
            "id": self.id,
            "pos": str(self.pos)
        }
