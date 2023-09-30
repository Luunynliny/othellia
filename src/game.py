import numpy as np

from settings.board import BOARD_CELL_LENGTH
from settings.cell_values import BLACK_VALUE, EMPTY_VALUE, WHITE_VALUE
from settings.directions import DIRECTIONS
from settings.graphics import WIDTH


class Game:
    """Class gathering all the game's behaviours.

    Args:
        width (int): width of the board.
        height (int): height if the board.
    """

    def __init__(self):
        self.reset_game()

    def reset_game(self):
        """Reset the game board into initial configuration."""
        self.board = np.full(
            (BOARD_CELL_LENGTH, BOARD_CELL_LENGTH), EMPTY_VALUE, dtype=int
        )

        self.play_piece((3, 3), WHITE_VALUE)
        self.play_piece((4, 4), WHITE_VALUE)
        self.play_piece((3, 4), BLACK_VALUE)
        self.play_piece((4, 3), BLACK_VALUE)

        self.update_surrounding_cells()
        self.update_sandwiches(BLACK_VALUE)
        self.update_indicators()

    def mouse_pos_to_cell_index(self, pos: tuple[int, int]) -> tuple[int, int]:
        """Convert a mouse position into a cell index.

        Args:
            pos (tuple[int, int]): x and y coordinates.

        Returns:
            tuple[int, int]: column and row indices.
        """
        x, y = pos
        cell_size = WIDTH / BOARD_CELL_LENGTH

        return (int(x // cell_size), int(y // cell_size))

    def is_cell_empty(self, cell_index: tuple[int, int]) -> bool:
        """Check if a cell doesn't contain  a piece.

        Args:
            cell_index (tuple[int, int]): cell's column and row.

        Returns:
            bool: non-presence of a piece.
        """
        col, row = cell_index
        return self.board[row, col] == EMPTY_VALUE

    def play_piece(self, cell_index: tuple[int, int], player_value: int):
        """Play a piece in a cell.

        Args:
            cell_index (tuple[int, int]): cell's column and row.
            player_value (int): value of the piece.
        """
        col, row = cell_index
        self.board[row, col] = player_value

    def is_move_legal(self, cell_index: tuple[int, int]) -> bool:
        """Ensure if a move is legal according to the current state of
        the board.

        Args:
            cell_index (tuple[int, int]): cell's column and row.

        Returns:
            bool: Legality of the move.
        """
        return np.any(np.all(self.indicators == cell_index, axis=1))

    def update_sandwiches(self, player_value: int):
        """Find all the sandwiches from available legal moves.

        Args:
            player_value (int): value of the piece.

        Returns:
            dict: sanwdiches for each possible move.
        """
        self.sandwiches = {}

        if self.surrounding_cells is not None:
            for cell_index in self.surrounding_cells:
                cell_sandwiches = self.search_cell_sandwiches(
                    cell_index, player_value
                )

                if cell_sandwiches is None:
                    continue

                x, y = cell_index
                self.sandwiches[f"{x},{y}"] = cell_sandwiches

    def search_cell_sandwiches(
        self, cell_index: tuple[int, int], player_value: int
    ) -> np.ndarray | None:
        """Find all possible sandwiches from a single cell.

        Args:
            cell_index (tuple[int, int]): cell's column and row.
            player_value (int): value of the piece.

        Returns:
            np.ndarray | None: cell indices within the sandwiches,
            None if no sandwiches.
        """
        sandwiches = []

        # Loop for sandwiches in all directions
        for direction in DIRECTIONS:
            cell_indices = self.search_cell_sandwich_towards(
                cell_index, player_value, direction
            )

            if cell_indices is None:
                continue

            sandwiches.extend(cell_indices)

        return np.array(sandwiches) if len(sandwiches) > 0 else None

    def search_cell_sandwich_towards(
        self,
        cell_index: tuple[int, int],
        player_value: int,
        direction: tuple[int, int],
    ) -> np.ndarray | None:
        """Find if a sanwich, if possible, in a given directory from a cell.

        Args:
            cell_index (tuple[int, int]): column and row of the cell.
            player_value (int): value of the piece.
            direction (tuple[int, int]): direction of the search.

        Returns:
            np.ndarray | None: cell indices within the sandwich, None if no sandwich.
        """
        consecutive = 0
        is_sandwich_end = False

        cvt = self.cell_values_toward(cell_index, direction)

        if cvt is None:
            return None

        for cell_value in cvt:
            # Check for the end of the sandwich
            if cell_value == player_value:
                is_sandwich_end = True
                break

            # Check if the cell has the opponent colour
            if cell_value != -player_value:
                break

            consecutive += 1

        x, y = cell_index
        dx, dy = direction

        return (
            np.array(
                [
                    (x + (dx * c), y + (dy * c))
                    for c in range(1, consecutive + 1)
                ],
                dtype=(int, 2),
            )
            if consecutive > 0 and is_sandwich_end
            else None
        )

    def cell_values_toward(
        self, cell_index: tuple[int, int], direction: tuple[int, int]
    ) -> np.ndarray | None:
        """Return all the cells value toward a cell in a given direction.

        Args:
            cell_index (tuple[int, int]): column and row of the cell.
            direction (tuple[int, int]): direction of the search.

        Returns:
            np.ndarray | None: cells value in the given direction.
        """
        x, y = cell_index
        values = None

        match direction:
            case (0, 1):
                values = self.board[y + 1 :, x]
            case (1, 0):
                values = self.board[y, x + 1 :]
            case (0, -1):
                values = self.board[:y, x][::-1]
            case (-1, 0):
                values = self.board[y, :x][::-1]
            case (1, 1):
                values = self.board[y + 1 :, x + 1 :].diagonal()
            case (1, -1):
                values = np.flipud(self.board[:y, x + 1 :]).diagonal()
            case (-1, 1):
                values = np.fliplr(self.board[y + 1 :, :x]).diagonal()
            case (-1, -1):
                values = np.flipud(np.fliplr(self.board[:y, :x])).diagonal()

        return values if len(values) > 0 else None

    def update_surrounding_cells(self):
        """Find the empty cells surrounding the pieces cluster."""
        surrounding_cells = []

        for cell_index in self.get_all_non_empty_cells():
            empty_neighbors = self.get_empty_neighbors(cell_index)

            if empty_neighbors is None:
                continue

            surrounding_cells.extend(empty_neighbors)

        self.surrounding_cells = (
            np.array(np.unique(surrounding_cells, axis=0))
            if len(surrounding_cells) > 0
            else None
        )

    def get_all_non_empty_cells(self) -> np.ndarray | None:
        """Return all non-empty cells on the board.

        Returns:
            np.ndarray | None: cells column and row, None if no empty cells.
        """
        cells = []

        for col in range(BOARD_CELL_LENGTH):
            for row in range(BOARD_CELL_LENGTH):
                value = self.board[row, col]

                if value == EMPTY_VALUE:
                    continue

                cells.append((col, row))

        return np.array(cells, dtype=(int, 2)) if len(cells) > 0 else None

    def get_empty_neighbors(
        self, cell_index: tuple[int, int]
    ) -> np.ndarray | None:
        """Retrieve all the empty neighbors of a given cell.

        Args:
            cell_index (tuple[int, int]): cell's column and row.

        Returns:
            np.ndarray | None: cells column and row, None if no empty neighbors.
        """
        row, col = cell_index
        neighbors = []

        # https://stackoverflow.com/a/67758639
        for y in range(-1, 2):
            for x in range(-1, 2):
                # No shifting case
                if x == 0 and y == 0:
                    continue

                nx = row + x
                ny = col + y

                # Check boundaries
                if (
                    nx < 0
                    or nx >= BOARD_CELL_LENGTH
                    or ny < 0
                    or ny >= BOARD_CELL_LENGTH
                ):
                    continue

                if self.board[ny, nx] != EMPTY_VALUE:
                    continue

                neighbors.append((nx, ny))

        return (
            np.array(neighbors, dtype=(int, 2)) if len(neighbors) > 0 else None
        )

    def update_indicators(self):
        """Update the move indicators positions according the possible sandwiches."""
        self.indicators = []

        if len(self.sandwiches) > 0:
            for k in self.sandwiches.keys():
                col, row = list(map(int, k.split(",")))
                self.indicators.append((col, row))

            self.indicators = np.array(self.indicators, dtype=(int, 2))
