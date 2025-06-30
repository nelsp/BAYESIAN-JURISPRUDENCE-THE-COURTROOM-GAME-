# test_bayesian_core.py
"""
Test suite for the core Bayesian game logic.
Run with: python test_bayesian_core.py
"""

import unittest
import json
import os
import tempfile
from bayesian_core import (
    BayesianCalculator, 
    BayesianGame, 
    CaseData, 
    PlayerState, 
    PlayerResponse,
    GamePhase,
    list_case_files,
    validate_case_file
)


class TestBayesianCalculator(unittest.TestCase):
    """Test the BayesianCalculator static methods."""
    
    def test_decibels_to_probability(self):
        """Test decibel to probability conversion."""
        # Test positive decibels (evidence for guilt)
        self.assertAlmostEqual(BayesianCalculator.decibels_to_probability(10), 0.9, places=4)
        self.assertAlmostEqual(BayesianCalculator.decibels_to_probability(20), 0.99, places=4)
        
        # Test negative decibels (evidence for innocence)
        self.assertAlmostEqual(BayesianCalculator.decibels_to_probability(-10), 0.1, places=4)
        
        # Test zero decibels (no evidence)
        self.assertAlmostEqual(BayesianCalculator.decibels_to_probability(0), 0.5, places=4)
    
    def test_probability_to_decibels(self):
        """Test probability to decibel conversion."""
        self.assertAlmostEqual(BayesianCalculator.probability_to_decibels(0.9), 9.54, places=1)
        self.assertAlmostEqual(BayesianCalculator.probability_to_decibels(0.5), 0, places=1)
        self.assertAlmostEqual(BayesianCalculator.probability_to_decibels(0.1), -9.54, places=1)
    
    def test_calculate_db_update(self):
        """Test evidence update calculation."""
        # Strong evidence for guilt
        db_update = BayesianCalculator.calculate_db_update(0.9, 0.1)
        self.assertAlmostEqual(db_update, 9.54, places=1)
        
        # Strong evidence for innocence
        db_update = BayesianCalculator.calculate_db_update(0.1, 0.9)
        self.assertAlmostEqual(db_update, -9.54, places=1)
        
        # No evidence either way
        db_update = BayesianCalculator.calculate_db_update(0.5, 0.5)
        self.assertAlmostEqual(db_update, 0, places=1)
    
    def test_calculate_guilt_threshold(self):
        """Test guilt threshold calculation."""
        # 1 in 100 tolerance
        threshold = BayesianCalculator.calculate_guilt_threshold(100)
        self.assertAlmostEqual(threshold, 20, places=1)
        
        # 1 in 10 tolerance
        threshold = BayesianCalculator.calculate_guilt_threshold(10)
        self.assertAlmostEqual(threshold, 10, places=1)
    
    def test_rating_to_probability(self):
        """Test rating scale conversion."""
        self.assertEqual(BayesianCalculator.rating_to_probability(0), 0.001)
        self.assertEqual(BayesianCalculator.rating_to_probability(5), 0.5)
        self.assertEqual(BayesianCalculator.rating_to_probability(10), 0.999)


class TestCaseData(unittest.TestCase):
    """Test the CaseData class."""
    
    def setUp(self):
        """Create a temporary case file for testing."""
        self.test_case_data = {
            "case": {
                "name": "Test Case",
                "description": "A test criminal case",
                "population": 10000
            },
            "prior": {
                "db": -40,
                "odds": "1 in 10,000"
            },
            "evidence": [
                {
                    "name": "Test Evidence 1",
                    "description": "First piece of evidence",
                    "prob_guilty": 0.8,
                    "prob_innocent": 0.2
                },
                {
                    "name": "Test Evidence 2", 
                    "description": "Second piece of evidence"
                }
            ]
        }
        
        # Create temporary file
        self.temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False)
        json.dump(self.test_case_data, self.temp_file)
        self.temp_file.close()
    
    def tearDown(self):
        """Clean up temporary file."""
        os.unlink(self.temp_file.name)
    
    def test_load_valid_case_file(self):
        """Test loading a valid case file."""
        case_data = CaseData(self.temp_file.name)
        self.assertEqual(case_data.case_info['name'], "Test Case")
        self.assertEqual(case_data.evidence_count, 2)
        self.assertEqual(case_data.prior_info['db'], -40)
    
    def test_get_evidence(self):
        """Test getting specific evidence items."""
        case_data = CaseData(self.temp_file.name)
        
        evidence_0 = case_data.get_evidence(0)
        self.assertEqual(evidence_0['name'], "Test Evidence 1")
        
        # Test index out of range
        with self.assertRaises(IndexError):
            case_data.get_evidence(10)
    
    def test_invalid_case_file(self):
        """Test handling of invalid case files."""
        # Test non-existent file
        with self.assertRaises(FileNotFoundError):
            CaseData("nonexistent.json")
        
        # Test invalid JSON
        invalid_file = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False)
        invalid_file.write("invalid json content")
        invalid_file.close()
        
        try:
            with self.assertRaises(ValueError):
                CaseData(invalid_file.name)
        finally:
            os.unlink(invalid_file.name)


class TestPlayerState(unittest.TestCase):
    """Test the PlayerState class."""
    
    def setUp(self):
        """Set up a test player."""
        self.player = PlayerState(
            player_id="test_player",
            name="Test Player",
            guilt_threshold_db=20,
            prior_guilt_tolerance=100,
            current_evidence_db=-40,
            responses=[],
            use_rating_scale=True
        )
    
    def test_add_response(self):
        """Test adding responses and updating evidence level."""
        response = PlayerResponse(
            player_id="test_player",
            evidence_index=0,
            evidence_name="Test Evidence",
            prob_guilty=0.8,
            prob_innocent=0.2,
            used_rating_scale=True,
            db_update=6.02  # 10 * log10(0.8/0.2)
        )
        
        initial_db = self.player.current_evidence_db
        self.player.add_response(response)
        
        self.assertEqual(len(self.player.responses), 1)
        self.assertAlmostEqual(self.player.current_evidence_db, initial_db + 6.02, places=1)
    
    def test_would_convict(self):
        """Test conviction threshold checking."""
        # Initially below threshold
        self.assertFalse(self.player.would_convict())
        
        # Add enough evidence to exceed threshold
        self.player.current_evidence_db = 25
        self.assertTrue(self.player.would_convict())


class TestBayesianGame(unittest.TestCase):
    """Test the main BayesianGame class."""
    
    def setUp(self):
        """Set up a test game with case file."""
        # Create test case file
        self.test_case_data = {
            "case": {
                "name": "Test Case",
                "description": "A test criminal case",
                "population": 10000
            },
            "prior": {
                "db": -40,
                "odds": "1 in 10,000"
            },
            "evidence": [
                {
                    "name": "Test Evidence 1",
                    "description": "First piece of evidence"
                },
                {
                    "name": "Test Evidence 2",
                    "description": "Second piece of evidence"
                }
            ]
        }
        
        self.temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False)
        json.dump(self.test_case_data, self.temp_file)
        self.temp_file.close()
        
        self.game = BayesianGame(self.temp_file.name, "test_game")
    
    def tearDown(self):
        """Clean up."""
        os.unlink(self.temp_file.name)
    
    def test_add_players(self):
        """Test adding players to the game."""
        # Add first player
        success = self.game.add_player("player1", "Alice", 100, True)
        self.assertTrue(success)
        self.assertEqual(len(self.game.players), 1)
        
        # Add second player
        success = self.game.add_player("player2", "Bob", 200, False)
        self.assertTrue(success)
        self.assertEqual(len(self.game.players), 2)
        
        # Try to add same player again
        success = self.game.add_player("player1", "Alice Again", 100, True)
        self.assertFalse(success)
        self.assertEqual(len(self.game.players), 2)
    
    def test_game_phases(self):
        """Test game phase transitions."""
        # Initially in setup
        self.assertEqual(self.game.phase, GamePhase.SETUP)
        
        # Can't start without players
        self.assertFalse(self.game.can_start_game())
        
        # Add player and start
        self.game.add_player("player1", "Alice", 100, True)
        self.assertTrue(self.game.can_start_game())
        
        success = self.game.start_game()
        self.assertTrue(success)
        self.assertEqual(self.game.phase, GamePhase.CASE_PRESENTATION)
        
        # Advance to evidence review
        self.game.advance_to_evidence_review()
        self.assertEqual(self.game.phase, GamePhase.EVIDENCE_REVIEW)
    
    def test_evidence_submission(self):
        """Test submitting evidence responses."""
        # Set up game with players
        self.game.add_player("player1", "Alice", 100, True)
        self.game.add_player("player2", "Bob", 200, False)
        self.game.start_game()
        self.game.advance_to_evidence_review()
        
        # Submit response for player1
        success = self.game.submit_evidence_response("player1", 0.8, 0.2, 8, 2)
        self.assertTrue(success)
        self.assertEqual(len(self.game.responses_for_current_evidence), 1)
        
        # Not all players have responded yet
        self.assertFalse(self.game.all_players_responded())
        
        # Submit response for player2
        success = self.game.submit_evidence_response("player2", 0.7, 0.3)
        self.assertTrue(success)
        self.assertEqual(len(self.game.responses_for_current_evidence), 2)
        
        # Now all players have responded
        self.assertTrue(self.game.all_players_responded())
    
    def test_advance_evidence(self):
        """Test advancing through evidence items."""
        # Set up game
        self.game.add_player("player1", "Alice", 100, True)
        self.game.start_game()
        self.game.advance_to_evidence_review()
        
        # Submit response and advance
        self.game.submit_evidence_response("player1", 0.8, 0.2)
        
        # Should advance to next evidence (index 1)
        has_more = self.game.advance_evidence()
        self.assertTrue(has_more)
        self.assertEqual(self.game.current_evidence_index, 1)
        self.assertEqual(self.game.phase, GamePhase.EVIDENCE_REVIEW)
        
        # Submit response for last evidence and advance
        self.game.submit_evidence_response("player1", 0.6, 0.4)
        
        # Should move to verdict phase
        has_more = self.game.advance_evidence()
        self.assertFalse(has_more)
        self.assertEqual(self.game.phase, GamePhase.VERDICT)
    
    def test_group_verdict_calculation(self):
        """Test group verdict calculation."""
        # Add players with different thresholds
        self.game.add_player("player1", "Alice", 10, True)   # Low threshold
        self.game.add_player("player2", "Bob", 1000, True)   # High threshold
        self.game.start_game()
        self.game.advance_to_evidence_review()
        
        # Submit responses for first evidence
        self.game.submit_evidence_response("player1", 0.9, 0.1)
        self.game.submit_evidence_response("player2", 0.9, 0.1)
        self.game.advance_evidence()
        
        # Submit responses for second evidence
        self.game.submit_evidence_response("player1", 0.8, 0.2)
        self.game.submit_evidence_response("player2", 0.8, 0.2)
        self.game.advance_evidence()
        
        # Get game state with verdict
        state = self.game.get_game_state()
        self.assertEqual(state['phase'], GamePhase.VERDICT.value)
        self.assertIn('verdict', state)
        
        # Check that verdict calculation works
        verdict_info = state['verdict']
        self.assertIn('group_verdict', verdict_info)
        self.assertIn('average_evidence_db', verdict_info)
        self.assertIn('statistics', verdict_info)
    
    def test_player_state_retrieval(self):
        """Test getting player state information."""
        # Add player
        self.game.add_player("player1", "Alice", 100, True)
        
        # Get player state
        player_state = self.game.get_player_state("player1")
        self.assertIsNotNone(player_state)
        self.assertEqual(player_state['name'], "Alice")
        self.assertEqual(player_state['player_id'], "player1")
        
        # Test non-existent player
        player_state = self.game.get_player_state("nonexistent")
        self.assertIsNone(player_state)
    
    def test_save_game_results(self):
        """Test saving game results."""
        # Set up and complete a game
        self.game.add_player("player1", "Alice", 100, True)
        self.game.start_game()
        self.game.advance_to_evidence_review()
        
        # Process all evidence
        for i in range(self.game.case_data.evidence_count):
            self.game.submit_evidence_response("player1", 0.8, 0.2)
            self.game.advance_evidence()
        
        # Save results
        try:
            filename = self.game.save_game_results()
            self.assertTrue(os.path.exists(filename))
            
            # Verify saved content
            with open(filename, 'r') as f:
                saved_data = json.load(f)
            
            self.assertEqual(saved_data['game_id'], self.game.game_id)
            self.assertIn('final_verdict', saved_data)
            self.assertIn('players', saved_data)
            
            # Clean up
            os.unlink(filename)
        except Exception as e:
            self.fail(f"Save game results failed: {e}")


class TestUtilityFunctions(unittest.TestCase):
    """Test utility functions."""
    
    def setUp(self):
        """Create temporary case files for testing."""
        self.temp_dir = tempfile.mkdtemp()
        
        # Create valid case file
        valid_case = {
            "case": {"name": "Valid Case", "description": "Test"},
            "prior": {"db": -40, "odds": "1 in 10,000"},
            "evidence": [{"name": "Evidence 1", "description": "Test evidence"}]
        }
        
        self.valid_file = os.path.join(self.temp_dir, "valid_case.json")
        with open(self.valid_file, 'w') as f:
            json.dump(valid_case, f)
        
        # Create invalid case file
        invalid_case = {"case": {"name": "Invalid"}}  # Missing required fields
        
        self.invalid_file = os.path.join(self.temp_dir, "invalid_case.json")
        with open(self.invalid_file, 'w') as f:
            json.dump(invalid_case, f)
        
        # Create result file (should be excluded from listing)
        result_file = os.path.join(self.temp_dir, "case_results_123.json")
        with open(result_file, 'w') as f:
            json.dump(valid_case, f)
    
    def tearDown(self):
        """Clean up temporary directory."""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_list_case_files(self):
        """Test listing case files."""
        case_files = list_case_files(self.temp_dir)
        
        # Should include valid and invalid, but not results
        self.assertIn("valid_case.json", case_files)
        self.assertIn("invalid_case.json", case_files)
        self.assertNotIn("case_results_123.json", case_files)
    
    def test_validate_case_file(self):
        """Test case file validation."""
        # Test valid file
        is_valid, message = validate_case_file(self.valid_file)
        self.assertTrue(is_valid)
        
        # Test invalid file
        is_valid, message = validate_case_file(self.invalid_file)
        self.assertFalse(is_valid)
        self.assertIn("Missing required field", message)
        
        # Test non-existent file
        is_valid, message = validate_case_file("nonexistent.json")
        self.assertFalse(is_valid)


class TestCompleteGameFlow(unittest.TestCase):
    """Integration test for complete game flow."""
    
    def setUp(self):
        """Set up a complete test case."""
        self.test_case_data = {
            "case": {
                "name": "Murder Case",
                "description": "A complex murder investigation",
                "population": 50000
            },
            "prior": {
                "db": -47,
                "odds": "1 in 50,000",
                "reasoning": "Base rate for murder in the population"
            },
            "evidence": [
                {
                    "name": "DNA Evidence",
                    "description": "DNA found at crime scene matches defendant",
                    "prob_guilty": 0.95,
                    "prob_innocent": 0.001,
                    "explanation": "DNA evidence is very reliable"
                },
                {
                    "name": "Eyewitness Testimony", 
                    "description": "Witness claims to have seen defendant at scene",
                    "prob_guilty": 0.7,
                    "prob_innocent": 0.3,
                    "explanation": "Eyewitness testimony can be unreliable"
                },
                {
                    "name": "Alibi Evidence",
                    "description": "Defendant claims to have been elsewhere",
                    "prob_guilty": 0.2,
                    "prob_innocent": 0.8,
                    "explanation": "Strong alibi evidence favors innocence"
                }
            ]
        }
        
        self.temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False)
        json.dump(self.test_case_data, self.temp_file)
        self.temp_file.close()
    
    def tearDown(self):
        """Clean up."""
        os.unlink(self.temp_file.name)
    
    def test_complete_game_simulation(self):
        """Test a complete game from start to finish."""
        game = BayesianGame(self.temp_file.name, "integration_test")
        
        # Add multiple players with different thresholds
        players_data = [
            ("alice", "Alice", 100, True),    # Moderate threshold
            ("bob", "Bob", 1000, False),      # High threshold  
            ("charlie", "Charlie", 20, True)  # Low threshold
        ]
        
        for player_id, name, tolerance, use_rating in players_data:
            success = game.add_player(player_id, name, tolerance, use_rating)
            self.assertTrue(success, f"Failed to add player {name}")
        
        # Start game
        self.assertTrue(game.start_game())
        self.assertEqual(game.phase, GamePhase.CASE_PRESENTATION)
        
        # Move to evidence review
        game.advance_to_evidence_review()
        self.assertEqual(game.phase, GamePhase.EVIDENCE_REVIEW)
        
        # Process each piece of evidence
        evidence_responses = [
            # DNA Evidence - players agree it's strong for guilt
            [("alice", 0.95, 0.001, 9, 0), ("bob", 0.98, 0.002), ("charlie", 0.90, 0.005, 9, 0)],
            # Eyewitness - more variation in responses  
            [("alice", 0.70, 0.30, 7, 3), ("bob", 0.60, 0.40), ("charlie", 0.80, 0.20, 8, 2)],
            # Alibi - favors innocence
            [("alice", 0.20, 0.80, 2, 8), ("bob", 0.15, 0.85), ("charlie", 0.25, 0.75, 2, 7)]
        ]
        
        for evidence_idx, responses in enumerate(evidence_responses):
            # Submit responses for all players
            for response in responses:
                if len(response) == 3:  # Direct probabilities only
                    player_id, prob_guilty, prob_innocent = response
                    success = game.submit_evidence_response(player_id, prob_guilty, prob_innocent)
                elif len(response) == 5:  # With ratings
                    player_id, prob_guilty, prob_innocent, guilty_rating, innocent_rating = response
                    success = game.submit_evidence_response(
                        player_id, prob_guilty, prob_innocent, guilty_rating, innocent_rating
                    )
                else:
                    self.fail(f"Invalid response format: {response}")
                self.assertTrue(success, f"Failed to submit response for {player_id}")
            
            # Check all players responded
            self.assertTrue(game.all_players_responded())
            
            # Advance evidence
            has_more = game.advance_evidence()
            expected_has_more = evidence_idx < len(evidence_responses) - 1
            self.assertEqual(has_more, expected_has_more)
        
        # Should now be in verdict phase
        self.assertEqual(game.phase, GamePhase.VERDICT)
        
        # Get final game state
        final_state = game.get_game_state()
        self.assertIn('verdict', final_state)
        
        verdict_info = final_state['verdict']
        self.assertIn('group_verdict', verdict_info)
        self.assertIn('statistics', verdict_info)
        
        # Verify each player has all responses
        for player_id in ["alice", "bob", "charlie"]:
            player_state = game.get_player_state(player_id)
            self.assertIsNotNone(player_state)
            self.assertEqual(len(player_state['responses']), 3)
        
        # Test saving results
        try:
            filename = game.save_game_results()
            self.assertTrue(os.path.exists(filename))
            os.unlink(filename)  # Clean up
        except Exception as e:
            self.fail(f"Failed to save game results: {e}")
        
        print(f"✓ Complete game simulation successful!")
        print(f"  Final verdict: {verdict_info['group_verdict']}")
        print(f"  Average evidence: {verdict_info['average_evidence_db']:.1f} db")
        print(f"  Voting: {verdict_info['statistics']['guilty_votes']} guilty, {verdict_info['statistics']['not_guilty_votes']} not guilty")


def run_all_tests():
    """Run all test cases."""
    print("Running Bayesian Court Game Core Logic Tests...")
    print("=" * 60)
    
    # Create test suite
    test_classes = [
        TestBayesianCalculator,
        TestCaseData,
        TestPlayerState,
        TestBayesianGame,
        TestUtilityFunctions,
        TestCompleteGameFlow
    ]
    
    total_tests = 0
    total_failures = 0
    
    for test_class in test_classes:
        print(f"\nRunning {test_class.__name__}...")
        suite = unittest.TestLoader().loadTestsFromTestCase(test_class)
        runner = unittest.TextTestRunner(verbosity=1)
        result = runner.run(suite)
        
        total_tests += result.testsRun
        total_failures += len(result.failures) + len(result.errors)
        
        if result.failures:
            print(f"  FAILURES in {test_class.__name__}:")
            for test, traceback in result.failures:
                print(f"    - {test}: {traceback}")
        
        if result.errors:
            print(f"  ERRORS in {test_class.__name__}:")
            for test, traceback in result.errors:
                print(f"    - {test}: {traceback}")
    
    print("\n" + "=" * 60)
    print(f"TOTAL TESTS: {total_tests}")
    print(f"FAILURES/ERRORS: {total_failures}")
    
    if total_failures == 0:
        print("🎉 ALL TESTS PASSED! Core logic is ready for web integration.")
    else:
        print("❌ Some tests failed. Please fix issues before proceeding.")
    
    return total_failures == 0


if __name__ == "__main__":
    run_all_tests()