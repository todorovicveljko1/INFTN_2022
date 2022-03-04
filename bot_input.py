from src.agent import Agent
import time
TURN = 0
MAX_TURN = 98
agent = None


def bot_input(dto):
    global TURN, agent, MAX_TURN
    if TURN % MAX_TURN == 0:
        agent = Agent(dto.tiles, dto.source, dto.enemy)
    else:
        agent.update_state(dto.tiles, dto.source, dto.enemy)

    # print(TURN)
    #print(dto.source.points, dto.source.gold)
    out = agent.next_action().toJSON()
    # print(out)
    TURN += 1
    return out
