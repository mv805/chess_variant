from __future__ import annotations

class ChessVar:
    """A ChessVar class to play a variation of Chess.
    See https://en.wikipedia.org/wiki/V._R._Parton#Dodo_chess for rules.
    """

    _default_wht_start_pos = (
        ("KING", "a1", 1),
        ("ROOK", "a2", 1),
        ("BISHOP", "b1", 1),
        ("BISHOP", "b2", 2),
        ("KNIGHT", "c1", 1),
        ("KNIGHT", "c2", 2),
    )
    _default_blk_start_pos = (
        ("KING", "h1", 1),
        ("ROOK", "h2", 1),
        ("BISHOP", "g1", 1),
        ("BISHOP", "g2", 2),
        ("KNIGHT", "f1", 1),
        ("KNIGHT", "f2", 2),
    )

    def __init__(
        self,
        wht_start_pos: tuple[tuple[str, str, int], ...] = None,
        blk_start_pos: tuple[tuple[str, str, int], ...] = None,
    ) -> None:
        """Initializes the ChessVar object.

        Args:
            wht_start_pos (tuple[tuple[str, str, int],...], optional): Initial starting positions for white player. Defaults to None.

            blk_start_pos (tuple[tuple[str, str, int],...], optional): Initial starting positions for black player. Defaults to None.

            Position tuple format: (str, str, int), or (piece type, starting coord, unique id)
            Example:
                (("KING", "a1", 1), ("ROOK", "a2", 1)...)
        """

        self._game_state = "UNFINISHED"  # initial game state
        self._game_board = []  # game board, 2D list
        self._white_player = None  # a Player object
        self._black_player = None  # a Player object
        self._whos_turn_it_is = None  # a Player Object
        self._players_with_kings_in_last_row = (
            []  # list of the current players with kings at the end
        )

        # if a custom start position is given, initialize the board and players with that
        if wht_start_pos is not None or blk_start_pos is not None:
            self._initialize_game(wht_start_pos, blk_start_pos)
        else:
            self._initialize_game(
                self._default_wht_start_pos, self._default_blk_start_pos
            )

    def get_game_state(self) -> str:
        """Returns the current game state.

        Returns:
            str: game state. i.e. "UNFINISHED", "WHITE_WON", "BLACK_WON", "TIE", "STALEMATE"
        """
        return self._game_state

    def _move_is_valid(self, source_coord: str, dest_coord: str) -> bool:
        """Validate if a given potential move is a legal move.

        Args:
            source_coord (str): source coordinate from the chess board. i.e. "a1"
            dest_coord (str): destination coordinate from the chess board. i.e. "a1"

        Returns:
            bool: False if not a legal move, True if otherwise
        """

        source_row_index, source_col_index = get_index_from_coord(
            [character for character in source_coord]
        )

        piece_to_move = self._game_board[source_row_index][source_col_index]

        # if the source location is empty
        if piece_to_move is None:
            return False

        # source piece does not belong to the current player
        elif piece_to_move.get_player() is not self._whos_turn_it_is:
            return False

        # destination is not in the pieces valid moves list for the piece
        # also catches no more moves possibly
        elif dest_coord not in piece_to_move.get_valid_moves():
            return False

        else:
            return True

    def get_players_with_kings_in_last_row(self) -> set[Player]:
        """Returns the players that have kings in the final row (8)

        Returns:
            set[Player]: A set of all the players with kings in the last row
        """
        return self._players_with_kings_in_last_row

    def make_move(self, source_coord: str, dest_coord: str) -> bool:
        """Makes a move, given a source and destination coord.

        Args:
            source_coord (str): source coordinate from the chess board. i.e. "a1"
            dest_coord (str): destination coordinate from the chess board. i.e. "a1"

        Returns:
            bool: True if the move was valid and executed, False if not.
        """
        # game is already over
        if self._game_state != "UNFINISHED":
            return False

        elif not self._move_is_valid(source_coord, dest_coord):
            return False

        # if the player cant move anymore, so stalemate for current player
        elif len(self._whos_turn_it_is.get_valid_moves()) == 0:
            self._game_state = "STALEMATE"
            False

        # make the move if its ok to do so
        else:
            destination_piece, source_piece = self._move_piece(
                source_coord, dest_coord
            )

        # if a king is in check, undo the move and exit with false
        if (
            self._black_player.get_king().get_pos()
            in self._white_player.get_valid_moves()  # the black players king is in check
            or self._white_player.get_king().get_pos()
            in self._black_player.get_valid_moves()  # the white players king is in check
        ):
            old_source_row_index, old_source_col_index = get_index_from_coord(
                source_coord
            )

            old_dest_row_index, old_dest_col_index = get_index_from_coord(dest_coord)

            # reset the source piece location
            self._game_board[old_source_row_index][old_source_col_index] = source_piece
            source_piece.set_current_pos(source_coord)

            # if a destination piece was removed, reset its position
            if destination_piece:
                self._game_board[old_dest_row_index][
                    old_dest_col_index
                ] = destination_piece
                destination_piece.set_current_pos(dest_coord)
                # add the destination back into the players collection
                destination_piece.get_player().add_piece(destination_piece)
            else:  # restore it to empty square
                self._game_board[old_dest_row_index][old_dest_col_index] = None

            return False

        # check if the king made it to the last row
        king_pos_row, king_pos_col = get_index_from_coord(
            self._whos_turn_it_is.get_king().get_pos()
        )

        if king_pos_row == 0:
            self._players_with_kings_in_last_row.append(self._whos_turn_it_is)

        # if the other player was already there then its a tie
        if len(self._players_with_kings_in_last_row) == 2:
            self._game_state = "TIE"
            return True

        if len(self._players_with_kings_in_last_row) == 1 and king_pos_row != 0:
            self._game_state = (
                f"{self._players_with_kings_in_last_row[0].get_color()}_WON"
            )
            return True

        # switch to other player
        if self._whos_turn_it_is.get_color() == "WHITE":
            self._whos_turn_it_is = self.get_player("BLACK")
        elif self._whos_turn_it_is.get_color() == "BLACK":
            self._whos_turn_it_is = self.get_player("WHITE")

        return True

    def _update_valid_moves_for_all_players(self) -> None:
        """Update all the valid moves for both white and black players."""
        self._white_player.update_valid_moves(self._game_board)
        self._black_player.update_valid_moves(self._game_board)

    def _move_piece(
        self, source: str, dest_coord: str
    ) -> tuple[ChessPiece | None, ChessPiece]:
        """Move a piece from source to destination on a given gameboard.

        Args:
            source (str): source coordinate from the chess board. i.e. "a1"
            destination (str): destination coordinate from the chess board. i.e. "a1"

        Returns:
            tuple['ChessPiece' | None, ChessPiece]:
                returns the chess pieces. i.e. (destination piece, moving piece). If no destination piece, will return None.
        """

        # swap the source piece to the destination square
        destination_row, destination_col = get_index_from_coord(
            [character for character in dest_coord]
        )
        source_row, source_col = get_index_from_coord(
            [character for character in source]
        )
        destination_piece_to_remove = self._game_board[destination_row][destination_col]
        source_piece_to_move = self._game_board[source_row][source_col]

        # move the source piece to the destination
        self._game_board[destination_row][destination_col] = source_piece_to_move

        # empty the source position now after the move
        self._game_board[source_row][source_col] = None

        # update the new pos of the moved piece
        source_piece_to_move.set_current_pos(dest_coord)

        # if the destination has a players piece, remove it from that players collection
        if destination_piece_to_remove is not None:
            destination_piece_to_remove.get_player().remove_piece(
                destination_piece_to_remove
            )

        # update the player valid moves with the new gameboard configuration
        self._update_valid_moves_for_all_players()

        return (destination_piece_to_remove, source_piece_to_move)

    def _initialize_game(
        self,
        white_starting_positions: tuple[tuple[str, str, int], ...],
        black_starting_positions: tuple[tuple[str, str, int], ...],
    ) -> None:
        """Initializes the players and game board with the starting locations.

        Args:
            white_starting_positions (tuple[tuple[str, str, int], ...]): Initial starting positions for white player.
            black_starting_positions (tuple[tuple[str, str, int], ...]): Initial starting positions for black player.

            Position tuple format: (str, str, int), or (piece type, starting coord, unique id)
            Example:
                (("KING", "a1", 1), ("ROOK", "a2", 1)...)
        """
        # create the players
        self._white_player = Player("WHITE", white_starting_positions)
        self._black_player = Player("BLACK", black_starting_positions)

        # set the current player whos turn it is
        self._whos_turn_it_is = self._white_player

        # fill a blank board
        for row in range(8):
            self._game_board.append([])
            for column in range(8):
                self._game_board[row].append(None)

        # place the player starting pieces on the board
        for piece in self._white_player.get_pieces():
            self._place_piece(piece)

        for piece in self._black_player.get_pieces():
            self._place_piece(piece)

        # update the valid moves of the players
        self._update_valid_moves_for_all_players()

    def _place_piece(
        self, piece: ChessPiece
    ) -> None:
        """Places a piece on the board per its current position.

        Args:
            piece (ChessPiece): A chess piece to place on the gameboard
        """
        row, col = get_index_from_coord(piece.get_pos())
        self._game_board[row][col] = piece

    def render_board(self)->list[list[str]]:
        """converts the game board to a string format for displaying to some GUI

        Returns:
            list[list[str]]: The game board in 2d string list format.
            Example:
                [[" ","-","-","-"]]
                [["2","|","|","|"]]
                [[" ","-","|","-"]]
                [["1","|","|","|"]]
                [[" ","-","-","-"]]
                [[" "," ","a"," "]]
        """
        
        # fmt: off
        board = [
            [" "," ","a"," ","b"," ","c"," ","d"," ","e"," ","f"," ","g"," ","h"," "],
            [" ","▪","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","▪"]
        ]
        

        for index, row in enumerate(self._game_board, start=-len(self._game_board)):
            new_row = [f"{abs(index)}", "|"]
            for square in row:
                if square is not None:
                    new_row.append(f"{square.get_symbol()}")
                else:
                    new_row.append(" ")
                new_row.append("|")
            new_row.append(f"{abs(index)}")
            board.append(new_row)
        
            board.append( [" ","▪","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","▪"])      
        board.append([" "," ","a"," ","b"," ","c"," ","d"," ","e"," ","f"," ","g"," ","h"," "])
        # fmt: on
        return board

    def set_game_state(self, new_state: str) -> None:
        """Sets the game state.

        Args:
            new_state (str): game state. Should be set to one of the following - "UNFINISHED", "WHITE_WON", "BLACK_WON", "TIE", "STALEMATE"
        """
        self._game_state = new_state

    def get_game_board(self) -> list[list[str | ChessPiece]]:
        """Returns the game board 2D array.

        Returns:
            list[list[str | "ChessPiece"]]: The current game board, passed by reference
        """
        return self._game_board

    def get_whos_turn_it_is(self) -> Player:
        """Returns the player whos turn it is.

        Returns:
            Player: The player whos turn it is
        """
        return self._whos_turn_it_is

    def get_player(self, color: str) -> Player | None:
        """Returns the player associated with the given color.

        Returns:
            'Player'|None: Returns the player or None if the color does not match a player
        """
        if color == "BLACK":
            return self._black_player
        elif color == "WHITE":
            return self._white_player
        else:
            return None

class InvalidInputError(Exception):
    """An error for inputing an invalid entry for a move choice."""

    pass


class Display:
    """A class used to prompt user for data and display it to the terminal. For use with the Chess Var game class."""

    def print_board(self, game: ChessVar) -> None:
        """Prints the game board to the terminal.

        Args:
            game (ChessVar): A ChessVar class object that has been initialized
        """
        board = game.render_board()
        for row in board:
            for character in row:
                print(character, end=" ")
            print()

    def prompt_move(self, color: str) -> tuple[str, str]:
        """Prompt the player for the move they would like to make (From terminal)

        Args:
            color (str): The color of the player to prompt

        Raises:
            InvalidInputError: first raised if not a valid source or destination selection
            InvalidInputError: second raised if the source and destination are the same

        Returns:
            tuple[str, str]: The chosen piece location and destination coordinates. i.e. ("e4", "c5") or (source, dest)
        """
        print(f"{color}, it is your turn.")
        source_piece_coord = input("Enter which piece you would like to move: ")
        destination_coord = input("Enter where you would like to move the piece: ")

        if (
            self._is_valid_coordinate(source_piece_coord) == False
            or self._is_valid_coordinate(destination_coord) == False
        ):
            raise InvalidInputError
        elif source_piece_coord == destination_coord:
            raise InvalidInputError
        else:
            return (source_piece_coord, destination_coord)

    def print_introduction(self) -> None:
        """Prints the introductory statements and instructions."""
        print(
            "Welcome to Dodo Chess! White goes first. First king to reach row 8 wins. Please enter moves in letter number format such as 'a1', 'b2' etc. The white pieces are on the left and black on the right. Have fun!"
        )

    def print_end_game_prompt(self) -> None:
        """Prints end game statement."""
        print("The game is over. Thanks for playing!")

    def print_invalid_input_error(self) -> None:
        """Prints the invalid input error."""
        print("Invalid input, please try again...")

    def print_king_in_check_error(self) -> None:
        """Prints the error that a king is in check."""
        print("Invalid move. A King would be in check...")

    def print_invalid_move_error(self) -> None:
        """Prints the error that the move given is invalid."""
        print("That is not a legal move, please try again...")

    def _is_valid_coordinate(self, coord: str) -> bool:
        """Determines if a given input is a valid coordinate on the chess board.

        Args:
            coord (str): the given user coordinate inpue. i.e. "a1"

        Returns:
            bool: True if it is valid board selection. False if otherwise
        """
        valid_columns = {"a", "b", "c", "d", "e", "f", "g", "h"}
        valid_rows = {"1", "2", "3", "4", "5", "6", "7", "8"}

        if len(coord) > 2 or len(coord) < 2:
            return False
        elif coord is None:
            return False

        col, row = [character for character in coord]

        if col not in valid_columns or row not in valid_rows:
            return False
        else:
            return True

    def get_game_state_message(self, game_state: str) -> str:
        """Gets the end game statement depending on the game state

        Args:
            game_state (str): The current state of the game

        Returns:
            str: the end game statement
        """
        if game_state == "TIE":
            return "The game ended in a tie!"
        elif game_state == "BLACK_WON":
            return "The Black player has won the game!"
        elif game_state == "WHITE_WON":
            return "The White player has won the game!"
        elif game_state == "STALEMATE":
            return "No more moves! The game is over!"
        else:
            return "The next players turn shall begin now..."


class Player:
    """A Player for the ChessVar game."""

    def __init__(
        self,
        color: str,
        starting_configuration: tuple[tuple[str, str, int], ...] | None,
    ) -> None:
        """Initializes the player object.

        Args:
            color (str): color of the player. Should be "WHITE" or "BLACK".
            starting_configuration (tuple[tuple[str, str, int], ...] | None): the starting piece types and their positions, and id

            configuration tuple format: (str, str, int), or (piece type, starting coord, unique id)
            Example:
                (("KING", "a1", 1), ("ROOK", "a2", 1)...)
        """
        self._chess_pieces = (
            set()
        )  # {ChessPiece Objects...}, all the the pieces the player has
        self._all_valid_moves = (
            set()
        )  # {positions...}, a position is a string "XX" of valid moves
        self._color = color  # strings, "WHITE" or "BLACK"
        self._king = None  # a king object, the players king

        self._initialize_start_configuration(starting_configuration)

    def get_valid_moves(self) -> set[str]:
        """Returns all of the valid moves from all of the players pieces. Taken from the time of the last game board update.

        Returns:
            set[str]: A set of all the valid moves. i.e. {"a1","b3",...}
        """
        return self._all_valid_moves

    def update_valid_moves(self, game_board: list[list[str | ChessPiece]]) -> None:
        """Updates the valid moves set, given the game board configuration.

        Args:
            game_board (list[list[str | 'ChessPiece']]): A game board
        """

        for piece in self._chess_pieces:
            piece.update_valid_moves(game_board)

        self._all_valid_moves = set()
        for piece in self._chess_pieces:
            self._all_valid_moves.update(piece.get_valid_moves())

    def get_piece_by_id(self, piece_to_find: str, id: int) -> None | str:
        """Returns a piece from the players active pieces that match a specific id.

        Args:
            piece_to_find (str): the type of piece. i.e. "ROOK", "KNIGHT" etc.
            id (int): the id of the piece

        Returns:
            None | str: returns the piece if found, otherwise returns None
        """

        for piece in self._chess_pieces:
            if piece.get_id() == id and piece_to_find == piece.get_piece_type():
                return piece
        return None

    def remove_piece(self, piece_to_remove: ChessPiece) -> None:
        """Removes the given piece from the players collection of pieces

        Args:
            piece_to_remove (ChessPiece): A chess piece to remove from the players pieces collection.
        """
        self._chess_pieces.remove(piece_to_remove)

    def add_piece(self, piece_to_add: ChessPiece) -> None:
        """Adds the given piece to the players collection

        Args:
            piece_to_add (ChessPiece): A chess piece to add
        """
        self._chess_pieces.add(piece_to_add)

    def _initialize_start_configuration(
        self, starting_configuration: tuple[tuple[str, str, int], ...] | None
    ) -> None:
        """Initializes the starting pieces for the player at board locations given with given ids.

        Args:
            starting_pieces_and_positions (tuple[tuple[str, str, int], ...] | None): the starting piece types and their positions, and id

            configuration tuple format: (str, str, int), or (piece type, starting coord, unique id)
            Example:
                (("KING", "a1", 1), ("ROOK", "a2", 1)...)
        """
        if starting_configuration is not None:
            for piece, pos, piece_id in starting_configuration:
                if piece == "KING":
                    self._king = King(self, pos, piece_id, piece)
                    self._chess_pieces.add(self._king)
                elif piece == "ROOK":
                    self._chess_pieces.add(Rook(self, pos, piece_id, piece))
                elif piece == "BISHOP":
                    self._chess_pieces.add(Bishop(self, pos, piece_id, piece))
                elif piece == "KNIGHT":
                    self._chess_pieces.add(Knight(self, pos, piece_id, piece))

    def get_color(self) -> str:
        """Returns the color of the player

        Returns:
            str: player color, "BLACK" or "WHITE"
        """
        return self._color

    def get_pieces(self) -> set[ChessPiece]:
        """Gets all the pieces in the players active played pieces.

        Returns:
            set['ChessPiece']: All the players current chess pieces
        """
        return self._chess_pieces

    def get_king(self) -> "King":
        """Get reference to the players king.

        Returns:
            King: The players king
        """
        return self._king


class ChessPiece:
    def __init__(self, player: Player, starting_coord: str, id: int, type: str) -> None:
        """Initializes the Chess Piece

        Args:
            player (Player): The player who will own this piece (Player Object)
            starting_coord (str): the starting board coordinate. i.e. "a1"
            id (int): The id of the piece
            type (str): The type of the piece. i.e. "ROOK", "KNIGHT" etc.
        """
        self._current_coord = starting_coord  # pos in 'a1" format
        self._valid_moves = set()  # all moves in {"a1","b2"...} format
        self._player = player  # Player object instance
        self._symbol = None  # a string symbol for the chess piece
        self._id = id
        self._type = type #"ROOK" or "BISHOP" etc.

    def get_id(self) -> int:
        """Get the pieces unique id.

        Returns:
            int: the piece id.
        """
        return self._id

    def set_current_pos(self, coord: str) -> None:
        """Sets the current piece position coordinate

        Args:
            coord (str): A given board coordinte. i.e. "a1", "b3" ...
        """
        self._current_coord = coord

    def get_pos(self):
        return self._current_coord

    def update_valid_moves(self) -> None:
        """Update all the valid moves for the given piece, given a board configuration.

        Args:
            game_board (list[list[str | 'ChessPiece']]): A game board 2d list

        Raises:
            NotImplementedError: If the function is not implemented at subclass level, will raise this.
        """
        # needs to be implemented at each piece subclass level
        raise NotImplementedError

    def get_player(self) -> Player:
        """Gets the player who owns this piece this is (white or black).

        Returns:
            Player : a game player, white or black
        """
        return self._player

    def get_symbol(self) -> str:
        """Gets the piece printing symbol.

        Returns:
            str: The Unicode chess symbol of the piece.
        """
        return self._symbol

    def get_valid_moves(self) -> set[str]:
        """Get all the valid moves of the piece.

        Returns:
            set[str]: A set of all the valid move board coordinates. i.e. {"a3","b4",...}
        """
        return self._valid_moves

    def get_piece_type(self) -> str:
        """Returns the piece type

        Returns:
            str: the piece type. i.e. "ROOK", "KNIGHT" etc.
        """
        return self._type

    def _update_single_square_moves(
        self,
        direction_offsets: dict[str, tuple[int, int]],
        game_board: list[list[str | ChessPiece]],
    ) -> set[str]:
        """Sets the piece valid moves list, given offsets and a game board.

        The offsets are a series of directions and distances that will be checked sequentially for valid movement. Only the King and Knight take one step moves in different directions (and different offsets). A pawn could as well but will need special en passant rules accounted for and is not in this game variation.

        Example of offset:
            {"TOP", (-1, 0)}, or will check -1 row and +0 col, so towards the Top direction just one square.

        Args:
            direction_offsets (dict[str,tuple[int, int]]): series of offset moves to check
            game_board (list[list[str  |  ChessPiece]]): a game board with pieces

        """

        self._valid_moves = set()

        for direction in direction_offsets:
            row_offset, col_offset = direction_offsets[direction]
            current_row_index, current_col_index = get_index_from_coord(
                self._current_coord
            )
            current_col_index += col_offset
            current_row_index += row_offset

            if not pos_on_board(current_row_index, current_col_index):
                continue

            if game_board[current_row_index][current_col_index] is None:
                self._valid_moves.add(
                    get_coord_from_index((current_row_index, current_col_index))
                )
            elif (
                game_board[current_row_index][current_col_index].get_player()
                is not self._player
            ):
                self._valid_moves.add(
                    get_coord_from_index((current_row_index, current_col_index))
                )
            elif (
                game_board[current_row_index][current_col_index].get_player()
                is self._player
            ):
                continue

    def _update_multi_square_moves(
        self,
        direction_offsets: dict[str, tuple[int, int]],
        game_board: list[list[str | ChessPiece]],
    ) -> None:
        """Sets the piece valid moves list, given offsets and a game board.

        The offsets are a series of directions and distances that will be checked sequentially for valid movement. This method will iterate with the given offset in some directionn repeatedly until it hits the edge of the board or another piece. Only the Bishop and Rook move in straight directions like this. The queen does as well but is not in the chess variant.

        Example of offset:
            {"TOP", (-1, 0)}, or will check -1 row and +0 col, so towards the Top direction just one square, but to be done repeatedly.

        Args:
            direction_offsets (dict[str,tuple[int, int]]): series of offset moves to check
            game_board (list[list[str  |  ChessPiece]]): a game board with pieces

        """
        self._valid_moves = set()
        current_row, current_col = get_index_from_coord(self._current_coord)

        for direction in direction_offsets:
            row_offset, col_offset = direction_offsets[direction]
            current_row, current_col = get_index_from_coord(self._current_coord)
            current_col += col_offset
            current_row += row_offset

            while pos_on_board(current_row, current_col):
                if game_board[current_row][current_col] is None:
                    self._valid_moves.add(
                        get_coord_from_index((current_row, current_col))
                    )
                elif (
                    game_board[current_row][current_col].get_player()
                    is not self._player
                ):
                    self._valid_moves.add(
                        get_coord_from_index((current_row, current_col))
                    )
                    break
                elif game_board[current_row][current_col].get_player() is self._player:
                    break
                current_col += col_offset
                current_row += row_offset


class Knight(ChessPiece):
    """A Knight chess piece"""
    def __init__(self, player, starting_pos, id, type):
        super().__init__(player, starting_pos, id, type)
        if player.get_color() == "WHITE":
            self._symbol = "♘"
        elif player.get_color() == "BLACK":
            self._symbol = "♞"

    def update_valid_moves(self, game_board: list[list[str | ChessPiece]]) -> None:
        """Updates all the valid moves for the knight.

        Args:
            game_board (list[list[str  |  ChessPiece]]): A 2d list gameboard with pieces on it.
        """
        # a Knight has 8 possible moves in 4 quadrants
        direction_offsets = {  # row offset, col offset
            "TOP RIGHT, TOP": (-2, 1),
            "TOP RIGHT, RIGHT": (-1, 2),
            "BOTTOM RIGHT, RIGHT": (1, 2),
            "BOTTOM RIGHT, BOTTOM": (2, 1),
            "BOTTOM LEFT, BOTTOM": (2, -1),
            "BOTTOM LEFT, LEFT": (1, -2),
            "TOP LEFT, LEFT": (-1, -2),
            "TOP LEFT, TOP": (-2, -1),
        }

        self._update_single_square_moves(direction_offsets, game_board)


class King(ChessPiece):
    """A King chess piece"""
    def __init__(self, player, starting_pos, id, type):
        super().__init__(player, starting_pos, id, type)
        if player.get_color() == "WHITE":
            self._symbol = "♔"
        elif player.get_color() == "BLACK":
            self._symbol = "♚"

    def update_valid_moves(self, game_board: list[list[str | ChessPiece]]) -> None:
        """Updates all the valid moves for the king.

        Args:
            game_board (list[list[str  |  ChessPiece]]): A 2d list gameboard with pieces on it.
        """
        # a King has 8 possible moves in all directions
        direction_offsets = {  # row offset, col offset
            "TOP": (-1, 0),
            "TOP RIGHT": (-1, 1),
            "RIGHT": (0, 1),
            "BOTTOM RIGHT": (1, 1),
            "BOTTOM": (1, 0),
            "BOTTOM LEFT": (1, -1),
            "LEFT": (0, -1),
            "TOP LEFT": (-1, -1),
        }

        self._update_single_square_moves(direction_offsets, game_board)


class Bishop(ChessPiece):
    """A Bishop chess piece"""
    def __init__(self, player, starting_pos, id, type):
        super().__init__(player, starting_pos, id, type)
        if player.get_color() == "WHITE":
            self._symbol = "♗"
        elif player.get_color() == "BLACK":
            self._symbol = "♝"

    def update_valid_moves(self, game_board: list[list[str | ChessPiece]]) -> None:
        direction_offsets = {  # row offset, col offset
            "TOP RIGHT": (-1, 1),
            "BOTTOM RIGHT": (1, 1),
            "BOTTOM LEFT": (1, -1),
            "TOP LEFT": (-1, -1),
        }

        self._update_multi_square_moves(direction_offsets, game_board)


class Rook(ChessPiece):
    """A Rook chess piece"""
    def __init__(self, player, starting_pos, id, type):
        super().__init__(player, starting_pos, id, type)
        if player.get_color() == "WHITE":
            self._symbol = "♖"
        elif player.get_color() == "BLACK":
            self._symbol = "♜"

    def update_valid_moves(self, game_board: list[list[str | ChessPiece]]) -> None:
        direction_offsets = {  # row offset, col offset
            "TOP": (-1, 0),
            "RIGHT": (0, 1),
            "BOTTOM": (1, 0),
            "LEFT": (0, -1),
        }

        self._update_multi_square_moves(direction_offsets, game_board)


def pos_on_board(row_index: int, col_index: int) -> bool:
    """Determines if a given list index position is on the chess board or not.

    Args:
        row_index (int): the row index position
        col_index (int): the column index position

    Returns:
        bool: Returns True if the position is on the board, False if otherwise
    """

    # the first and last column and row on the board, by list index
    _MAX_COLUMN = 7
    _MIN_COLUMN = 0
    _MAX_ROW = 7
    _MIN_ROW = 0

    if col_index < _MIN_COLUMN or col_index > _MAX_COLUMN:
        return False
    elif row_index < _MIN_ROW or row_index > _MAX_ROW:
        return False
    else:
        return True


def get_coord_from_index(position_index: tuple[int, int]) -> str:
    """Get the board alpha numeric coordinate given a 2d list index.

    Args:
        position_index (tuple[int, int]): a 2d list index in tuple format (row, col)

    Returns:
        str: the board coordinate in alphanumeric and integer format "XX",
        Example:
            "a1" or "b2", "column/row"...
    """

    row_index, col_index = position_index  # 0 7

    row_conversion = {
        7: "1",
        6: "2",
        5: "3",
        4: "4",
        3: "5",
        2: "6",
        1: "7",
        0: "8",
    }

    col_conversion = {
        0: "a",
        1: "b",
        2: "c",
        3: "d",
        4: "e",
        5: "f",
        6: "g",
        7: "h",
    }

    return col_conversion[col_index] + row_conversion[row_index]


def get_index_from_coord(coord: str) -> tuple[int, int]:
    """Get the 2d list index given the game board coordinates.

    Args:
        coord (str): board alphanumeric coordinate. i.e. "a1", "b2" etc.

    Returns:
        tuple[int, int]: board 2d index, (row and colum index)
        Example:
            "h1" -> (7, 7) in format: (row index, col index)
    """

    col_letter, row_number = [character for character in coord]

    board_index = {
        "a": 0,
        "b": 1,
        "c": 2,
        "d": 3,
        "e": 4,
        "f": 5,
        "g": 6,
        "h": 7,
        "1": 7,
        "2": 6,
        "3": 5,
        "4": 4,
        "5": 3,
        "6": 2,
        "7": 1,
        "8": 0,
    }
    return (board_index[row_number], board_index[col_letter])


def run_game() -> None:
    """The main game running function. Prints board and gets input. Not required to run ChessVar."""
    display = Display()
    game = ChessVar()

    display.print_introduction()
    display.print_board(game)

    while game.get_game_state() == "UNFINISHED":
        #main game loop, repeats until the game state is changed from UNFINISHED

        try:
            selected_move = display.prompt_move(game.get_whos_turn_it_is().get_color())
        except InvalidInputError:
            display.print_invalid_input_error()

        piece_to_move, destination_to_move_piece = selected_move

        if not game.make_move(piece_to_move, destination_to_move_piece):
            display.print_invalid_move_error()
            continue

        if game.get_game_over_condition():
            display.print_board(game)
            print(display.get_game_state_message(game.get_game_state()))
            break

        display.print_board(game)

    display.print_end_game_prompt()


if __name__ == "__main__":
    run_game()
