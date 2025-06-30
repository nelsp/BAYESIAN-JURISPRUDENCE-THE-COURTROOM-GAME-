# Bayesian Jurisprudence: The Courtroom Game

A multi-player web-based game that simulates jury deliberation using Bayesian probability theory. Players analyze evidence and reach verdicts based on probability calculations.

## Features

### 🎮 Multi-Player Game
- Real-time web interface using Flask and Socket.IO
- Multiple players can join and participate simultaneously
- Live updates of game state and player responses

### 📊 Bayesian Probability System
- Evidence evaluation using probability theory
- Decibel-based evidence strength calculations
- Individual guilt thresholds for each player
- Group verdict calculation based on collective evidence

### 🧠 Philosophical Quiz
- 24-dimensional personality assessment
- 1-10 rating scale for nuanced responses
- Radar chart visualization of philosophical leanings
- Covers dimensions like Rationality, Mysticism, Individualism, Collectivism, etc.

## Project Structure

```
├── bayesian-court-game/          # Flask web application
│   ├── flask_app.py             # Main Flask server
│   ├── bayesian_core.py         # Core game logic
│   ├── templates/               # HTML templates
│   │   ├── index.html          # Main game interface
│   │   └── admin.html          # Admin panel
│   ├── case_files/             # JSON case files
│   └── game_results/           # Saved game results
├── bayesian_core.py            # Core Bayesian logic (standalone)
├── test_bayesian_core.py       # Unit tests
├── phil_quiz.py                # Philosophical assessment tool
├── guilt_or_innocence_game.py  # Original single-player version
└── README.md                   # This file
```

## Getting Started

### Prerequisites
- Python 3.7+
- Flask
- Flask-SocketIO
- matplotlib (for phil_quiz.py)

### Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/nelsp/BAYESIAN-JURISPRUDENCE-THE-COURTROOM-GAME-.git
   cd BAYESIAN-JURISPRUDENCE-THE-COURTROOM-GAME-
   ```

2. Install dependencies:
   ```bash
   pip install flask flask-socketio matplotlib numpy
   ```

### Running the Web Game
1. Navigate to the Flask app directory:
   ```bash
   cd bayesian-court-game
   ```

2. Start the server:
   ```bash
   python flask_app.py
   ```

3. Open your browser to `http://localhost:5000`

### Running the Philosophical Quiz
```bash
python phil_quiz.py
```

### Running Tests
```bash
python test_bayesian_core.py
```

## How to Play

### Web Game
1. **Create a Game**: Select a case file and set maximum players
2. **Join as Player**: Enter your name and guilt tolerance settings
3. **Start Game**: Click "Start Game" when ready
4. **Review Case**: Read the case information
5. **Evaluate Evidence**: Rate each piece of evidence on probability scales
6. **Reach Verdict**: See the group's final decision

### Philosophical Quiz
1. Answer questions on a 1-10 scale
2. Questions cover 24 different philosophical dimensions
3. View your results as a radar chart
4. Compare your philosophical leanings across dimensions

## Case Files

The game includes several pre-built case files:
- **Biker Bar Murder Case**: Complex murder investigation
- **Gentleman's Club Murder Case**: High-profile case
- **Jewelry Heist Case**: Property crime investigation
- **Manor Murder Case**: Classic whodunit scenario
- **Stolen Photos Case**: Digital evidence case

## Technical Details

### Bayesian Calculations
- Evidence strength measured in decibels
- Prior probability based on population statistics
- Likelihood ratios for evidence evaluation
- Posterior probability updates after each piece of evidence

### Web Technologies
- **Backend**: Flask with Socket.IO for real-time communication
- **Frontend**: HTML5, CSS3, JavaScript with Socket.IO client
- **Data**: JSON case files and game state management

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is open source and available under the MIT License.

## Acknowledgments

- Based on Bayesian probability theory and jury deliberation research
- Inspired by educational games that teach statistical reasoning
- Built for educational and research purposes
