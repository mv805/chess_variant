import unittest
from ChessVar import ChessVar, Display, get_coord_from_index, get_index_from_coord, pos_on_board


class TestChessVar(unittest.TestCase):
    
    def test_get_index_from_coord(self):
        test_positions = (
            ("h1", (7, 7)),
            ("a1", (7, 0)),
            ("h8", (0, 7)),
            ("a8", (0, 0)),
            ("b2", (6, 1)),
            ("f5", (3, 5)),
            ("b1", (7, 1)),
            ("a2", (6, 0)),
            
        )

        for test_case in test_positions:
            board_coord, result_index = test_case
            with self.subTest(
                f"Board coord.: {board_coord}, result index: {result_index}"
            ):
                self.assertEqual(get_index_from_coord(board_coord), result_index)
                
    def test_get_coord_from_index(self):
        test_positions = (
            ((0, 7),"h8"),
            ((0, 0),"a8"),
            ((7, 7),"h1"),
            ((7, 0),"a1"),
            ((7, 1),"b1"),
            ((4, 5),"f4"),
        )

        for test_case in test_positions:
            board_index, result_coord = test_case
            with self.subTest(
                f"Board index: {board_index}, result coord.: {result_coord}"
            ):
                self.assertEqual(get_coord_from_index(board_index), result_coord)
                
    def test_get_if_pos_on_board(self):
        test_positions = (
            ((7, 7), True),
            ((7, 0), True),
            ((0, 7), True),
            ((0, 0), True),
            ((6, 1), True),
            ((3, 5), True),
            ((10,0), False),
            ((0,10), False),
            ((8,1), False),
            ((1,8), False)
        )

        for test_case in test_positions:
            (row_index, col_index), result = test_case
            with self.subTest(
                f"Board index: ({row_index}, {col_index}) result: {result}"
            ): 
                self.assertEqual(pos_on_board(row_index, col_index), result)       
        
    def test_cant_move_piece_if_not_turn(self):
        """Cant move a piece if its not the players turn."""
        test_game = ChessVar()
        "if a selected piece to move is not the current player, should not be able to move it"
        "cant move the black piece first"
        self.assertFalse(test_game.make_move("f2","g4"))
        "can move the white piece first"
        self.assertTrue(test_game.make_move("c2","d4"))
        
    def test_knight_valid_moves_on_clear_board(self):
        """A Knight can calculate all moves on a clear board."""
        white_test_pos = (
            ("KNIGHT", "e4", 1),
        )
        
        black_test_pos = None
        
        test_game = ChessVar(white_test_pos, black_test_pos)
        valid_knight_moves_clear_board = {"f2","g3","g5","f6","d6","c5","c3","d2"}
        self.assertEqual(test_game.get_player("WHITE").get_piece_by_id("KNIGHT", 1).get_valid_moves(), valid_knight_moves_clear_board)
    
    def test_knight_valid_moves_with_enemy_player_and_own_piece(self):   
        """Testing a board with an enemy player piece in a move zone and one player piece in a move zone."""
        white_test_pos = (
            ("KNIGHT", "e4", 1),
            ("KNIGHT", "f6", 2),
        )
        
        black_test_pos = (
            ("KNIGHT", "g3", 1),
        )
        test_game = ChessVar(white_test_pos, black_test_pos)
        valid_knight_moves_with_conflicts = {"f2","g3","g5","d6","c5","c3","d2"}
        self.assertEqual(test_game.get_player("WHITE").get_piece_by_id("KNIGHT", 1).get_valid_moves(), valid_knight_moves_with_conflicts)
    
    def test_knight_valid_moves_corner_and_blocked(self): 
        """Testing a board with a player piece at the corner of the board and player pieces in the only 2 possible spots for movement.""" 
        
        white_test_pos = (
            ("KNIGHT", "h1", 1),
            ("KNIGHT", "f2", 2),
            ("KNIGHT", "g3", 3),
        )
        
        black_test_pos = None
        
        test_game = ChessVar(white_test_pos, black_test_pos)
        valid_knight_moves_in_corner = set()
        self.assertEqual(test_game.get_player("WHITE").get_piece_by_id("KNIGHT", 1).get_valid_moves(), valid_knight_moves_in_corner)
    
    def test_king_valid_moves_on_clear_board(self):
        """King can move on a clear board."""
        white_test_pos = (
            ("KING", "e4", 1),
        )
        
        black_test_pos = None
        
        test_game = ChessVar(white_test_pos, black_test_pos)
        valid_king_moves_clear_board = {"d3","e3","f3","f4","f5","e5","d5","d4"}
        self.assertEqual(test_game.get_player("WHITE").get_piece_by_id("KING", 1).get_valid_moves(), valid_king_moves_clear_board)
    
    def test_king_valid_moves_with_enemy_player_and_own_piece(self):   
        """Testing a board with an enemy player piece in a move zone and one player piece in a move zone."""
        white_test_pos = (
            ("KING", "e4", 1),
            ("KING", "d5", 2),
        )
        
        black_test_pos = (
            ("KING", "f3", 1),
        )
        test_game = ChessVar(white_test_pos, black_test_pos)
        valid_king_moves_with_conflicts = {"d3","e3","f3","f4","f5","e5","d4"}
        self.assertEqual(test_game.get_player("WHITE").get_piece_by_id("KING", 1).get_valid_moves(), valid_king_moves_with_conflicts)
    
    def test_king_valid_moves_corner_and_blocked(self): 
        """Testing a board with a player piece at the corner of the board and player pieces in the only 2 possible spots for movement""" 
        
        white_test_pos = (
            ("KING", "h1", 1),
            ("KING", "g1", 2),
            ("KING", "g2", 3),
            ("KING", "h2", 4),
        )
        
        black_test_pos = None
        
        test_game = ChessVar(white_test_pos, black_test_pos)
        valid_king_moves_in_corner = set()
        self.assertEqual(test_game.get_player("WHITE").get_piece_by_id("KING", 1).get_valid_moves(), valid_king_moves_in_corner)
    
    def test_king_blocked_to_top_and_right_side_cant_move_diagonal_up_into_check(self):
        """A king blocked in certain ways can still move to a diagonal location."""
        white_test_pos = (
            ("KING", "b1", 1),
            ("KNIGHT", "c1", 2),
            ("KNIGHT", "d4", 1),
            ("BISHOP", "d3", 1),
            ("BISHOP", "b2", 2),
            ("ROOK", "a2", 1),
        )
        
        black_test_pos = (
            ("KING", "h1", 1),
            ("BISHOP", "g1", 1),
            ("BISHOP", "d5", 2),
            ("ROOK", "g2", 1),
            ("KNIGHT", "f1", 1),
        )
        
        test_game = ChessVar(white_test_pos, black_test_pos)
        self.assertFalse(test_game.make_move("b1","c2"))
    
    def test_bishop_valid_moves_on_clear_board(self):
        """Bishop can calculate valid moves on a clear board."""
        white_test_pos = (
            ("BISHOP", "e4", 1),
        )
        
        black_test_pos = None
        
        test_game = ChessVar(white_test_pos, black_test_pos)
        valid_bishop_moves_clear_board = {"f5","g6","h7","f3","g2","h1","d3","c2","b1","d5","c6","b7","a8"}
        self.assertEqual(test_game.get_player("WHITE").get_piece_by_id("BISHOP", 1).get_valid_moves(), valid_bishop_moves_clear_board)

    def test_bishop_valid_moves_with_enemy_player_and_own_piece(self):   
        """Testing a board with an enemy player piece in a move zone and one player piece in a move zone."""
        white_test_pos = (
            ("BISHOP", "e4", 1),
            ("BISHOP", "d5", 2),
        )
        
        black_test_pos = (
            ("BISHOP", "d3", 1),
        )
        test_game = ChessVar(white_test_pos, black_test_pos)
        valid_bishop_moves_with_conflicts = {"d3","f3","g2","h1","f5","g6","h7"}
        self.assertEqual(test_game.get_player("WHITE").get_piece_by_id("BISHOP", 1).get_valid_moves(), valid_bishop_moves_with_conflicts)
    
    def test_bishop_valid_moves_corner_and_blocked(self): 
        """Testing a board with a player piece at the corner of the board and player pieces in the only 2 possible spots for movement.""" 
        
        white_test_pos = (
            ("BISHOP", "h1", 1),
            ("BISHOP", "g2", 2),
        )
        
        black_test_pos = None
        
        test_game = ChessVar(white_test_pos, black_test_pos)
        valid_bishop_moves_in_corner = set()
        self.assertEqual(test_game.get_player("WHITE").get_piece_by_id("BISHOP", 1).get_valid_moves(), valid_bishop_moves_in_corner)
    
    def test_rook_valid_moves_on_clear_board(self):
        """The rook calculates valid moves on a clear board."""
        white_test_pos = (
            ("ROOK", "e4", 1),
        )
        
        black_test_pos = None
        
        test_game = ChessVar(white_test_pos, black_test_pos)
        valid_rook_moves_clear_board = {"e3","e2","e1","f4","g4","h4","e5","e6","e7","e8","d4","c4","b4","a4"}
        self.assertEqual(test_game.get_player("WHITE").get_piece_by_id("ROOK", 1).get_valid_moves(), valid_rook_moves_clear_board)

    def test_rook_valid_moves_with_enemy_player_and_own_piece(self):   
        """Testing a board with an enemy player piece in a move zone and one player piece in a move zone."""
       
        white_test_pos = (
            ("ROOK", "e4", 1),
            ("ROOK", "d4", 2),
        )
        
        black_test_pos = (
            ("ROOK", "e2", 1),
        )
        test_game = ChessVar(white_test_pos, black_test_pos)
        valid_rook_moves_with_conflicts = {"e3","e2","f4","g4","h4","e5","e6","e7","e8"}
        self.assertEqual(test_game.get_player("WHITE").get_piece_by_id("ROOK", 1).get_valid_moves(), valid_rook_moves_with_conflicts)
    
    def test_rook_valid_moves_corner_and_blocked_to_left_but_not_down(self): 
        """Testing a board with a player piece at the corner of the board and player pieces in the only 2 possible spots for movement.""" 
        
        white_test_pos = (
            ("ROOK", "h1", 1),
            ("ROOK", "g1", 2),
            ("ROOK", "g2", 3),
        )
        
        black_test_pos = None
        
        test_game = ChessVar(white_test_pos, black_test_pos)
        valid_rook_h1_moves = {"h2","h3","h4","h5","h6","h7","h8"}
        self.assertEqual(test_game.get_player("WHITE").get_piece_by_id("ROOK", 1).get_valid_moves(), valid_rook_h1_moves)
        
        valid_rook_g1_moves = {"a1","b1","c1","d1","e1","f1"}
        self.assertEqual(test_game.get_player("WHITE").get_piece_by_id("ROOK", 2).get_valid_moves(), valid_rook_g1_moves)
        
        valid_rook_g2_moves = {"a2","b2","c2","d2","e2","f2","g3","g4","g5","g6","g7","g8","h2"}
        self.assertEqual(test_game.get_player("WHITE").get_piece_by_id("ROOK", 3).get_valid_moves(), valid_rook_g2_moves)
    
    def test_rook_valid_moves_update_after_move_even_if_in_check_condition(self):
        """The rook updates all valid moves after a move"""
        white_test_pos = (
            ("ROOK", "a2", 1),
            ("KING", "a1", 1), 
        )
        
        black_test_pos = (
            ("KING", "h1", 1),
        )
        
        test_game = ChessVar(white_test_pos, black_test_pos)
        valid_rook_moves_before_move = {"a3","a4","a5","a6","a7","a8","b2","c2","d2","e2","f2","g2","h2"}
        self.assertEqual(test_game.get_player("WHITE").get_piece_by_id("ROOK",1).get_valid_moves(), valid_rook_moves_before_move)
        
        test_game.make_move("a2","h2")
        valid_rook_moves_after_move = {"a2","b2","c2","d2","e2","f2","g2","h1","h3","h4","h5","h6","h7","h8"}
        self.assertEqual(test_game.get_player("WHITE").get_piece_by_id("ROOK",1).get_valid_moves(), valid_rook_moves_after_move)
        
  
    def test_update_all_valid_moves(self): 
        """All valid moves should be recalculating correctly upon initialization.""" 
        
        white_test_pos = (
            ("ROOK", "a8", 1),
            ("KING", "d5", 2),
            ("BISHOP", "e4", 3),
            ("KNIGHT", "g4", 3),
        )
        
        black_test_pos = (
            ("ROOK", "c8", 1),
            ("KNIGHT", "f5", 2),
        )
        
        test_game = ChessVar(white_test_pos, black_test_pos)
        valid_moves = {"a1","b1","h1","a2","c2","f2","g2","h2","a3","d3","e3","f3","a4","c4","d4","a5","c5","e5","f5","a6","c6","d6","e6","f6","h6","a7","b8","c8"}
        self.assertEqual(test_game.get_player("WHITE").get_valid_moves(), valid_moves)
        
    def test_white_knight_moves_then_black_knight(self):
        """Simple test to make sure the knights can move sequentially at beginning of game"""
        test_game = ChessVar()
        self.assertEqual(test_game.get_whos_turn_it_is(), test_game.get_player("WHITE"))
        self.assertTrue(test_game.make_move("c2","d4"))
        self.assertEqual(test_game.get_whos_turn_it_is(), test_game.get_player("BLACK"))
        self.assertTrue(test_game.make_move("f2","d3"))
        self.assertEqual(test_game.get_whos_turn_it_is(), test_game.get_player("WHITE"))
        self.assertNotEqual(test_game.get_whos_turn_it_is(), test_game.get_player("BLACK"))
        
        white_knight_row_index, white_knight_col_index = get_index_from_coord("d4")
        black_knight_row_index, black_knight_col_index = get_index_from_coord("d3")
        
        self.assertEqual(test_game.get_game_board()[white_knight_row_index][white_knight_col_index].get_player().get_color(),"WHITE")
        self.assertEqual(test_game.get_game_board()[white_knight_row_index][white_knight_col_index].get_piece_type(),"KNIGHT")
        
        self.assertEqual(test_game.get_game_board()[black_knight_row_index][black_knight_col_index].get_player().get_color(),"BLACK")
        self.assertEqual(test_game.get_game_board()[black_knight_row_index][black_knight_col_index].get_piece_type(),"KNIGHT")
        
    def test_white_wins_game(self): 
        """White should be able to win."""
        white_test_pos = (
            ("KING", "b7", 1),
        )
        
        black_test_pos = (
            ("KING", "g7", 1),
        )
        
        test_game = ChessVar(white_test_pos, black_test_pos)
        self.assertEqual(len(test_game.get_players_with_kings_in_last_row()), 0)
        self.assertEqual(test_game.get_game_state(), "UNFINISHED")
        test_game.make_move("b7","b8") #white moves king to final row
        self.assertEqual(len(test_game.get_players_with_kings_in_last_row()), 1)
        test_game.make_move("g7","g6")
        self.assertEqual(test_game.get_game_state(), "WHITE_WON")
    
    def test_black_wins_game(self): 
        """Black should be able to win."""
        white_test_pos = (
            ("KING", "b7", 1),
        )
        
        black_test_pos = (
            ("KING", "g7", 1),
        )
        
        test_game = ChessVar(white_test_pos, black_test_pos)
        self.assertEqual(test_game.get_game_state(), "UNFINISHED")
        test_game.make_move("b7","b6") #white moves king to one row backwards
        self.assertEqual(len(test_game.get_players_with_kings_in_last_row()), 0)
        test_game.make_move("g7","g8")
        self.assertEqual(len(test_game.get_players_with_kings_in_last_row()), 1)
        self.assertEqual(test_game.get_game_state(), "UNFINISHED")
        test_game.make_move("b6","b5") #white moves king to one row backwards
        self.assertEqual(len(test_game.get_players_with_kings_in_last_row()), 1)
        self.assertEqual(test_game.get_game_state(), "BLACK_WON")
        
    
    def test_tie_game(self):
        """Game should be able to end in tie."""
        white_test_pos = (
            ("KING", "b7", 1),
        )
        
        black_test_pos = (
            ("KING", "g7", 1),
        )
        
        test_game = ChessVar(white_test_pos, black_test_pos)
        self.assertEqual(test_game.get_game_state(), "UNFINISHED")
        self.assertEqual(len(test_game.get_players_with_kings_in_last_row()), 0)
        
        test_game.make_move("b7","b8") #white moves king to finish
        self.assertEqual(len(test_game.get_players_with_kings_in_last_row()), 1)
        test_game.make_move("g7","g8")#black moves king to finish
        self.assertEqual(len(test_game.get_players_with_kings_in_last_row()), 2)
        self.assertEqual(test_game.get_game_state(), "TIE")  
        
    def test_full_game(self):
        """A full sequence of a game with expected feedback asserted."""
        test_game = ChessVar()
        self.assertTrue(test_game.make_move("c2","d4"))
        self.assertTrue(test_game.make_move("f2","d3"))
        self.assertTrue(test_game.make_move("b1","d3"))
        self.assertTrue(test_game.make_move("g2","d5"))
        self.assertTrue(test_game.make_move("a1","b1"))
        
        #white player and black player should have 5 and 6 pieces respectively
        self.assertTrue(len(test_game.get_player("WHITE").get_pieces()), 5)
        self.assertTrue(len(test_game.get_player("BLACK").get_pieces()), 6)
        
        #try to move to check condition by black (white in check)
        self.assertFalse(test_game.make_move("d5","a2"))
        
        #check to make sure the pieces were moved back
        self.assertEqual(test_game.get_game_board()[3][3].get_player().get_color(), "BLACK")
        self.assertEqual(test_game.get_game_board()[3][3].get_piece_type(), "BISHOP")
        self.assertEqual(test_game.get_game_board()[6][0].get_player().get_color(), "WHITE")
        self.assertEqual(test_game.get_game_board()[6][0].get_piece_type(), "ROOK")
        #its still whites turn
        self.assertEqual(test_game.get_whos_turn_it_is().get_color(), "BLACK")
        #white player and black player still have 5 and 6 pieces respectively
        self.assertTrue(len(test_game.get_player("WHITE").get_pieces()), 5)
        self.assertTrue(len(test_game.get_player("BLACK").get_pieces()), 6)
        
        self.assertFalse(test_game.make_move("h2","b2"))
        self.assertTrue(test_game.make_move("h2","g2"))
        self.assertFalse(test_game.make_move("b1","c2"))#cant move to check
        self.assertTrue(test_game.make_move("c1","e2"))
        self.assertTrue(test_game.make_move("h1","h2"))
        self.assertFalse(test_game.make_move("b1","b2"))#cant move on top of bishop
        self.assertTrue(test_game.make_move("b1","c2"))
        self.assertTrue(test_game.make_move("h2","h3"))
        self.assertTrue(test_game.make_move("c2","c3"))
        self.assertFalse(test_game.make_move("c3","c4"))#cant select another players piece (white)
        self.assertTrue(test_game.make_move("h3","h4"))
        self.assertFalse(test_game.make_move("c3","c4"))#cant move king into check
        self.assertTrue(test_game.make_move("c3","b4"))
        self.assertTrue(test_game.make_move("g2","g5"))
        self.assertTrue(test_game.make_move("b4","b5"))
        self.assertFalse(test_game.make_move("d5","a2"))
        self.assertTrue(test_game.make_move("h4","h5"))
        self.assertTrue(test_game.make_move("b5","b6"))
        self.assertTrue(test_game.make_move("h5","h6"))
        self.assertTrue(test_game.make_move("b6","c7"))
        self.assertFalse(test_game.make_move("h6","h7"))#cant move into check (black king)
        self.assertTrue(test_game.make_move("h6","g7"))
        
        self.assertEqual(test_game.get_game_state(), "UNFINISHED")
        self.assertTrue(test_game.make_move("c7","c8"))
        self.assertTrue(test_game.make_move("g5","g6")) #black doesnt finish in time 
        self.assertEqual(test_game.get_game_state(), "WHITE_WON")
        

    def test_cant_check_with_rook(self): 
        """A rook cant cause a check condition."""
        white_test_pos = (
            ("ROOK", "a2", 1),
            ("KING", "a1", 1), #need both kings on board for function to work
        )
        
        black_test_pos = (
            ("KING", "h1", 1),
        )
        
        test_game = ChessVar(white_test_pos, black_test_pos)
        self.assertFalse(test_game.make_move("a2","h2"))
    
    def test_should_stalemate(self):
        """Should be able to stop the game if stalemate occurs."""
        white_test_pos = ( #need both kings on board for function to work
            ("KING", "h2", 1), #starts in check which cant happen but its ok for this test only
        )
        
        black_test_pos = (
            ("KNIGHT", "g1", 1),
            ("KNIGHT", "g2", 2),
            ("KNIGHT", "f1", 3),
            ("KING","a8",1)
        )
        
        test_game = ChessVar(white_test_pos, black_test_pos)
        self.assertTrue(test_game.get_game_state(),"UNFINISHED")
        self.assertTrue(test_game.make_move("h2","h1"))
        self.assertTrue(test_game.make_move("f1","h2"))
        self.assertTrue(test_game.get_game_state(),"STALEMATE")

class TestDisplay(unittest.TestCase):
    test_display = Display()

    def test_input_validation(self):
        # testing internal validation function. If test fails in the future, delete it.
        test_cases = (
            "sf$$2df2ajd%^f&jsdfoa#ijioio3[]2i@3434234234/]2",
            "",
            "x3",
            "9",
        )

        for test_case in test_cases:
            with self.subTest(f"Test case: {test_case}"):
                 self.assertFalse(self.test_display._is_valid_coordinate(test_case))


if __name__ == "__main__":
    unittest.main()
