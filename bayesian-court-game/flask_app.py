# app.py
"""
Flask web server for the Bayesian Court Game.
Provides REST API endpoints and real-time WebSocket communication.
"""

from flask import Flask, render_template, request, jsonify, session
from flask_socketio import SocketIO, emit, join_room, leave_room
import uuid
import json
from datetime import datetime
from typing import Dict, Optional
import logging

# Import our core game logic
from bayesian_core import (
    BayesianGame, 
    BayesianCalculator,
    GamePhase,
    list_case_files,
    validate_case_file
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'bayesian-court-game-secret-key-change-in-production'

# Initialize Socket.IO
socketio = SocketIO(app, cors_allowed_origins="*", logger=True, engineio_logger=True)

# Global game storage (in production, use Redis or database)
active_games: Dict[str, BayesianGame] = {}
player_sessions: Dict[str, str] = {}  # session_id -> game_id


class GameManager:
    """Manages active games and player sessions."""
    
    @staticmethod
    def create_game(case_file: str, max_players: int = 12) -> Optional[str]:
        """Create a new game and return game_id."""
        try:
            # Ensure case file path is correct
            if not case_file.startswith('case_files/'):
                case_file = f'case_files/{case_file}'
            
            # Validate case file first
            is_valid, error_msg = validate_case_file(case_file)
            if not is_valid:
                logger.error(f"Invalid case file {case_file}: {error_msg}")
                return None
            
            # Create game
            game_id = f"game_{uuid.uuid4().hex[:8]}"
            game = BayesianGame(case_file, game_id)
            game.max_players = max_players
            
            active_games[game_id] = game
            logger.info(f"Created game {game_id} with case file {case_file}")
            return game_id
            
        except Exception as e:
            logger.error(f"Error creating game: {e}")
            return None
    
    @staticmethod
    def get_game(game_id: str) -> Optional[BayesianGame]:
        """Get game by ID."""
        return active_games.get(game_id)
    
    @staticmethod
    def delete_game(game_id: str) -> bool:
        """Delete a game."""
        if game_id in active_games:
            del active_games[game_id]
            logger.info(f"Deleted game {game_id}")
            return True
        return False
    
    @staticmethod
    def add_player_to_game(game_id: str, session_id: str, player_name: str, 
                          guilt_tolerance: int, use_rating_scale: bool) -> bool:
        """Add player to game."""
        game = GameManager.get_game(game_id)
        if not game:
            return False
        
        # Use session_id as player_id for uniqueness
        success = game.add_player(session_id, player_name, guilt_tolerance, use_rating_scale)
        if success:
            player_sessions[session_id] = game_id
            logger.info(f"Added player {player_name} ({session_id}) to game {game_id}")
        
        return success
    
    @staticmethod
    def remove_player_from_game(session_id: str) -> bool:
        """Remove player from their current game."""
        if session_id not in player_sessions:
            return False
        
        game_id = player_sessions[session_id]
        game = GameManager.get_game(game_id)
        
        if game:
            game.remove_player(session_id)
            del player_sessions[session_id]
            logger.info(f"Removed player {session_id} from game {game_id}")
            return True
        
        return False
    
    @staticmethod
    def get_player_game(session_id: str) -> Optional[str]:
        """Get the game_id for a player's session."""
        return player_sessions.get(session_id)


# ============================================================================
# REST API Routes
# ============================================================================

@app.route('/')
def index():
    """Main game page."""
    return render_template('index.html')

@app.route('/admin')
def admin():
    """Admin page for managing games."""
    return render_template('admin.html')

@app.route('/api/case-files')
def get_case_files():
    """Get list of available case files."""
    try:
        case_files = list_case_files('case_files')
        validated_files = []
        
        for filename in case_files:
            is_valid, message = validate_case_file(f'case_files/{filename}')
            validated_files.append({
                'filename': filename,
                'is_valid': is_valid,
                'message': message
            })
        
        return jsonify({
            'success': True,
            'case_files': validated_files
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/games', methods=['GET'])
def get_active_games():
    """Get list of active games."""
    try:
        games_info = []
        for game_id, game in active_games.items():
            game_info = {
                'game_id': game_id,
                'case_name': game.case_data.case_info['name'],
                'phase': game.phase.value,
                'player_count': len(game.players),
                'max_players': game.max_players,
                'created_at': game.created_at.isoformat(),
                'can_join': len(game.players) < game.max_players and game.phase == GamePhase.SETUP
            }
            games_info.append(game_info)
        
        return jsonify({
            'success': True,
            'games': games_info
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/games', methods=['POST'])
def create_game():
    """Create a new game."""
    try:
        data = request.get_json()
        case_file = data.get('case_file')
        max_players = data.get('max_players', 12)
        
        if not case_file:
            return jsonify({
                'success': False,
                'error': 'Case file is required'
            }), 400
        
        game_id = GameManager.create_game(case_file, max_players)
        
        if game_id:
            return jsonify({
                'success': True,
                'game_id': game_id
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to create game'
            }), 500
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/games/<game_id>')
def get_game_info(game_id):
    """Get detailed information about a specific game."""
    try:
        game = GameManager.get_game(game_id)
        if not game:
            return jsonify({
                'success': False,
                'error': 'Game not found'
            }), 404
        
        game_state = game.get_game_state()
        return jsonify({
            'success': True,
            'game_state': game_state
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# ============================================================================
# WebSocket Event Handlers
# ============================================================================

@socketio.on('connect')
def handle_connect():
    """Handle client connection."""
    session_id = session.get('session_id')
    if not session_id:
        session_id = str(uuid.uuid4())
        session['session_id'] = session_id
    
    logger.info(f"Client connected: {session_id}")
    emit('connected', {'session_id': session_id})

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection."""
    session_id = session.get('session_id')
    if session_id:
        # Update player connection status
        game_id = GameManager.get_player_game(session_id)
        if game_id:
            game = GameManager.get_game(game_id)
            if game:
                game.set_player_connection_status(session_id, False)
                # Notify other players
                socketio.emit('player_disconnected', {
                    'player_id': session_id
                }, room=game_id)
        
        logger.info(f"Client disconnected: {session_id}")

@socketio.on('join_game')
def handle_join_game(data):
    """Handle player joining a game."""
    try:
        session_id = session.get('session_id')
        game_id = data.get('game_id')
        player_name = data.get('player_name')
        guilt_tolerance = data.get('guilt_tolerance')
        use_rating_scale = data.get('use_rating_scale', True)
        
        # Validate input
        if not all([session_id, game_id, player_name, guilt_tolerance]):
            emit('error', {'message': 'Missing required fields'})
            return
        
        # Add player to game
        success = GameManager.add_player_to_game(
            game_id, session_id, player_name, guilt_tolerance, use_rating_scale
        )
        
        if success:
            # Join socket room
            join_room(game_id)
            
            # Get updated game state
            game = GameManager.get_game(game_id)
            game_state = game.get_game_state()
            
            # Notify player
            emit('join_success', {
                'game_id': game_id,
                'player_id': session_id,
                'game_state': game_state
            })
            
            # Notify other players
            emit('player_joined', {
                'player_id': session_id,
                'player_name': player_name,
                'game_state': game_state
            }, room=game_id, include_self=False)
            
        else:
            emit('join_failed', {'message': 'Failed to join game'})
    
    except Exception as e:
        logger.error(f"Error in join_game: {e}")
        emit('error', {'message': str(e)})

@socketio.on('leave_game')
def handle_leave_game():
    """Handle player leaving a game."""
    try:
        session_id = session.get('session_id')
        game_id = GameManager.get_player_game(session_id)
        
        if game_id:
            # Remove player from game
            GameManager.remove_player_from_game(session_id)
            
            # Leave socket room
            leave_room(game_id)
            
            # Get updated game state
            game = GameManager.get_game(game_id)
            if game:
                game_state = game.get_game_state()
                
                # Notify other players
                emit('player_left', {
                    'player_id': session_id,
                    'game_state': game_state
                }, room=game_id)
            
            emit('leave_success')
        
    except Exception as e:
        logger.error(f"Error in leave_game: {e}")
        emit('error', {'message': str(e)})

@socketio.on('start_game')
def handle_start_game(data):
    """Handle starting a game."""
    try:
        session_id = session.get('session_id')
        game_id = data.get('game_id')
        
        game = GameManager.get_game(game_id)
        if not game:
            emit('error', {'message': 'Game not found'})
            return
        
        # Check if player is in the game
        if session_id not in game.players:
            emit('error', {'message': 'You are not in this game'})
            return
        
        # Start the game
        if game.start_game():
            game_state = game.get_game_state()
            
            # Notify all players
            socketio.emit('game_started', {
                'game_state': game_state
            }, room=game_id)
        else:
            emit('error', {'message': 'Cannot start game'})
    
    except Exception as e:
        logger.error(f"Error in start_game: {e}")
        emit('error', {'message': str(e)})

@socketio.on('advance_to_evidence')
def handle_advance_to_evidence(data):
    """Handle advancing from case presentation to evidence review."""
    try:
        session_id = session.get('session_id')
        game_id = data.get('game_id')
        
        game = GameManager.get_game(game_id)
        if not game:
            emit('error', {'message': 'Game not found'})
            return
        
        # Check if player is in the game
        if session_id not in game.players:
            emit('error', {'message': 'You are not in this game'})
            return
        
        # Advance to evidence review
        game.advance_to_evidence_review()
        game_state = game.get_game_state()
        
        # Notify all players
        socketio.emit('evidence_phase_started', {
            'game_state': game_state
        }, room=game_id)
    
    except Exception as e:
        logger.error(f"Error in advance_to_evidence: {e}")
        emit('error', {'message': str(e)})

@socketio.on('submit_evidence_response')
def handle_submit_evidence_response(data):
    """Handle player submitting evidence response."""
    try:
        session_id = session.get('session_id')
        game_id = GameManager.get_player_game(session_id)
        
        if not game_id:
            emit('error', {'message': 'You are not in a game'})
            return
        
        game = GameManager.get_game(game_id)
        if not game:
            emit('error', {'message': 'Game not found'})
            return
        
        # Extract response data
        prob_guilty = data.get('prob_guilty')
        prob_innocent = data.get('prob_innocent')
        guilty_rating = data.get('guilty_rating')
        innocent_rating = data.get('innocent_rating')
        
        # Submit response
        success = game.submit_evidence_response(
            session_id, prob_guilty, prob_innocent, guilty_rating, innocent_rating
        )
        
        if success:
            # Notify player of successful submission
            emit('response_submitted', {
                'evidence_index': game.current_evidence_index
            })
            
            # Get updated game state
            game_state = game.get_game_state()
            
            # Notify all players of response count update
            socketio.emit('response_received', {
                'player_id': session_id,
                'responses_received': len(game.responses_for_current_evidence),
                'total_players': len([p for p in game.players.values() if p.is_connected]),
                'all_responded': game.all_players_responded()
            }, room=game_id)
            
            # If all players have responded, automatically advance
            if game.all_players_responded():
                has_more_evidence = game.advance_evidence()
                game_state = game.get_game_state()
                
                if has_more_evidence:
                    # Move to next evidence
                    socketio.emit('evidence_completed', {
                        'game_state': game_state,
                        'next_evidence_index': game.current_evidence_index
                    }, room=game_id)
                else:
                    # Move to verdict phase
                    socketio.emit('all_evidence_completed', {
                        'game_state': game_state
                    }, room=game_id)
        else:
            emit('error', {'message': 'Failed to submit response'})
    
    except Exception as e:
        logger.error(f"Error in submit_evidence_response: {e}")
        emit('error', {'message': str(e)})

@socketio.on('get_game_state')
def handle_get_game_state(data):
    """Handle request for current game state."""
    try:
        session_id = session.get('session_id')
        game_id = data.get('game_id') or GameManager.get_player_game(session_id)
        
        if not game_id:
            emit('error', {'message': 'Game ID not provided and not in a game'})
            return
        
        game = GameManager.get_game(game_id)
        if not game:
            emit('error', {'message': 'Game not found'})
            return
        
        game_state = game.get_game_state()
        player_state = game.get_player_state(session_id)
        
        emit('game_state_update', {
            'game_state': game_state,
            'player_state': player_state
        })
    
    except Exception as e:
        logger.error(f"Error in get_game_state: {e}")
        emit('error', {'message': str(e)})


# ============================================================================
# Admin Routes (for testing and management)
# ============================================================================

@app.route('/api/admin/games/<game_id>', methods=['DELETE'])
def admin_delete_game(game_id):
    """Admin endpoint to delete a game."""
    try:
        success = GameManager.delete_game(game_id)
        if success:
            # Notify players that game was deleted
            socketio.emit('game_deleted', {'game_id': game_id}, room=game_id)
            return jsonify({'success': True})
        else:
            return jsonify({'success': False, 'error': 'Game not found'}), 404
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/admin/games/<game_id>/force-advance', methods=['POST'])
def admin_force_advance(game_id):
    """Admin endpoint to force advance game phase."""
    try:
        game = GameManager.get_game(game_id)
        if not game:
            return jsonify({'success': False, 'error': 'Game not found'}), 404
        
        if game.phase == GamePhase.CASE_PRESENTATION:
            game.advance_to_evidence_review()
        elif game.phase == GamePhase.EVIDENCE_REVIEW:
            game.advance_evidence()
        
        game_state = game.get_game_state()
        
        # Notify all players
        socketio.emit('admin_force_advance', {
            'game_state': game_state
        }, room=game_id)
        
        return jsonify({'success': True, 'new_phase': game.phase.value})
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# ============================================================================
# Error Handlers
# ============================================================================

@app.errorhandler(404)
def not_found(error):
    return jsonify({'success': False, 'error': 'Not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'success': False, 'error': 'Internal server error'}), 500


# ============================================================================
# Main Application Entry Point
# ============================================================================

if __name__ == '__main__':
    # Development configuration
    app.debug = True
    
    print("Starting Bayesian Court Game Server...")
    print("Available endpoints:")
    print("  GET  /                     - Main game page")
    print("  GET  /admin                - Admin page")
    print("  GET  /api/case-files       - List case files")
    print("  GET  /api/games            - List active games")
    print("  POST /api/games            - Create new game")
    print("  GET  /api/games/<id>       - Get game info")
    print("\nWebSocket events:")
    print("  join_game, leave_game, start_game")
    print("  advance_to_evidence, submit_evidence_response")
    print("  get_game_state")
    print("\nStarting server on http://localhost:5000")
    
    # Run the application
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
