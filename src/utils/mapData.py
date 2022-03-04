
class MapData:
    def __init__(self) -> None:
        self.map = []
        self.metadata = {}
        self.annotations = []
        self.players = {
            "me": None,
            "opponents": []
        }

    def preset(self, metadata):
        self.metadata = metadata

    def toJson(self, withMeta=False):
        if withMeta:
            return {
                "map": self.map,
                "metadata": self.metadata,
                "annotations": self.annotations,
                "players": self.players
            }
        else:
            return {
                "map": self.map,
                "annotations": self.annotations,
                "players": self.players
            }
