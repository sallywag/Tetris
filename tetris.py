"""
PIECES ARE CENTERED AT TOP ALWAYS START IN SAME POSITION,
THREE SEGMENT PEICES ARE PUSHED TO THE LEFT ONE SQUARE

CANT MOVE BLOCK MUST CHECK FOR COLLISION AT PIECE LEVEL
"""
from typing import Tuple
from itertools import product

import arcade

WINDOW_TITLE = "Tetris"
SCREEN_SIZE = {"width": 640, "height": 640}
HORIZONTAL_SQUARES = 10
VERTICAL_SQUARES = 18
SQUARE_SIZE = 32
MARGIN = 64
FRAMES_PER_DROP = 15

class Block(arcade.SpriteSolidColor):
    def __init__(self, color: arcade.Color, center_x: float, center_y: float):
        super().__init__(SQUARE_SIZE, SQUARE_SIZE, color)
        self.center_x = center_x
        self.center_y = center_y

    def in_bottom_row(self) -> bool:
        return self.center_y == SQUARE_SIZE * 2


class TetrisPiece:
    def __init__(self, *blocks: Tuple[Block]):
        super().__init__()
        self.blocks = [*blocks]

    def draw(self) -> None:
        for block in self.blocks:
            block.draw()

    def move_down(self, block_list: arcade.SpriteList) -> None:
        if not any(block.in_bottom_row() for block in self.blocks):
            for block in self.blocks:
                block.center_y -= SQUARE_SIZE
        if any(block.collides_with_list(block_list) for block in self.blocks):
            for block in self.blocks:
                block.center_y += SQUARE_SIZE


class SquarePiece(TetrisPiece):
    def __init__(self):
        super().__init__(
            Block(arcade.color.GREEN, SQUARE_SIZE*6, SQUARE_SIZE*18),
            Block(arcade.color.GREEN, SQUARE_SIZE*7, SQUARE_SIZE*18),
            Block(arcade.color.RED, SQUARE_SIZE*6, SQUARE_SIZE*19),
            Block(arcade.color.RED, SQUARE_SIZE*7, SQUARE_SIZE*19)
        )


class Tetris(arcade.Window):
    def __init__(self):
        super().__init__(SCREEN_SIZE["width"], SCREEN_SIZE["height"], WINDOW_TITLE)
        arcade.set_background_color(arcade.color.BLACK)
        self.current_piece = SquarePiece()

        self.test_piece = SquarePiece()
        self.test_piece.blocks[0].center_y -= 128
        self.test_piece.blocks[1].center_y -= 128
        self.test_piece.blocks[2].center_y -= 128
        self.test_piece.blocks[3].center_y -= 128
        self.test_piece.blocks[0].center_x -= 32
        self.test_piece.blocks[1].center_x -= 32
        self.test_piece.blocks[2].center_x -= 32
        self.test_piece.blocks[3].center_x -= 32

        self.frame_count = 0
        self.block_list = arcade.SpriteList()
        self.block_list.extend(self.current_piece.blocks)
        self.block_list.extend(self.test_piece.blocks)

    def on_update(self, delta_time: float) -> None:
        if self.frame_count == FRAMES_PER_DROP:
            self.current_piece.move_down(self.block_list)
            self.frame_count = 0
        else:
            self.frame_count += 1

    def on_draw(self) -> None:
        arcade.start_render()
        self.draw_grid()
        self.current_piece.draw()
        self.test_piece.draw()

    def draw_grid(self) -> None:
        for x, y in product(
            range(MARGIN, SQUARE_SIZE*HORIZONTAL_SQUARES+MARGIN, SQUARE_SIZE),
            range(MARGIN, SQUARE_SIZE*VERTICAL_SQUARES+MARGIN, SQUARE_SIZE)
        ):
            arcade.draw_rectangle_outline(
                x, y,
                SQUARE_SIZE, SQUARE_SIZE,
                arcade.color.BABY_PINK,
                2
            )


def main():
    game = Tetris()
    arcade.run()


if __name__ == "__main__":
    main()
