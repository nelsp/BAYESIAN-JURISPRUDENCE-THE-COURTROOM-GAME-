import math
import time
import json
import os

from datetime import datetime

def decibels_to_probability(db):
    """Convert decibels to probability."""
    if db > 0:
        return 1 - (1 / (10 ** (db / 10)))
    else:
        return 1 / (10 ** (abs(db) / 10))

def probability_to_decibels(prob):
    """Convert probability to decibels."""
    if prob >= 0.5:
        return 10 * math.log10(prob / (1 - prob))
    else:
        return -10 * math.log10((1 - prob) / prob)

def print_slowly(text, delay=0.005):
    """Print text with a typing effect."""
    for char in text:
        print(char, end='', flush=True)
        time.sleep(delay)
    print()
    time.sleep(0.5)

def clear_screen():
    """Clear the console screen."""
    print("\n" * 50)

def get_valid_number(prompt, min_val=0, max_val=1, allow_float=True):
    """Get a valid number input from the user."""
    while True:
        try:
            value = float(input(prompt))
            if value < min_val:
                print(f"Please enter a number greater than or equal to {min_val}.")
                continue
            if max_val is not None and value > max_val:
                print(f"Please enter a number less than or equal to {max_val}.")
                continue
            if not allow_float:
                value = int(value)
            return value
        except ValueError:
            print("Please enter a valid number.")

def print_title():
    """Print the game title."""
    title = """
    ╔══════════════════════════════════════════════════════════════╗
    ║                                                              ║
    ║          BAYESIAN JURISPRUDENCE: THE COURTROOM GAME          ║
    ║                                                              ║
    ╚══════════════════════════════════════════════════════════════╝
    """
    print_slowly(title, delay=0.005)

class BayesianCourtGame:
    """A flexible game applying Bayesian reasoning to a courtroom scenario."""
    
    def __init__(self, case_file):
        self.case_file = case_file
        self.case_data = self.load_case_file()
        self.prior_guilt_tolerance = None
        self.guilt_threshold_db = None
        self.current_evidence_db = self.case_data["prior"]["db"]
        self.player_responses = []
        self.evidence_presented = 0
        self.use_rating_scale = None  # Will be set by set_probability_input_method
        self.integer_probability_dict = {
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
        
    def load_case_file(self):
        """Load case data from JSON file."""
        try:
            with open(self.case_file, 'r') as file:
                return json.load(file)
        except FileNotFoundError:
            print(f"Error: Could not find case file '{self.case_file}'")
            exit(1)
        except json.JSONDecodeError:
            print(f"Error: Invalid JSON format in case file '{self.case_file}'")
            exit(1)
    
    def save_case_file(self, filename=None):
        """Save updated case data to JSON file."""
        if filename is None:
            # Create a new filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            base, ext = os.path.splitext(self.case_file)
            filename = f"{base}_played_{timestamp}{ext}"
        
        # Add player responses to case data
        self.case_data["player_responses"] = self.player_responses
        self.case_data["final_evidence_db"] = self.current_evidence_db
        self.case_data["guilt_threshold_db"] = self.guilt_threshold_db
        self.case_data["verdict"] = "GUILTY" if self.current_evidence_db >= self.guilt_threshold_db else "NOT GUILTY"
        
        try:
            with open(filename, 'w') as file:
                json.dump(self.case_data, file, indent=2)
            print(f"\nGame results saved to {filename}")
        except Exception as e:
            print(f"Error saving results: {e}")
    
    def set_probability_input_method(self):
        """Set the default method for entering probabilities."""
        print_slowly("\nBefore we begin, please choose how you'd like to enter probabilities:")
        print_slowly("1. Using a rating scale from 0-10")
        print_slowly("   0 = Very unlikely (0.1%)")
        print_slowly("   5 = Equal chance (50%)")
        print_slowly("   10 = Almost certain (99.9%)")
        print_slowly("2. Entering a probability directly (0-1)")
        
        while True:
            choice = input("\nEnter your choice (1 or 2): ").strip()
            if choice == '1':
                self.use_rating_scale = True
                break
            elif choice == '2':
                self.use_rating_scale = False
                break
            else:
                print("Please enter either 1 or 2.")
        
        print_slowly("\nYou've chosen to use the " + ("rating scale" if self.use_rating_scale else "direct probability input") + " method.")
        print_slowly("This will be your default method for all evidence assessments.")
        input("\nPress Enter to continue...")
        clear_screen()

    def start_game(self):
        """Start the Bayesian court game."""
        print_title()
        
        print_slowly("Welcome to the Bayesian Jurisprudence simulation.")
        print_slowly("In this game, you'll analyze evidence in a criminal case using Bayesian probability.")
        print_slowly("You'll estimate the probability of guilt as new evidence is presented.")
        
        # Set the default probability input method
        self.set_probability_input_method()
        
        # Set the player's tolerance for false convictions first
        self.set_guilt_threshold()
        
        input("\nPress Enter to see the case details...")
        clear_screen()
        
        # Present the case information
        self.present_case()
        
        # List all pieces of evidence first
        print_slowly("\n=== LIST OF EVIDENCE TO BE PRESENTED ===")
        for i, evidence in enumerate(self.case_data["evidence"], 1):
            print_slowly(f"\nEvidence {i}: {evidence['name']}")
            print_slowly(f"Description: {evidence['description']}")
        
        input("\nPress Enter to begin analyzing each piece of evidence...")
        clear_screen()
        
        # Present each piece of evidence and update
        for i in range(len(self.case_data["evidence"])):
            self.present_evidence(i)
            self.get_player_probabilities(i)
        
        # Final verdict
        self.deliver_verdict()
        
        # Save results
        self.save_case_file()
    
    def set_guilt_threshold(self):
        """Set the player's tolerance for false convictions."""
        print_slowly("\nBefore we proceed, we need to establish your standards for conviction.")
        print_slowly("How many innocent people would you be willing to convict per guilty conviction?")
        print_slowly("For example, if you say '1 in 100', that means you accept that")
        print_slowly("1 out of every 100 convictions may be of an innocent person.")
        print_slowly("so 1 out of 10 is 90%, 1 out of 20 is 95%, 1 out of 100 is 99%, 1 out of 200 is 99.5%")
        print_slowly("1 out of every 10,000 convictions would be 99.99%.")
        
        tolerance = get_valid_number("\nEnter your tolerance (e.g., for 1 in 200, enter 200): ", min_val=10, max_val=None, allow_float=False)
        
        self.prior_guilt_tolerance = tolerance
        self.guilt_threshold_db = 10 * math.log10(tolerance)
        
        print_slowly(f"\nBased on your tolerance, the threshold for conviction is:")
        print_slowly(f"{self.guilt_threshold_db:.1f} decibels of evidence")
        print_slowly(f"This corresponds to a {(1 - 1/tolerance) * 100:.4f}% certainty of guilt.")
        
        print_slowly("\nTo understand this threshold:")
        print_slowly(f"- If you convict when evidence reaches {self.guilt_threshold_db:.1f} decibels")
        print_slowly(f"- Then statistically, only 1 in {tolerance} convictions would be of an innocent person")
        print_slowly("- This helps ensure a high standard of proof for criminal cases")
        
        input("\nPress Enter to continue...")
        clear_screen()
    
    def present_case(self):
        """Present the initial case scenario."""
        case = self.case_data["case"]
        
        print_slowly("\n=== THE CASE ===")
        print_slowly(f"\n{case['name']}")
        print_slowly(f"{case['description']}")
        print_slowly(f"The case takes place in a location with {case['population']} people.")
        
        print_slowly("\nInitially, with no specific evidence, the probability that any particular person")
        print_slowly(f"is guilty is:")
        print_slowly(f"• Prior probability = {self.case_data['prior']['odds']}")
        print_slowly(f"• In decibels: e(guilty|X) = {self.case_data['prior']['db']} db")
        
        # Print the reasoning for base probability if it exists
        if "reasoning" in self.case_data["prior"]:
            print_slowly("\n=== Base Probability Reasoning ===")
            print_slowly(self.case_data["prior"]["reasoning"])
        
        input("\nPress Enter to begin examining evidence...")
        clear_screen()
    
    def present_evidence(self, evidence_index):
        """Present a piece of evidence to the player."""
        self.evidence_presented = evidence_index + 1
        evidence = self.case_data["evidence"][evidence_index]
        
        print_slowly(f"\n=== EVIDENCE {evidence_index + 1}: {evidence['name']} ===")
        print_slowly(f"\n{evidence['description']}")
        
        print_slowly(f"\nCurrent evidence level: {self.current_evidence_db:.1f} db")
        print_slowly(f"This corresponds to a {decibels_to_probability(self.current_evidence_db) * 100:.4f}% probability of guilt.")
    
    def get_player_probabilities(self, evidence_index):
        """Get the player's probability estimates and calculate the update."""
        evidence = self.case_data["evidence"][evidence_index]
        
        while True:  # Loop until user confirms their inputs
            # Use the default method set at the start
            use_rating = self.use_rating_scale
            
            if use_rating:
                print_slowly("\nRate these probabilities on a scale of 0-10:")
                print_slowly("   0 = Very unlikely (0.1%)")
                print_slowly("   5 = Equal chance (50%)")
                print_slowly("   10 = Almost certain (99.9%)")
                # Get probability for innocent first
                innocent_rating = get_valid_number("\nRate likelihood if INNOCENT P(evidence|innocent)(0-10): ", min_val=0, max_val=10, allow_float=False)
                prob_innocent = self.integer_probability_dict[innocent_rating]
                
                guilty_rating = get_valid_number("Rate likelihood if GUILTY P(evidence|guilty)(0-10): ", min_val=0, max_val=10, allow_float=False)
                prob_guilty = self.integer_probability_dict[guilty_rating]
            else:
                print_slowly("\nEnter probabilities between 0 and 1:")
                # Get probability for innocent first
                prob_innocent = get_valid_number("\nP(evidence|innocent) - Enter probability (0-1): ", min_val=0.00001, max_val=0.9999)
                prob_guilty = get_valid_number("P(evidence|guilty) - Enter probability (0-1): ", min_val=0.0001, max_val=0.9999)
                guilty_rating = None
                innocent_rating = None
            
            # Calculate update in decibels
            db_update = 10 * math.log10(prob_guilty / prob_innocent)
            
            # Display the current estimates for confirmation
            print_slowly(f"\nYour current probability estimates:")
            if use_rating:
                print_slowly(f"• Guilty rating: {guilty_rating}/10 → P(evidence|guilty) = {prob_guilty:.4f}")
                print_slowly(f"• Innocent rating: {innocent_rating}/10 → P(evidence|innocent) = {prob_innocent:.4f}")
            else:
                print_slowly(f"• P(evidence|guilty) = {prob_guilty:.4f}")
                print_slowly(f"• P(evidence|innocent) = {prob_innocent:.4f}")
            print_slowly(f"• Likelihood ratio = {prob_guilty/prob_innocent:.4f}")
            print_slowly(f"• Evidence update = {db_update:.1f} db")
            
            # Ask for confirmation
            confirm = input("\nAre you sure about these values? (y/n): ").lower().strip()
            if confirm == 'y':
                break
            else:
                print_slowly("\nLet's try again...")
                clear_screen()
                self.present_evidence(evidence_index)  # Re-present the evidence
        
        # Store the player's response
        player_response = {
            "evidence_index": evidence_index,
            "evidence_name": evidence["name"],
            "player_prob_guilty": prob_guilty,
            "player_prob_innocent": prob_innocent,
            "used_rating_scale": use_rating,
            "db_update": db_update,
            "actual_prob_guilty": evidence.get("prob_guilty", None),
            "actual_prob_innocent": evidence.get("prob_innocent", None),
        }
        
        # Only include ratings if using the rating scale
        if use_rating:
            player_response["player_guilty_rating"] = guilty_rating
            player_response["player_innocent_rating"] = innocent_rating
        
        if "prob_guilty" in evidence and "prob_innocent" in evidence:
            actual_db_update = 10 * math.log10(evidence["prob_guilty"] / evidence["prob_innocent"])
            player_response["actual_db_update"] = actual_db_update
        
        self.player_responses.append(player_response)
        
        # Update the current evidence level
        self.current_evidence_db += db_update
        
        # Display final results
        print_slowly(f"\nYour probability estimates:")
        if use_rating:
            print_slowly(f"• Guilty rating: {guilty_rating}/10 → P(evidence|guilty) = {prob_guilty:.4f}")
            print_slowly(f"• Innocent rating: {innocent_rating}/10 → P(evidence|innocent) = {prob_innocent:.4f}")
        else:
            print_slowly(f"• P(evidence|guilty) = {prob_guilty:.4f}")
            print_slowly(f"• P(evidence|innocent) = {prob_innocent:.4f}")
        print_slowly(f"• Likelihood ratio = {prob_guilty/prob_innocent:.4f}")
        print_slowly(f"• Evidence update = {db_update:.1f} db")
        
        if "prob_guilty" in evidence and "prob_innocent" in evidence:
            print_slowly(f"\nActual values in case file:")
            print_slowly(f"• P(evidence|guilty) = {evidence['prob_guilty']:.4f}")
            print_slowly(f"• P(evidence|innocent) = {evidence['prob_innocent']:.4f}")
            print_slowly(f"• Likelihood ratio = {evidence['prob_guilty']/evidence['prob_innocent']:.4f}")
            print_slowly(f"• Evidence update = {actual_db_update:.1f} db")
        
        print_slowly(f"\nThe evidence level is now {self.current_evidence_db:.1f} db")
        print_slowly(f"This corresponds to a {decibels_to_probability(self.current_evidence_db) * 100:.4f}% probability of guilt.")
        
        # Print the explanation if it exists in the evidence data
        if "explanation" in evidence:
            print_slowly("\n=== Explanation ===")
            print_slowly(evidence["explanation"])
        
        # Save the updated db to the evidence item
        evidence["player_db_update"] = db_update
        evidence["updated_total_db"] = self.current_evidence_db
        
        if self.evidence_presented < len(self.case_data["evidence"]):
            input("\nPress Enter to continue to the next piece of evidence...")
        else:
            input("\nPress Enter to deliver the final verdict...")
        
        clear_screen()
    
    def deliver_verdict(self):
        """Deliver the final verdict based on all evidence."""
        print_slowly("\n=== FINAL VERDICT ===")
        print_slowly(f"\nCase: {self.case_data['case']['name']}")
        
        print_slowly(f"\nYour evidence assessment:")
        for i, response in enumerate(self.player_responses):
            print_slowly(f"Evidence {i+1} - {response['evidence_name']}: {response['db_update']:.1f} db")
        
        print_slowly(f"\nFinal evidence level: {self.current_evidence_db:.1f} db")
        guilt_probability = decibels_to_probability(self.current_evidence_db) * 100
        print_slowly(f"Final probability of guilt: {guilt_probability:.4f}%")
        print_slowly(f"Your conviction threshold: {self.guilt_threshold_db:.1f} db")
        
        if self.current_evidence_db >= self.guilt_threshold_db:
            print_slowly("\nVERDICT: GUILTY - The evidence exceeds your threshold for conviction.")
        else:
            print_slowly("\nVERDICT: NOT GUILTY - The evidence does not meet your threshold for conviction.")
            print_slowly("This does not mean the defendant is innocent, only that the evidence")
            print_slowly("is insufficient to justify conviction by your standards.")
        
        # Calculate how much more evidence would be needed
        if self.current_evidence_db < self.guilt_threshold_db:
            evidence_needed = self.guilt_threshold_db - self.current_evidence_db
            print_slowly(f"\nAdditional evidence of {evidence_needed:.1f} db would be needed to convict.")
        
        print_slowly("\nThank you for participating in this Bayesian reasoning exercise!")


def list_case_files():
    """List available JSON case files in the current directory."""
    # Filter out files that end with _played_ in their name
    case_files = [f for f in os.listdir('.') if f.endswith('.json') and '_played_' not in f]
    if not case_files:
        print("No JSON case files found in the current directory.")
        return None
    
    print("\nAvailable case files:")
    for i, file in enumerate(case_files):
        print(f"{i+1}. {file}")
    
    choice = get_valid_number("\nEnter the number of the case file to use: ", min_val=1, max_val=len(case_files), allow_float=False)
    return case_files[choice-1]


if __name__ == "__main__":
    print_slowly("Welcome to the Bayesian Court Game!")
    print_slowly("This program will guide you through analyzing legal evidence using Bayesian probability theory.")
    
    # Either select a case file or use a default
    case_file = list_case_files()
    if not case_file:
        case_file = "guilt_or_innocent.json"
        print(f"Using default case file: {case_file}")
    
    game = BayesianCourtGame(case_file)
    game.start_game()