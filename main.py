from input import Input
from world import World
from gameAction import GameAction
from graphic import Graphic
import cv2 as cv

if __name__ == '__main__':

    input = Input()
    input.parse_and_store()

    my_world = World(input.world.data)
    my_world.build_world()

    graphic_world = Graphic(my_world.mat_world)
    graphic_world.show_matrix()



    gameAction = GameAction()
    # over the start
    for command in input.start:
        command.arguments.append("start")
        gameAction.execute_command(command)

    # over the input
    for command in input.steps:
        command.arguments.append("input")
        gameAction.execute_command(command)

    # over the asserts
    for one_assert in input.asserts:
        gameAction.execute_asserts(one_assert)

