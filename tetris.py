"""
PIECES ARE CENTERED AT TOP ALWAYS START IN SAME POSITION,
THREE SEGMENT PEICES ARE PUSHED TO THE LEFT ONE SQUARE

CANT MOVE BLOCK MUST CHECK FOR COLLISION AT PIECE LEVEL
"""
from typing import Tuple
from itertools import product
import random

import arcade


WINDOW_TITLE = "Tetris"
SCREEN_SIZE = {"width": 640, "height": 640}
HORIZONTAL_SQUARES = 10
VERTICAL_SQUARES = 18
SQUARE_SIZE = 32
MARGIN = SQUARE_SIZE * 2
FRAMES_PER_DROP = 15


class Block(arcade.SpriteSolidColor):
    def __init__(self, color: arcade.Color, center_x: float, center_y: float):
        super().__init__(SQUARE_SIZE, SQUARE_SIZE, color)
        self.center_x = center_x
        self.center_y = center_y


class TetrisPiece:
    def __init__(self, *blocks: Tuple[Block]):
        super().__init__()
        self.blocks = arcade.SpriteList()
        self.blocks.extend(blocks)

    def draw(self) -> None:
        for block in self.blocks:
            block.draw()

    def move_up(self) -> None:
        for block in self.blocks:
            block.center_y += SQUARE_SIZE

    def move_down(self) -> None:
        for block in self.blocks:
            block.center_y -= SQUARE_SIZE

    def move_left(self) -> None:
        for block in self.blocks:
            block.center_x -= SQUARE_SIZE

    def move_right(self) -> None:
        for block in self.blocks:
            block.center_x += SQUARE_SIZE

    def at_bottom_edge(self) -> bool:
        return any(block.center_y == SQUARE_SIZE * 2 for block in self.blocks)

    def at_left_edge(self) -> bool:
        return any(block.center_x == 0 + MARGIN for block in self.blocks)

    def at_right_edge(self) -> bool:
        return any(
            block.center_x == HORIZONTAL_SQUARES * SQUARE_SIZE + SQUARE_SIZE
            for block in self.blocks
        )


class SquarePiece(TetrisPiece):
    def __init__(self):
        super().__init__(
            Block(arcade.color.ORANGE, SQUARE_SIZE * 6, SQUARE_SIZE * 18),
            Block(arcade.color.GREEN, SQUARE_SIZE * 7, SQUARE_SIZE * 18),
            Block(arcade.color.RED, SQUARE_SIZE * 6, SQUARE_SIZE * 19),
            Block(arcade.color.BLUE, SQUARE_SIZE * 7, SQUARE_SIZE * 19),
        )


class Tetris(arcade.Window):
    def __init__(self):
        super().__init__(SCREEN_SIZE["width"], SCREEN_SIZE["height"], WINDOW_TITLE)
        arcade.set_background_color(arcade.color.BLACK)
        self.current_piece = SquarePiece()
        self.next_piece = random.choice([SquarePiece])()
        self.rows_cleared = 0

        self.test_piece_1 = SquarePiece()
        self.test_piece_1.blocks[0].center_y -= SQUARE_SIZE * 16
        self.test_piece_1.blocks[1].center_y -= SQUARE_SIZE * 16
        self.test_piece_1.blocks[2].center_y -= SQUARE_SIZE * 16
        self.test_piece_1.blocks[3].center_y -= SQUARE_SIZE * 16
        self.test_piece_1.blocks[0].center_x -= SQUARE_SIZE * 4
        self.test_piece_1.blocks[1].center_x -= SQUARE_SIZE * 4
        self.test_piece_1.blocks[2].center_x -= SQUARE_SIZE * 4
        self.test_piece_1.blocks[3].center_x -= SQUARE_SIZE * 4

        self.test_piece_2 = SquarePiece()
        self.test_piece_2.blocks[0].center_y -= SQUARE_SIZE * 16
        self.test_piece_2.blocks[1].center_y -= SQUARE_SIZE * 16
        self.test_piece_2.blocks[2].center_y -= SQUARE_SIZE * 16
        self.test_piece_2.blocks[3].center_y -= SQUARE_SIZE * 16
        self.test_piece_2.blocks[0].center_x -= SQUARE_SIZE * 2
        self.test_piece_2.blocks[1].center_x -= SQUARE_SIZE * 2
        self.test_piece_2.blocks[2].center_x -= SQUARE_SIZE * 2
        self.test_piece_2.blocks[3].center_x -= SQUARE_SIZE * 2

        self.test_piece_3 = SquarePiece()
        self.test_piece_3.blocks[0].center_y -= SQUARE_SIZE * 16
        self.test_piece_3.blocks[1].center_y -= SQUARE_SIZE * 16
        self.test_piece_3.blocks[2].center_y -= SQUARE_SIZE * 16
        self.test_piece_3.blocks[3].center_y -= SQUARE_SIZE * 16

        self.test_piece_4 = SquarePiece()
        self.test_piece_4.blocks[0].center_y -= SQUARE_SIZE * 16
        self.test_piece_4.blocks[1].center_y -= SQUARE_SIZE * 16
        self.test_piece_4.blocks[2].center_y -= SQUARE_SIZE * 16
        self.test_piece_4.blocks[3].center_y -= SQUARE_SIZE * 16
        self.test_piece_4.blocks[0].center_x += SQUARE_SIZE * 2
        self.test_piece_4.blocks[1].center_x += SQUARE_SIZE * 2
        self.test_piece_4.blocks[2].center_x += SQUARE_SIZE * 2
        self.test_piece_4.blocks[3].center_x += SQUARE_SIZE * 2

        self.test_piece_5 = SquarePiece()
        self.test_piece_5.blocks[0].center_y -= SQUARE_SIZE * 16
        self.test_piece_5.blocks[1].center_y -= SQUARE_SIZE * 16
        self.test_piece_5.blocks[2].center_y -= SQUARE_SIZE * 16
        self.test_piece_5.blocks[3].center_y -= SQUARE_SIZE * 16
        self.test_piece_5.blocks[0].center_x += SQUARE_SIZE * 4
        self.test_piece_5.blocks[1].center_x += SQUARE_SIZE * 4
        self.test_piece_5.blocks[2].center_x += SQUARE_SIZE * 4
        self.test_piece_5.blocks[3].center_x += SQUARE_SIZE * 4

        self.frame_count = 0
        self.pieces = [
            self.test_piece_1,
            self.test_piece_2,
            self.test_piece_3,
            self.test_piece_4,
            self.test_piece_5,
        ]

    def on_key_press(self, symbol: int, modifiers: int) -> None:
        if symbol == arcade.key.LEFT and not self.current_piece.at_left_edge():
            self.current_piece.move_left()
            if self.collides_with_other_pieces(self.current_piece):
                self.current_piece.move_right()
        elif symbol == arcade.key.RIGHT and not self.current_piece.at_right_edge():
            self.current_piece.move_right()
            if self.collides_with_other_pieces(self.current_piece):
                self.current_piece.move_left()
        if symbol == arcade.key.SPACE:
            self.clear_full_rows()

    def collides_with_other_pieces(self, piece: TetrisPiece) -> bool:
        for piece_ in self.pieces:
            if any(block.collides_with_list(piece_.blocks) for block in piece.blocks):
                return True
        return False

    def on_update(self, delta_time: float) -> None:
        if self.frame_count == FRAMES_PER_DROP:
            if not self.current_piece.at_bottom_edge():
                self.current_piece.move_down()
                if self.collides_with_other_pieces(self.current_piece):
                    self.current_piece.move_up()
            self.frame_count = 0
        else:
            self.frame_count += 1

    def clear_full_rows(self) -> None:
        count = {}

        for piece in self.pieces:
            for block in piece.blocks:
                if block.center_y not in count:
                    count[block.center_y] = 1
                else:
                    count[block.center_y] += 1
        print(count)

        locations_to_delete = []
        for key, value in count.items():
            if value == HORIZONTAL_SQUARES:
                locations_to_delete.append(key)
        print(locations_to_delete)

        for piece in self.pieces:
            for block in piece.blocks[:]:
                if block.center_y in locations_to_delete:
                    print("HERE")
                    piece.blocks.remove(block)

        print(self.pieces)
        for piece in self.pieces[:]:
            if not piece.blocks:
                self.pieces.remove(piece)
        print(self.pieces)
        
        self.rows_cleared += len(locations_to_delete)

    def on_draw(self) -> None:
        arcade.start_render()
        self.draw_grid()
        self.draw_next_piece_preview()
        self.draw_score()
        self.current_piece.draw()
        for piece in self.pieces:
            piece.draw()

    def draw_grid(self) -> None:
        for x, y in product(
            range(MARGIN, SQUARE_SIZE * HORIZONTAL_SQUARES + MARGIN, SQUARE_SIZE),
            range(MARGIN, SQUARE_SIZE * VERTICAL_SQUARES + MARGIN, SQUARE_SIZE),
        ):
            arcade.draw_rectangle_outline(
                x, y, SQUARE_SIZE, SQUARE_SIZE, arcade.color.BABY_PINK, 2
            )

    def draw_next_piece_preview(self) -> None:
        arcade.draw_rectangle_outline(
            HORIZONTAL_SQUARES * SQUARE_SIZE + SQUARE_SIZE * 2 + MARGIN,
            VERTICAL_SQUARES * SQUARE_SIZE,
            SQUARE_SIZE * 3,
            SQUARE_SIZE * 3,
            arcade.color.BABY_BLUE,
            2,
        )

    def draw_score(self) -> None:
        arcade.draw_text(
            f"Rows Cleared: {self.rows_cleared}",
            384,
            480,
            arcade.color.BABY_POWDER,
            14,
            align="left"
        )


def main():
    game = Tetris()
    arcade.run()


if __name__ == "__main__":
    main()
