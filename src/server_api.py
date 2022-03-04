from urllib import response
import requests


class ServerApi:
    def __init__(self, server_url, game_id, player_id) -> None:
        self.server_url = server_url
        self.game_id = game_id
        self.player_id = player_id

    def init_connection(self):
        response = requests.get(
            f"{self.server_url}/joinGame?playerId={self.player_id}&gameId={self.game_id}")
        return response.json()

    def do_action(self, action: tuple[str, dict[str, str] | None]):
        print(action)
        url = f"{self.server_url}/{action[0]}/?playerId={self.player_id}&gameId={self.game_id}"
        if action[1] is not None:
            for key in action[1]:
                url += ("&" + str(key) + "=" + str(action[1][key]))
        response = requests.get(url)
        return response.json()
