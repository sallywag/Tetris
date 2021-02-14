from typing import List, Tuple, Optional, Any
from itertools import product
import random

import arcade


WINDOW_TITLE = "Tetris"
SCREEN_SIZE = {"width": 640, "height": 640}
HORIZONTAL_SQUARES = 10
VERTICAL_SQUARES = 18
SQUARE_SIZE = 32
MARGIN = SQUARE_SIZE * 2


class Block(arcade.SpriteSolidColor):
    def __init__(self, color: arcade.Color, center_x: float, center_y: float):
        super().__init__(SQUARE_SIZE, SQUARE_SIZE, color)
        self.center_x = center_x
        self.center_y = center_y


class TetrisPiece:
    def __init__(
        self,
        block_preview_locations: List[Tuple[float, float]],
        block_board_locations: List[Tuple[float, float]],
        color: arcade.Color,
        pivot_block_index: int = None,
    ):
        super().__init__()
        self.blocks = arcade.SpriteList()
        for location in block_preview_locations:
            self.blocks.append(Block(color, location[0], location[1]))
        self.block_board_locations = block_board_locations
        self.pivot_block = None
        if pivot_block_index:
            self.pivot_block = self.blocks[pivot_block_index]
        self.falling = True

    def draw(self) -> None:
        for block in self.blocks:
            block.draw()

    def move_piece_to_board(self) -> None:
        for block, location in zip(self.blocks, self.block_board_locations):
            block.center_x = location[0]
            block.center_y = location[1]

    def rotate(self, other_pieces: List["TetrisPiece"]) -> None:
        if self.pivot_block is not None:
            for block in self.blocks:
                if block is not self.pivot_block:
                    self.rotate_block(block, clockwise=False)
            self.undo_rotation_if_collision_occurs(other_pieces)

    def rotate_block(self, block: Block, clockwise: bool) -> None:
        x_difference = block.center_x - self.pivot_block.center_x
        y_difference = block.center_y - self.pivot_block.center_y
        if not clockwise:
            new_x = 0 * x_difference + -1 * y_difference
            new_y = 1 * x_difference + 0 * y_difference
        else:
            new_x = 0 * x_difference + 1 * y_difference
            new_y = -1 * x_difference + 0 * y_difference
        block.center_x, block.center_y = (
            self.pivot_block.center_x + new_x,
            self.pivot_block.center_y + new_y,
        )

    def undo_rotation_if_collision_occurs(
        self, other_pieces: List["TetrisPiece"]
    ) -> None:
        if (
            self.collides_with_other_pieces(other_pieces)
            or self.past_top_edge()
            or self.past_bottom_edge()
            or self.past_left_edge()
            or self.past_right_edge()
        ):
            for block in self.blocks:
                if block is not self.pivot_block:
                    self.rotate_block(block, clockwise=True)

    def past_top_edge(self) -> bool:
        return any(
            block.center_y > VERTICAL_SQUARES * SQUARE_SIZE + MARGIN - SQUARE_SIZE
            for block in self.blocks
        )

    def past_bottom_edge(self) -> bool:
        return any(block.center_y < MARGIN for block in self.blocks)

    def past_left_edge(self) -> bool:
        return any(block.center_x < 0 + MARGIN for block in self.blocks)

    def past_right_edge(self) -> bool:
        return any(
            block.center_x > HORIZONTAL_SQUARES * SQUARE_SIZE + SQUARE_SIZE
            for block in self.blocks
        )

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
        return any(block.center_y == MARGIN for block in self.blocks)

    def at_left_edge(self) -> bool:
        return any(block.center_x == 0 + MARGIN for block in self.blocks)

    def at_right_edge(self) -> bool:
        return any(
            block.center_x == HORIZONTAL_SQUARES * SQUARE_SIZE + SQUARE_SIZE
            for block in self.blocks
        )

    def collides_with_other_pieces(self, other_pieces: List["TetrisPiece"]) -> bool:
        for piece in other_pieces:
            if any(block.collides_with_list(piece.blocks) for block in self.blocks):
                return True
        return False

    def collapse(self) -> None:
        bottom_block = min(self.blocks, key=lambda block: block.center_y)
        lower_blocks = [
            block for block in self.blocks if block.center_y == bottom_block.center_y
        ]
        upper_blocks = [
            block for block in self.blocks if block.center_y != bottom_block.center_y
        ]
        if upper_blocks:
            while True:
                for block in upper_blocks:
                    block.center_y -= SQUARE_SIZE
                if any(
                    u_b.collides_with_sprite(l_b)
                    for u_b in upper_blocks
                    for l_b in lower_blocks
                ):
                    for block in upper_blocks:
                        block.center_y += SQUARE_SIZE
                    break
                if any(
                    block.center_y == bottom_block.center_y for block in upper_blocks
                ):
                    break


class OPiece(TetrisPiece):
    def __init__(self):
        super().__init__(
            block_preview_locations=[
                (SQUARE_SIZE * 13 + SQUARE_SIZE / 2, SQUARE_SIZE * 17),
                (SQUARE_SIZE * 14 + SQUARE_SIZE / 2, SQUARE_SIZE * 17),
                (SQUARE_SIZE * 13 + SQUARE_SIZE / 2, SQUARE_SIZE * 18),
                (SQUARE_SIZE * 14 + SQUARE_SIZE / 2, SQUARE_SIZE * 18),
            ],
            block_board_locations=[
                (SQUARE_SIZE * 6, SQUARE_SIZE * 18),
                (SQUARE_SIZE * 7, SQUARE_SIZE * 18),
                (SQUARE_SIZE * 6, SQUARE_SIZE * 19),
                (SQUARE_SIZE * 7, SQUARE_SIZE * 19),
            ],
            color=arcade.color.RED,
        )


class TPiece(TetrisPiece):
    def __init__(self):
        super().__init__(
            block_preview_locations=[
                (SQUARE_SIZE * 14, SQUARE_SIZE * 17),
                (SQUARE_SIZE * 13, SQUARE_SIZE * 18),
                (SQUARE_SIZE * 14, SQUARE_SIZE * 18),
                (SQUARE_SIZE * 15, SQUARE_SIZE * 18),
            ],
            block_board_locations=[
                (SQUARE_SIZE * 7, SQUARE_SIZE * 18),
                (SQUARE_SIZE * 6, SQUARE_SIZE * 19),
                (SQUARE_SIZE * 7, SQUARE_SIZE * 19),
                (SQUARE_SIZE * 8, SQUARE_SIZE * 19),
            ],
            color=arcade.color.PURPLE,
            pivot_block_index=2,
        )


class IPiece(TetrisPiece):
    def __init__(self):
        super().__init__(
            block_preview_locations=[
                (
                    SQUARE_SIZE * 13 - SQUARE_SIZE / 2,
                    SQUARE_SIZE * 18 - SQUARE_SIZE / 2,
                ),
                (
                    SQUARE_SIZE * 14 - SQUARE_SIZE / 2,
                    SQUARE_SIZE * 18 - SQUARE_SIZE / 2,
                ),
                (
                    SQUARE_SIZE * 15 - SQUARE_SIZE / 2,
                    SQUARE_SIZE * 18 - SQUARE_SIZE / 2,
                ),
                (
                    SQUARE_SIZE * 16 - SQUARE_SIZE / 2,
                    SQUARE_SIZE * 18 - SQUARE_SIZE / 2,
                ),
            ],
            block_board_locations=[
                (SQUARE_SIZE * 6, SQUARE_SIZE * 19),
                (SQUARE_SIZE * 7, SQUARE_SIZE * 19),
                (SQUARE_SIZE * 8, SQUARE_SIZE * 19),
                (SQUARE_SIZE * 9, SQUARE_SIZE * 19),
            ],
            color=arcade.color.YELLOW,
            pivot_block_index=1,
        )


class JPiece(TetrisPiece):
    def __init__(self):
        super().__init__(
            block_preview_locations=[
                (SQUARE_SIZE * 16 - SQUARE_SIZE, SQUARE_SIZE * 18 - SQUARE_SIZE),
                (SQUARE_SIZE * 14 - SQUARE_SIZE, SQUARE_SIZE * 19 - SQUARE_SIZE),
                (SQUARE_SIZE * 15 - SQUARE_SIZE, SQUARE_SIZE * 19 - SQUARE_SIZE),
                (SQUARE_SIZE * 16 - SQUARE_SIZE, SQUARE_SIZE * 19 - SQUARE_SIZE),
            ],
            block_board_locations=[
                (SQUARE_SIZE * 8, SQUARE_SIZE * 18),
                (SQUARE_SIZE * 6, SQUARE_SIZE * 19),
                (SQUARE_SIZE * 7, SQUARE_SIZE * 19),
                (SQUARE_SIZE * 8, SQUARE_SIZE * 19),
            ],
            color=arcade.color.BLUE,
            pivot_block_index=2,
        )


class LPiece(TetrisPiece):
    def __init__(self):
        super().__init__(
            block_preview_locations=[
                (SQUARE_SIZE * 14 - SQUARE_SIZE, SQUARE_SIZE * 18 - SQUARE_SIZE),
                (SQUARE_SIZE * 14 - SQUARE_SIZE, SQUARE_SIZE * 19 - SQUARE_SIZE),
                (SQUARE_SIZE * 15 - SQUARE_SIZE, SQUARE_SIZE * 19 - SQUARE_SIZE),
                (SQUARE_SIZE * 16 - SQUARE_SIZE, SQUARE_SIZE * 19 - SQUARE_SIZE),
            ],
            block_board_locations=[
                (SQUARE_SIZE * 6, SQUARE_SIZE * 18),
                (SQUARE_SIZE * 6, SQUARE_SIZE * 19),
                (SQUARE_SIZE * 7, SQUARE_SIZE * 19),
                (SQUARE_SIZE * 8, SQUARE_SIZE * 19),
            ],
            color=arcade.color.GREEN,
            pivot_block_index=2,
        )


class SPiece(TetrisPiece):
    def __init__(self):
        super().__init__(
            block_preview_locations=[
                (SQUARE_SIZE * 14 - SQUARE_SIZE, SQUARE_SIZE * 18 - SQUARE_SIZE),
                (SQUARE_SIZE * 15 - SQUARE_SIZE, SQUARE_SIZE * 18 - SQUARE_SIZE),
                (SQUARE_SIZE * 15 - SQUARE_SIZE, SQUARE_SIZE * 19 - SQUARE_SIZE),
                (SQUARE_SIZE * 16 - SQUARE_SIZE, SQUARE_SIZE * 19 - SQUARE_SIZE),
            ],
            block_board_locations=[
                (SQUARE_SIZE * 6, SQUARE_SIZE * 18),
                (SQUARE_SIZE * 7, SQUARE_SIZE * 18),
                (SQUARE_SIZE * 7, SQUARE_SIZE * 19),
                (SQUARE_SIZE * 8, SQUARE_SIZE * 19),
            ],
            color=arcade.color.NEON_FUCHSIA,
            pivot_block_index=2,
        )


class ZPiece(TetrisPiece):
    def __init__(self):
        super().__init__(
            block_preview_locations=[
                (SQUARE_SIZE * 15 - SQUARE_SIZE, SQUARE_SIZE * 18 - SQUARE_SIZE),
                (SQUARE_SIZE * 16 - SQUARE_SIZE, SQUARE_SIZE * 18 - SQUARE_SIZE),
                (SQUARE_SIZE * 14 - SQUARE_SIZE, SQUARE_SIZE * 19 - SQUARE_SIZE),
                (SQUARE_SIZE * 15 - SQUARE_SIZE, SQUARE_SIZE * 19 - SQUARE_SIZE),
            ],
            block_board_locations=[
                (SQUARE_SIZE * 7, SQUARE_SIZE * 18),
                (SQUARE_SIZE * 8, SQUARE_SIZE * 18),
                (SQUARE_SIZE * 6, SQUARE_SIZE * 19),
                (SQUARE_SIZE * 7, SQUARE_SIZE * 19),
            ],
            color=arcade.color.GRAY_BLUE,
            pivot_block_index=3,
        )


class Tetris(arcade.Window):
    def __init__(self):
        super().__init__(SCREEN_SIZE["width"], SCREEN_SIZE["height"], WINDOW_TITLE)
        arcade.set_background_color(arcade.color.BLACK)
        self.current_piece = None
        self.pieces = None
        self.next_piece = None
        self.rows_cleared = None
        self.frame_count = None
        self.game_over = None
        self.frames_per_drop = 20
        self.setup()

    def setup(self) -> None:
        self.current_piece = self.get_random_piece()
        self.current_piece.move_piece_to_board()
        self.pieces = [self.current_piece]
        self.next_piece = self.get_random_piece()
        self.rows_cleared = 0
        self.frame_count = 0
        self.frames_per_drop = 20
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

    def on_mouse_press(self, x: float, y: float, button: int, modifiers: int) -> None:
        if self.game_over and button == arcade.MOUSE_BUTTON_LEFT:
            self.game_over = False
            self.setup()

    def on_update(self, delta_time: float) -> None:
        if not self.game_over:
            if self.frame_count == self.frames_per_drop:
                self.current_piece.move_down(self.pieces)
                self.frame_count = 0
            else:
                self.frame_count += 1
            if not self.current_piece.falling:
                self.ready_next_piece()
                self.clear_full_rows()
                if self.current_piece.collides_with_other_pieces(self.pieces):
                    self.game_over = True

    def ready_next_piece(self) -> None:
        self.current_piece = self.next_piece
        self.current_piece.move_piece_to_board()
        self.pieces.append(self.current_piece)
        self.next_piece = self.get_random_piece()

    def get_random_piece(self) -> TetrisPiece:
        return random.choice([OPiece, TPiece, IPiece, JPiece, LPiece, SPiece, ZPiece])()

    def clear_full_rows(self) -> None:
        while locations_to_delete := self.get_locations_of_blocks_to_delete():
            self.remove_blocks(locations_to_delete)
            self.collapse_pieces()
            self.drop_hanging_pieces()
            self.rows_cleared += len(locations_to_delete)

    def get_locations_of_blocks_to_delete(self) -> List[Any]:
        block_count_per_row = {}
        full_row_locations = []
        for piece in self.pieces:
            for block in piece.blocks:
                if block.center_y not in block_count_per_row:
                    block_count_per_row[block.center_y] = 1
                else:
                    block_count_per_row[block.center_y] += 1
                if block_count_per_row[block.center_y] == HORIZONTAL_SQUARES:
                    full_row_locations.append(block.center_y)
        return full_row_locations

    def remove_blocks(self, locations_to_delete: List[int]) -> None:
        for piece in self.pieces[:]:
            for block in piece.blocks[:]:
                if block.center_y in locations_to_delete:
                    piece.blocks.remove(block)
            if not piece.blocks:
                self.pieces.remove(piece)

    def collapse_pieces(self) -> None:
        for piece in self.pieces:
            piece.collapse()

    def drop_hanging_pieces(self) -> None:
        for piece in self.pieces:
            if piece is not self.current_piece:
                piece.drop(self.pieces)

    def on_draw(self) -> None:
        arcade.start_render()
        self.draw_grid()
        self.draw_next_piece_preview_box()
        self.next_piece.draw()
        self.draw_score()
        for piece in self.pieces:
            piece.draw()
        if self.game_over:
            self.draw_transparent_overlay()
            self.draw_reset_helper_text()

    def draw_grid(self) -> None:
        for x, y in product(
            range(MARGIN, SQUARE_SIZE * HORIZONTAL_SQUARES + MARGIN, SQUARE_SIZE),
            range(MARGIN, SQUARE_SIZE * VERTICAL_SQUARES + MARGIN, SQUARE_SIZE),
        ):
            arcade.draw_rectangle_outline(
                x, y, SQUARE_SIZE, SQUARE_SIZE, arcade.color.BABY_PINK, 2
            )

    def draw_next_piece_preview_box(self) -> None:
        arcade.draw_rectangle_outline(
            HORIZONTAL_SQUARES * SQUARE_SIZE + SQUARE_SIZE * 2 + MARGIN,
            VERTICAL_SQUARES * SQUARE_SIZE - SQUARE_SIZE / 2,
            SQUARE_SIZE * 4,
            SQUARE_SIZE * 4,
            arcade.color.BABY_BLUE,
            2,
        )

    def draw_score(self) -> None:
        arcade.draw_text(
            f"Rows Cleared: {self.rows_cleared}",
            SQUARE_SIZE * 12,
            SQUARE_SIZE * 14,
            arcade.color.BABY_POWDER,
            14,
            align="left",
        )

    def draw_transparent_overlay(self) -> None:
        arcade.draw_rectangle_filled(
            MARGIN + SQUARE_SIZE * HORIZONTAL_SQUARES / 2 - SQUARE_SIZE / 2,
            MARGIN + SQUARE_SIZE * VERTICAL_SQUARES / 2 - SQUARE_SIZE / 2,
            SQUARE_SIZE * HORIZONTAL_SQUARES,
            SQUARE_SIZE * VERTICAL_SQUARES,
            arcade.make_transparent_color(arcade.color.TEAL, 150),
        )

    def draw_reset_helper_text(self) -> None:
        arcade.draw_text(
            "Left click to restart...",
            SQUARE_SIZE * 12,
            SQUARE_SIZE * 13,
            arcade.color.NEON_CARROT,
            18,
            align="left",
        )


def main():
    Tetris()
    arcade.run()


if __name__ == "__main__":
    main()
