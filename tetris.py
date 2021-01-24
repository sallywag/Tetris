from typing import List, Dict
from itertools import product
from copy import deepcopy
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
    def __init__(self, blocks: List[Block], pivot_block_index: int = None):
        super().__init__()
        self.blocks = arcade.SpriteList()
        self.blocks.extend(blocks)
        self.falling = True
        self.pivot_block = None
        self.pivot_block_index = pivot_block_index
        if pivot_block_index:
            self.pivot_block = self.blocks[pivot_block_index]

    def draw(self) -> None:
        for block in self.blocks:
            block.draw()

    def rotate(self, other_pieces: List["TetrisPiece"]) -> None:
        if self.pivot_block:
            original_blocks = deepcopy(self.blocks)
            for block in self.blocks:
                if block is not self.pivot_block:
                    x_dif = block.center_x - self.pivot_block.center_x
                    y_dif = block.center_y - self.pivot_block.center_y
                    new_x = 0 * x_dif + -1 * y_dif
                    new_y = 1 * x_dif + 0 * y_dif
                    block.center_x = self.pivot_block.center_x + new_x
                    block.center_y = self.pivot_block.center_y + new_y
            if (
                self.collides_with_other_pieces(other_pieces)
                or self.past_bottom_edge()
                or self.past_left_edge()
                or self.past_right_edge()
            ):
                self.blocks = original_blocks
                self.pivot_block = self.blocks[self.pivot_block_index]

    def move_down(self, other_pieces: List["TetrisPiece"]) -> None:
        if not self.at_bottom_edge():
            for block in self.blocks:
                block.center_y -= SQUARE_SIZE
            if self.collides_with_other_pieces(other_pieces):
                for block in self.blocks:
                    block.center_y += SQUARE_SIZE
                self.falling = False
        else:
            self.falling = False

    def move_left(self, other_pieces: List["TetrisPiece"]) -> None:
        if not self.at_left_edge():
            for block in self.blocks:
                block.center_x -= SQUARE_SIZE
            if self.collides_with_other_pieces(other_pieces):
                for block in self.blocks:
                    block.center_x += SQUARE_SIZE

    def move_right(self, other_pieces: List["TetrisPiece"]) -> None:
        if not self.at_right_edge():
            for block in self.blocks:
                block.center_x += SQUARE_SIZE
            if self.collides_with_other_pieces(other_pieces):
                for block in self.blocks:
                    block.center_x -= SQUARE_SIZE

    def drop(self, other_pieces: List["TetrisPiece"]) -> None:
        if not self.at_bottom_edge():
            while True:
                for block in self.blocks:
                    block.center_y -= SQUARE_SIZE
                if self.collides_with_other_pieces(other_pieces):
                    for block in self.blocks:
                        block.center_y += SQUARE_SIZE
                    break
                if self.at_bottom_edge():
                    break
            self.falling = False

    def at_bottom_edge(self) -> bool:
        return any(block.center_y == SQUARE_SIZE * 2 for block in self.blocks)

    def at_left_edge(self) -> bool:
        return any(block.center_x == 0 + MARGIN for block in self.blocks)

    def at_right_edge(self) -> bool:
        return any(
            block.center_x == HORIZONTAL_SQUARES * SQUARE_SIZE + SQUARE_SIZE
            for block in self.blocks
        )

    def past_bottom_edge(self) -> bool:
        return any(block.center_y < SQUARE_SIZE * 2 for block in self.blocks)

    def past_left_edge(self) -> bool:
        return any(block.center_x < 0 + MARGIN for block in self.blocks)

    def past_right_edge(self) -> bool:
        return any(
            block.center_x > HORIZONTAL_SQUARES * SQUARE_SIZE + SQUARE_SIZE
            for block in self.blocks
        )

    def collides_with_other_pieces(self, other_pieces: List["TetrisPiece"]) -> bool:
        for piece in other_pieces:
            if any(block.collides_with_list(piece.blocks) for block in self.blocks):
                return True
        return False


class OPiece(TetrisPiece):
    def __init__(self):
        super().__init__(
            [
                Block(arcade.color.RED, SQUARE_SIZE * 6, SQUARE_SIZE * 18),
                Block(arcade.color.RED, SQUARE_SIZE * 7, SQUARE_SIZE * 18),
                Block(arcade.color.RED, SQUARE_SIZE * 6, SQUARE_SIZE * 19),
                Block(arcade.color.RED, SQUARE_SIZE * 7, SQUARE_SIZE * 19),
            ]
        )


class TPiece(TetrisPiece):
    def __init__(self):
        super().__init__(
            [
                Block(arcade.color.PURPLE, SQUARE_SIZE * 7, SQUARE_SIZE * 18),
                Block(arcade.color.PURPLE, SQUARE_SIZE * 6, SQUARE_SIZE * 19),
                Block(arcade.color.PURPLE, SQUARE_SIZE * 7, SQUARE_SIZE * 19),
                Block(arcade.color.PURPLE, SQUARE_SIZE * 8, SQUARE_SIZE * 19),
            ],
            2,
        )


class Tetris(arcade.Window):
    def __init__(self):
        super().__init__(SCREEN_SIZE["width"], SCREEN_SIZE["height"], WINDOW_TITLE)
        arcade.set_background_color(arcade.color.BLACK)
        self.current_piece = random.choice([OPiece, TPiece])()
        self.next_piece = random.choice([OPiece, TPiece])()
        self.rows_cleared = 0
        self.reset_button = arcade.SpriteSolidColor(96, 32, arcade.color.BARN_RED)
        self.pieces = [self.current_piece]
        self.frame_count = 0
        self.game_over = False

    def on_key_press(self, symbol: int, modifiers: int) -> None:
        if symbol == arcade.key.LEFT:
            self.current_piece.move_left(self.pieces)
        elif symbol == arcade.key.RIGHT:
            self.current_piece.move_right(self.pieces)
        if symbol == arcade.key.SPACE:
            self.current_piece.drop(self.pieces)
        if symbol == arcade.key.R:
            self.current_piece.rotate(self.pieces)

    def on_update(self, delta_time: float) -> None:
        if self.frame_count == FRAMES_PER_DROP:
            self.current_piece.move_down(self.pieces)
            self.frame_count = 0
        else:
            self.frame_count += 1
        if not self.current_piece.falling:
            self.ready_next_piece()

    def ready_next_piece(self) -> None:
        self.clear_full_rows()
        self.drop_hanging_pieces()
        self.current_piece = self.next_piece
        self.pieces.append(self.current_piece)
        self.next_piece = random.choice([OPiece, TPiece])()

    def clear_full_rows(self) -> None:
        locations_to_delete = self.get_locations_of_blocks_to_delete(
            self.get_block_count_per_row()
        )
        self.remove_blocks(locations_to_delete)
        self.remove_pieces_with_no_blocks()
        self.rows_cleared += len(locations_to_delete)

    def get_block_count_per_row(self) -> Dict[int, int]:
        block_count_per_row = {}
        for piece in self.pieces:
            for block in piece.blocks:
                if block.center_y not in block_count_per_row:
                    block_count_per_row[block.center_y] = 1
                else:
                    block_count_per_row[block.center_y] += 1
        return block_count_per_row

    def get_locations_of_blocks_to_delete(
        self, block_count_per_row: Dict[int, int]
    ) -> List[int]:
        locations_of_blocks_to_delete = []
        for key, value in block_count_per_row.items():
            if value == HORIZONTAL_SQUARES:
                locations_of_blocks_to_delete.append(key)
        return locations_of_blocks_to_delete

    def remove_blocks(self, locations_to_delete: List[int]) -> None:
        for piece in self.pieces:
            for block in piece.blocks[:]:
                if block.center_y in locations_to_delete:
                    piece.blocks.remove(block)

    def remove_pieces_with_no_blocks(self) -> None:
        for piece in self.pieces[:]:
            if not piece.blocks:
                self.pieces.remove(piece)

    def drop_hanging_pieces(self) -> None:
        for piece in self.pieces:
            piece.drop(self.pieces)

    def on_draw(self) -> None:
        arcade.start_render()
        self.draw_grid()
        self.draw_next_piece_preview()
        self.draw_score()
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
            align="left",
        )

    def draw_reset_button_text(self) -> None:
        arcade.draw_text(
            "Reset", 384, 416, arcade.color.BABY_POWDER, 14, align="center"
        )


def main():
    Tetris()
    arcade.run()


if __name__ == "__main__":
    main()
