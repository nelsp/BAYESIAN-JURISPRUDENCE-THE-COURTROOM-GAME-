# bayesian_core.py
"""
Core Bayesian jurisprudence game logic for multi-player web game.
Extracted and refactored from the original single-player version.
"""

import math
import json
import os
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum


class GamePhase(Enum):
    """Enumeration of game phases."""
    SETUP = "setup"
    CASE_PRESENTATION = "case_presentation" 
    EVIDENCE_REVIEW = "evidence_review"
    VERDICT = "verdict"
    COMPLETED = "completed"


@dataclass
class PlayerResponse:
    """Data class for storing a player's response to evidence."""
    player_id: str
    evidence_index: int
    evidence_name: str
    prob_guilty: float
    prob_innocent: float
    used_rating_scale: bool
    db_update: float
    guilty_rating: Optional[int] = None
    innocent_rating: Optional[int] = None
    timestamp: str = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()


@dataclass
class PlayerState:
    """Data class for tracking individual player state."""
    player_id: str
    name: str
    guilt_threshold_db: float
    prior_guilt_tolerance: int
    current_evidence_db: float
    responses: List[PlayerResponse]
    use_rating_scale: bool
    is_connected: bool = True
    
    def add_response(self, response: PlayerResponse):
        """Add a response and update current evidence level."""
        self.responses.append(response)
        self.current_evidence_db += response.db_update
    
    def get_current_guilt_probability(self) -> float:
        """Get current probability of guilt as percentage."""
        return BayesianCalculator.decibels_to_probability(self.current_evidence_db) * 100
    
    def would_convict(self) -> bool:
        """Check if current evidence meets conviction threshold."""
        return self.current_evidence_db >= self.guilt_threshold_db


class BayesianCalculator:
    """Static methods for Bayesian probability calculations."""
    
    # Rating scale mapping from original game
    RATING_TO_PROBABILITY = {
        0: 0.001,
        1: 0.02,
        2: 0.1,
        3: 0.2,
        4: 0.35,
        5: 0.5,
        6: 0.65,
        7: 0.8,
        8: 0.9,
        9: 0.98,
        10: 0.999,
    }
    
    @staticmethod
    def decibels_to_probability(db: float) -> float:
        """Convert decibels to probability."""
        if db > 0:
            return 1 - (1 / (10 ** (db / 10)))
        else:
            return 1 / (10 ** (abs(db) / 10))
    
    @staticmethod
    def probability_to_decibels(prob: float) -> float:
        """Convert probability to decibels."""
        if prob >= 0.5:
            return 10 * math.log10(prob / (1 - prob))
        else:
            return -10 * math.log10((1 - prob) / prob)
    
    @staticmethod
    def calculate_db_update(prob_guilty: float, prob_innocent: float) -> float:
        """Calculate evidence update in decibels."""
        return 10 * math.log10(prob_guilty / prob_innocent)
    
    @staticmethod
    def calculate_guilt_threshold(tolerance: int) -> float:
        """Calculate conviction threshold in decibels from tolerance ratio."""
        return 10 * math.log10(tolerance)
    
    @staticmethod
    def rating_to_probability(rating: int) -> float:
        """Convert integer rating (0-10) to probability."""
        return BayesianCalculator.RATING_TO_PROBABILITY.get(rating, 0.5)
    
    @staticmethod
    def average_evidence_levels(players: List[PlayerState]) -> float:
        """Calculate average evidence level across all players."""
        if not players:
            return 0.0
        return sum(player.current_evidence_db for player in players) / len(players)
    
    @staticmethod
    def calculate_group_verdict(players: List[PlayerState]) -> Tuple[str, float, Dict]:
        """
        Calculate group verdict based on average evidence levels and individual thresholds.
        Returns: (verdict, average_db, stats_dict)
        """
        if not players:
            return "NO PLAYERS", 0.0, {}
        
        avg_evidence_db = BayesianCalculator.average_evidence_levels(players)
        avg_guilt_prob = BayesianCalculator.decibels_to_probability(avg_evidence_db) * 100
        
        # Count individual verdicts
        guilty_votes = sum(1 for player in players if player.would_convict())
        not_guilty_votes = len(players) - guilty_votes
        
        # Group verdict based on majority of individual thresholds
        group_verdict = "GUILTY" if guilty_votes > not_guilty_votes else "NOT GUILTY"
        
        stats = {
            "average_evidence_db": avg_evidence_db,
            "average_guilt_probability": avg_guilt_prob,
            "guilty_votes": guilty_votes,
            "not_guilty_votes": not_guilty_votes,
            "total_players": len(players),
            "unanimous": guilty_votes == 0 or not_guilty_votes == 0
        }
        
        return group_verdict, avg_evidence_db, stats


class CaseData:
    """Class for managing case data loaded from JSON files."""
    
    def __init__(self, case_file: str):
        self.case_file = case_file
        self.data = self._load_case_file()
        self.validate_case_data()
    
    def _load_case_file(self) -> Dict:
        """Load case data from JSON file."""
        try:
            with open(self.case_file, 'r') as file:
                return json.load(file)
        except FileNotFoundError:
            raise FileNotFoundError(f"Could not find case file '{self.case_file}'")
        except json.JSONDecodeError:
            raise ValueError(f"Invalid JSON format in case file '{self.case_file}'")
    
    def validate_case_data(self):
        """Validate that required fields exist in case data."""
        required_fields = ['case', 'prior', 'evidence']
        for field in required_fields:
            if field not in self.data:
                raise ValueError(f"Missing required field '{field}' in case data")
        
        # Validate case structure
        case_required = ['name', 'description']
        for field in case_required:
            if field not in self.data['case']:
                raise ValueError(f"Missing required field 'case.{field}' in case data")
        
        # Validate prior structure
        prior_required = ['db', 'odds']
        for field in prior_required:
            if field not in self.data['prior']:
                raise ValueError(f"Missing required field 'prior.{field}' in case data")
        
        # Validate evidence structure
        if not isinstance(self.data['evidence'], list):
            raise ValueError("Evidence must be a list")
        
        for i, evidence in enumerate(self.data['evidence']):
            evidence_required = ['name', 'description']
            for field in evidence_required:
                if field not in evidence:
                    raise ValueError(f"Missing required field 'evidence[{i}].{field}' in case data")
    
    @property
    def case_info(self) -> Dict:
        """Get case information."""
        return self.data['case']
    
    @property
    def prior_info(self) -> Dict:
        """Get prior probability information."""
        return self.data['prior']
    
    @property
    def evidence_list(self) -> List[Dict]:
        """Get list of evidence items."""
        return self.data['evidence']
    
    @property
    def evidence_count(self) -> int:
        """Get number of evidence items."""
        return len(self.data['evidence'])
    
    def get_evidence(self, index: int) -> Dict:
        """Get specific evidence item by index."""
        if 0 <= index < len(self.data['evidence']):
            return self.data['evidence'][index]
        raise IndexError(f"Evidence index {index} out of range")


class BayesianGame:
    """Main game class that manages the multi-player Bayesian jurisprudence game."""
    
    def __init__(self, case_file: str, game_id: str = None):
        self.game_id = game_id or self._generate_game_id()
        self.case_data = CaseData(case_file)
        self.players: Dict[str, PlayerState] = {}
        self.phase = GamePhase.SETUP
        self.current_evidence_index = 0
        self.created_at = datetime.now()
        self.max_players = 12
        self.responses_for_current_evidence: Dict[str, PlayerResponse] = {}
    
    def _generate_game_id(self) -> str:
        """Generate a unique game ID."""
        return f"game_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    def add_player(self, player_id: str, name: str, guilt_tolerance: int, 
                   use_rating_scale: bool = True) -> bool:
        """
        Add a player to the game.
        Returns True if successful, False if game is full or player already exists.
        """
        if len(self.players) >= self.max_players:
            return False
        
        if player_id in self.players:
            return False
        
        guilt_threshold_db = BayesianCalculator.calculate_guilt_threshold(guilt_tolerance)
        
        player_state = PlayerState(
            player_id=player_id,
            name=name,
            guilt_threshold_db=guilt_threshold_db,
            prior_guilt_tolerance=guilt_tolerance,
            current_evidence_db=self.case_data.prior_info['db'],
            responses=[],
            use_rating_scale=use_rating_scale
        )
        
        self.players[player_id] = player_state
        return True
    
    def remove_player(self, player_id: str) -> bool:
        """Remove a player from the game."""
        if player_id in self.players:
            del self.players[player_id]
            # Also remove their response for current evidence if it exists
            if player_id in self.responses_for_current_evidence:
                del self.responses_for_current_evidence[player_id]
            return True
        return False
    
    def set_player_connection_status(self, player_id: str, is_connected: bool):
        """Update player connection status."""
        if player_id in self.players:
            self.players[player_id].is_connected = is_connected
    
    def can_start_game(self) -> bool:
        """Check if game can be started (at least 1 player)."""
        return len(self.players) >= 1 and self.phase == GamePhase.SETUP
    
    def start_game(self) -> bool:
        """Start the game if conditions are met."""
        if self.can_start_game():
            self.phase = GamePhase.CASE_PRESENTATION
            return True
        return False
    
    def advance_to_evidence_review(self):
        """Advance from case presentation to evidence review."""
        if self.phase == GamePhase.CASE_PRESENTATION:
            self.phase = GamePhase.EVIDENCE_REVIEW
            self.current_evidence_index = 0
    
    def submit_evidence_response(self, player_id: str, prob_guilty: float, 
                                prob_innocent: float, guilty_rating: int = None, 
                                innocent_rating: int = None) -> bool:
        """
        Submit a player's response to the current evidence.
        Returns True if successful, False if player not found or invalid phase.
        """
        if self.phase != GamePhase.EVIDENCE_REVIEW:
            return False
        
        if player_id not in self.players:
            return False
        
        player = self.players[player_id]
        
        # Calculate decibel update
        db_update = BayesianCalculator.calculate_db_update(prob_guilty, prob_innocent)
        
        # Create response object
        response = PlayerResponse(
            player_id=player_id,
            evidence_index=self.current_evidence_index,
            evidence_name=self.case_data.get_evidence(self.current_evidence_index)['name'],
            prob_guilty=prob_guilty,
            prob_innocent=prob_innocent,
            used_rating_scale=player.use_rating_scale,
            db_update=db_update,
            guilty_rating=guilty_rating,
            innocent_rating=innocent_rating
        )
        
        # Store response
        self.responses_for_current_evidence[player_id] = response
        
        return True
    
    def all_players_responded(self) -> bool:
        """Check if all connected players have responded to current evidence."""
        connected_players = [pid for pid, player in self.players.items() if player.is_connected]
        return len(self.responses_for_current_evidence) == len(connected_players)
    
    def advance_evidence(self) -> bool:
        """
        Process current evidence responses and advance to next evidence or verdict.
        Returns True if advanced to next evidence, False if moving to verdict phase.
        """
        if self.phase != GamePhase.EVIDENCE_REVIEW:
            return False
        
        # Add responses to player states
        for player_id, response in self.responses_for_current_evidence.items():
            if player_id in self.players:
                self.players[player_id].add_response(response)
        
        # Clear current responses
        self.responses_for_current_evidence.clear()
        
        # Check if more evidence to review
        if self.current_evidence_index < self.case_data.evidence_count - 1:
            self.current_evidence_index += 1
            return True
        else:
            # Move to verdict phase
            self.phase = GamePhase.VERDICT
            return False
    
    def get_game_state(self) -> Dict:
        """Get current game state for sending to clients."""
        state = {
            'game_id': self.game_id,
            'phase': self.phase.value,
            'case_info': self.case_data.case_info,
            'prior_info': self.case_data.prior_info,
            'current_evidence_index': self.current_evidence_index,
            'total_evidence_count': self.case_data.evidence_count,
            'players': {
                pid: {
                    'name': player.name,
                    'is_connected': player.is_connected,
                    'current_guilt_probability': player.get_current_guilt_probability(),
                    'current_evidence_db': player.current_evidence_db,
                    'responses_count': len(player.responses)
                }
                for pid, player in self.players.items()
            },
            'responses_received': len(self.responses_for_current_evidence),
            'waiting_for_responses': not self.all_players_responded()
        }
        
        # Add current evidence if in evidence review phase
        if self.phase == GamePhase.EVIDENCE_REVIEW:
            current_evidence = self.case_data.get_evidence(self.current_evidence_index)
            state['current_evidence'] = current_evidence
        
        # Add verdict information if in verdict phase
        if self.phase == GamePhase.VERDICT:
            verdict, avg_db, stats = BayesianCalculator.calculate_group_verdict(list(self.players.values()))
            state['verdict'] = {
                'group_verdict': verdict,
                'average_evidence_db': avg_db,
                'statistics': stats
            }
        
        return state
    
    def get_player_state(self, player_id: str) -> Optional[Dict]:
        """Get detailed state for a specific player."""
        if player_id not in self.players:
            return None
        
        player = self.players[player_id]
        return {
            'player_id': player_id,
            'name': player.name,
            'guilt_threshold_db': player.guilt_threshold_db,
            'prior_guilt_tolerance': player.prior_guilt_tolerance,
            'current_evidence_db': player.current_evidence_db,
            'current_guilt_probability': player.get_current_guilt_probability(),
            'would_convict': player.would_convict(),
            'use_rating_scale': player.use_rating_scale,
            'responses': [asdict(response) for response in player.responses],
            'is_connected': player.is_connected
        }
    
    def save_game_results(self, filename: str = None) -> str:
        """Save game results to JSON file."""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            base, ext = os.path.splitext(self.case_data.case_file)
            filename = f"{base}_results_{self.game_id}_{timestamp}{ext}"
        
        # Calculate final results
        verdict, avg_db, stats = BayesianCalculator.calculate_group_verdict(list(self.players.values()))
        
        results = {
            'game_id': self.game_id,
            'case_file': self.case_data.case_file,
            'created_at': self.created_at.isoformat(),
            'completed_at': datetime.now().isoformat(),
            'case_data': self.case_data.data,
            'final_verdict': verdict,
            'final_statistics': stats,
            'players': {
                pid: asdict(player) for pid, player in self.players.items()
            }
        }
        
        try:
            with open(filename, 'w') as file:
                json.dump(results, file, indent=2, default=str)
            return filename
        except Exception as e:
            raise Exception(f"Error saving results: {e}")


# Utility functions for case file management
def list_case_files(directory: str = '.') -> List[str]:
    """List available JSON case files, excluding result files."""
    case_files = [
        f for f in os.listdir(directory) 
        if f.endswith('.json') and '_results_' not in f and '_played_' not in f
    ]
    return sorted(case_files)


def validate_case_file(filename: str) -> Tuple[bool, str]:
    """
    Validate a case file format.
    Returns (is_valid, error_message)
    """
    try:
        case_data = CaseData(filename)
        return True, "Valid case file"
    except Exception as e:
        return False, str(e)


# Example usage and testing
if __name__ == "__main__":
    # This section can be used for testing the core logic
    print("Bayesian Court Game - Core Logic Module")
    print("Testing basic functionality...")
    
    # Test case file listing
    case_files = list_case_files()
    print(f"Found {len(case_files)} case files: {case_files}")
    
    # Test calculator functions
    print(f"Decibels to probability (10 db): {BayesianCalculator.decibels_to_probability(10):.4f}")
    print(f"Probability to decibels (0.9): {BayesianCalculator.probability_to_decibels(0.9):.2f} db")
    print(f"Guilt threshold for 1 in 100: {BayesianCalculator.calculate_guilt_threshold(100):.2f} db")
    
    print("Core logic module ready for integration!")
