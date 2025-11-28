"""
GUI module for Flip 7 game using tkinter.

This module provides a graphical user interface for the Flip 7 card game.
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from typing import List, Optional
from game import Flip7Game
from player import Player
from cards import Card
from ai import OptimalTurnAI


class Flip7GUI:
    """
    Graphical User Interface for Flip 7 card game.
    
    Provides a complete GUI for playing the Flip 7 game with visual feedback,
    game controls, and real-time game state display.
    """
    
    def __init__(self):
        """Initialize the GUI application."""
        self.root = tk.Tk()
        self.root.title("Flip 7 Card Game")
        self.root.geometry("1000x700")
        self.root.configure(bg='#2c3e50')
        
        # Game instance
        self.game: Optional[Flip7Game] = None
        
        # AI support
        self.ai = OptimalTurnAI()
        self.ai_players = set()        # set of player names that are AI-controlled

        # GUI components
        self.setup_gui()
        
        # Start with game setup
        self.show_game_setup()
    
    def setup_gui(self):
        """Set up the main GUI components."""
        # Main frame
        self.main_frame = ttk.Frame(self.root, padding="10")
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        self.main_frame.columnconfigure(1, weight=1)
        self.main_frame.rowconfigure(2, weight=1)
        
        # Title
        title_label = ttk.Label(
            self.main_frame, 
            text="Flip 7 Card Game", 
            font=('Arial', 20, 'bold')
        )
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # Game info frame
        self.info_frame = ttk.LabelFrame(self.main_frame, text="Game Information", padding="10")
        self.info_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Game area frame
        self.game_frame = ttk.LabelFrame(self.main_frame, text="Game Area", padding="10")
        self.game_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        self.game_frame.columnconfigure(0, weight=1)
        self.game_frame.rowconfigure(1, weight=1)
        
        # Control frame
        self.control_frame = ttk.Frame(self.main_frame)
        self.control_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(10, 0))
        
        # Status frame
        self.status_frame = ttk.LabelFrame(self.main_frame, text="Status", padding="10")
        self.status_frame.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(10, 0))
    
    def show_game_setup(self):
        """Show the game setup dialog."""
        setup_window = tk.Toplevel(self.root)
        setup_window.title("Game Setup")
        setup_window.geometry("400x300")
        setup_window.configure(bg='#2c3e50')
        setup_window.transient(self.root)
        setup_window.grab_set()
        
        # Center the window
        setup_window.geometry("+%d+%d" % (
            self.root.winfo_rootx() + 50,
            self.root.winfo_rooty() + 50
        ))
        
        # Setup frame
        setup_frame = ttk.Frame(setup_window, padding="20")
        setup_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        ttk.Label(setup_frame, text="Setup New Game", font=('Arial', 16, 'bold')).pack(pady=(0, 20))
        
        # Players: name + Human/AI toggle
        ttk.Label(setup_frame, text="Players:").pack(anchor=tk.W, pady=(0, 5))
        
        self.player_entries = []
        self.player_type_vars = []  # True = AI, False = Human
        
        for i in range(3):
            frame = ttk.Frame(setup_frame)
            frame.pack(fill=tk.X, pady=2)
            
            ttk.Label(frame, text=f"Player {i+1}:").pack(side=tk.LEFT, padx=(0, 10))
            
            entry = ttk.Entry(frame, width=20)
            entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
            entry.insert(0, f"Player {i+1}")
            self.player_entries.append(entry)
            
            # Default: Player 1 human, others AI (feel free to change)
            is_ai = tk.BooleanVar(value=(i != 0))
            ai_check = ttk.Checkbutton(frame, text="AI", variable=is_ai)
            ai_check.pack(side=tk.LEFT, padx=(10, 0))
            self.player_type_vars.append(is_ai)

        
        # Target score
        score_frame = ttk.Frame(setup_frame)
        score_frame.pack(fill=tk.X, pady=(20, 10))
        
        ttk.Label(score_frame, text="Target Score:").pack(side=tk.LEFT, padx=(0, 10))
        self.target_score_var = tk.StringVar(value="200")
        score_entry = ttk.Entry(score_frame, textvariable=self.target_score_var, width=10)
        score_entry.pack(side=tk.LEFT)
        
        # Buttons
        button_frame = ttk.Frame(setup_frame)
        button_frame.pack(fill=tk.X, pady=(20, 0))
        
        ttk.Button(button_frame, text="Start Game", command=lambda: self.start_game(setup_window)).pack(side=tk.RIGHT, padx=(10, 0))
        ttk.Button(button_frame, text="Cancel", command=setup_window.destroy).pack(side=tk.RIGHT)
    
    def start_game(self, setup_window):
        """Start a new game with the provided settings."""
        try:
            player_names = [entry.get().strip() for entry in self.player_entries]
            target_score = int(self.target_score_var.get())
            ai_flags = [var.get() for var in self.player_type_vars]
            
            # Validate player names
            if not all(player_names):
                messagebox.showerror("Error", "All player names must be provided!")
                return
            
            if len(set(player_names)) != len(player_names):
                messagebox.showerror("Error", "Player names must be unique!")
                return
            
            # Store which players are AI
            self.ai_players = {
                name for name, is_ai in zip(player_names, ai_flags) if is_ai
            }
            
            # Create game
            self.game = Flip7Game(player_names, target_score)
            setup_window.destroy()
            
            # Initialize game display
            self.initialize_game_display()
            
            # If the first player is an AI, let it start playing
            self.run_ai_turns()
            
        except ValueError:
            messagebox.showerror("Error", "Target score must be a valid number!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to start game: {str(e)}")
    
    def initialize_game_display(self):
        """Initialize the game display after starting a new game."""
        # Clear existing widgets
        for widget in self.info_frame.winfo_children():
            widget.destroy()
        for widget in self.game_frame.winfo_children():
            widget.destroy()
        for widget in self.control_frame.winfo_children():
            widget.destroy()
        for widget in self.status_frame.winfo_children():
            widget.destroy()
        
        # Game info
        self.setup_game_info()
        
        # Game area
        self.setup_game_area()
        
        # Controls
        self.setup_controls()
        
        # Status
        self.setup_status()
        
        # Update display
        self.update_display()
    
    def setup_game_info(self):
        """Set up the game information display."""
        info_text = f"Round: {self.game.round_number} | Target Score: {self.game.target_score} | Cards Remaining: {self.game.deck.cards_remaining()}"
        ttk.Label(self.info_frame, text=info_text, font=('Arial', 12)).pack()
    
    def setup_game_area(self):
        """Set up the main game area."""
        # Players frame
        self.players_frame = ttk.Frame(self.game_frame)
        self.players_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        self.players_frame.columnconfigure((0, 1, 2), weight=1)
        
        # Player displays
        self.player_displays = []
        for i, player in enumerate(self.game.players):
            player_frame = ttk.LabelFrame(self.players_frame, text=player.name, padding="10")
            player_frame.grid(row=0, column=i, padx=5, sticky=(tk.W, tk.E, tk.N, tk.S))
            
            # Player info
            info_text = f"Total Score: {player.total_score}\nRound Score: {player.calculate_round_score()}"
            if player.is_busted:
                info_text += "\nBUSTED!"
            elif player.has_stayed:
                info_text += "\nSTAYED"
            elif player.seven_card_bonus:
                info_text += "\nSEVEN CARD BONUS!"
            
            info_label = ttk.Label(player_frame, text=info_text, font=('Arial', 10))
            info_label.pack()
            
            # Hand display
            hand_frame = ttk.Frame(player_frame)
            hand_frame.pack(fill=tk.X, pady=(10, 0))
            
            hand_label = ttk.Label(hand_frame, text="Hand:", font=('Arial', 9, 'bold'))
            hand_label.pack(anchor=tk.W)
            
            hand_text = tk.Text(hand_frame, height=4, width=15, wrap=tk.WORD, state=tk.DISABLED)
            hand_text.pack(fill=tk.X)
            
            self.player_displays.append({
                'frame': player_frame,
                'info_label': info_label,
                'hand_text': hand_text
            })
        
        # Current player indicator
        self.current_player_label = ttk.Label(self.game_frame, text="", font=('Arial', 14, 'bold'))
        self.current_player_label.grid(row=1, column=0, pady=10)
    
    def setup_controls(self):
        """Set up the game control buttons."""
        # Control buttons
        self.hit_button = ttk.Button(self.control_frame, text="Hit", command=self.hit_card, state=tk.DISABLED)
        self.hit_button.pack(side=tk.LEFT, padx=(0, 10))
        
        self.stay_button = ttk.Button(self.control_frame, text="Stay", command=self.stay_turn, state=tk.DISABLED)
        self.stay_button.pack(side=tk.LEFT, padx=(0, 10))
        
        self.new_round_button = ttk.Button(self.control_frame, text="New Round", command=self.start_new_round, state=tk.DISABLED)
        self.new_round_button.pack(side=tk.LEFT, padx=(0, 10))
        
        self.new_game_button = ttk.Button(self.control_frame, text="New Game", command=self.show_game_setup)
        self.new_game_button.pack(side=tk.RIGHT)
    
    def setup_status(self):
        """Set up the status display."""
        self.status_text = scrolledtext.ScrolledText(self.status_frame, height=6, width=70, wrap=tk.WORD, state=tk.DISABLED)
        self.status_text.pack(fill=tk.BOTH, expand=True)
    
    def update_display(self):
        """Update the entire game display."""
        if not self.game:
            return
        
        # Update game info
        for widget in self.info_frame.winfo_children():
            widget.destroy()
        info_text = f"Round: {self.game.round_number} | Target Score: {self.game.target_score} | Cards Remaining: {self.game.deck.cards_remaining()}"
        ttk.Label(self.info_frame, text=info_text, font=('Arial', 12)).pack()
        
        # Update player displays
        for i, player in enumerate(self.game.players):
            display = self.player_displays[i]

            # Update frame title (mark AI players)
            frame = display['frame']
            title = player.name
            if player.name in self.ai_players:
                title = f"{player.name} (AI)"
            frame.config(text=title)
            
            # Update info
            info_text = f"Total Score: {player.total_score}\nRound Score: {player.calculate_round_score()}"
            if player.is_busted:
                info_text += "\nBUSTED!"
            elif player.has_stayed:
                info_text += "\nSTAYED"
            elif player.seven_card_bonus:
                info_text += "\nSEVEN CARD BONUS!"
            
            display['info_label'].config(text=info_text)
            
            # Update hand display
            hand_text = ", ".join([str(card) for card in player.hand]) if player.hand else "Empty"
            display['hand_text'].config(state=tk.NORMAL)
            display['hand_text'].delete(1.0, tk.END)
            display['hand_text'].insert(1.0, hand_text)
            display['hand_text'].config(state=tk.DISABLED)
        
        # Update current player indicator
        if self.game.round_active:
            current_player = self.game.get_current_player()
            self.current_player_label.config(text=f"Current Turn: {current_player.name}")
        else:
            self.current_player_label.config(text="Round Ended")
        
        # Update button states
        self.update_button_states()
    
    def update_button_states(self):
        """Update the state of control buttons."""
        if not self.game:
            return
        
        current_player = self.game.get_current_player()
        is_ai_turn = current_player.name in self.ai_players
        
        # Hit and Stay buttons
        if (self.game.round_active and 
            not current_player.has_stayed and 
            not current_player.is_busted and
            not is_ai_turn):
            self.hit_button.config(state=tk.NORMAL)
            self.stay_button.config(state=tk.NORMAL)
        else:
            self.hit_button.config(state=tk.DISABLED)
            self.stay_button.config(state=tk.DISABLED)
        
        # New Round button
        if not self.game.round_active and not self.game.is_game_over():
            self.new_round_button.config(state=tk.NORMAL)
        else:
            self.new_round_button.config(state=tk.DISABLED)
    
    def hit_card(self):
        """Handle the hit button click."""
        if not self.game:
            return
        
        success, message = self.game.hit()
        self.add_status_message(message)
        
        if success:
            self.update_display()
            
            # Check if round ended
            if not self.game.round_active:
                self.show_round_results()
                if not self.game.is_game_over():
                    self.add_status_message("Round completed! Starting next round...")
                    self.game.start_new_round()
                    self.update_display()
            
            # Check for game over
            if self.game.is_game_over():
                winner = self.game.get_winner()
                self.add_status_message(f"🎉 GAME OVER! {winner.name} wins with {winner.total_score} points!")
                self.update_button_states()
        # Let AI players act if it's their turn now
        self.run_ai_turns()
    
    def stay_turn(self):
        """Handle the stay button click."""
        if not self.game:
            return
        
        success, message = self.game.stay()
        self.add_status_message(message)
        
        if success:
            self.update_display()
            
            # Check if round ended
            if not self.game.round_active:
                self.show_round_results()
                if not self.game.is_game_over():
                    self.add_status_message("Round completed! Starting next round...")
                    self.game.start_new_round()
                    self.update_display()
            
            # Check for game over
            if self.game.is_game_over():
                winner = self.game.get_winner()
                self.add_status_message(f"🎉 GAME OVER! {winner.name} wins with {winner.total_score} points!")
                self.update_button_states()
        
        # Let AI players act if it's their turn now
        self.run_ai_turns()
    
    def run_ai_turns(self):
        """
        Let AI-controlled players take turns automatically until it's a human's
        turn, the round ends, or the game ends.
        """
        if not self.game:
            return
        
        # Safety cap to avoid infinite loops if something weird happens
        steps = 0
        max_steps = 100
        
        while self.game.round_active and not self.game.is_game_over() and steps < max_steps:
            steps += 1
            current_player = self.game.get_current_player()
            
            # Stop if it's a human's turn
            if current_player.name not in self.ai_players:
                break
            
            # Decide action with the AI
            action = self.ai.choose_action(self.game)
            if action == "hit":
                success, message = self.game.hit()
                action_label = "HIT"
            else:
                success, message = self.game.stay()
                action_label = "STAY"
            
            self.add_status_message(f"{current_player.name} (AI) chooses {action_label}: {message}")
            
            if not success:
                # If something failed, don't keep looping
                break
            
            # Update the display after each AI action
            self.update_display()
            
            # If round ended, follow the same logic as hit/stay handlers
            if not self.game.round_active:
                self.show_round_results()
                if not self.game.is_game_over():
                    self.add_status_message("Round completed! Starting next round...")
                    self.game.start_new_round()
                    self.update_display()
            
            # If game over, announce and stop
            if self.game.is_game_over():
                winner = self.game.get_winner()
                self.add_status_message(
                    f"🎉 GAME OVER! {winner.name} wins with {winner.total_score} points!"
                )
                self.update_button_states()
                break
    
    def show_round_results(self):
        """Show the results of the current round."""
        if not self.game:
            return
        
        self.add_status_message(f"\nRound {self.game.round_number} Results:")
        self.add_status_message("-" * 30)
        
        for player in self.game.players:
            status = ""
            if player.is_busted:
                status = " (BUSTED)"
            elif player.seven_card_bonus:
                status = " (SEVEN CARD BONUS!)"
            
            self.add_status_message(f"{player.name}: {player.round_score} points{status} (Total: {player.total_score})")
    
    def start_new_round(self):
        """Handle the new round button click."""
        if not self.game:
            return
        
        self.game.start_new_round()
        self.add_status_message(f"Starting Round {self.game.round_number}")
        self.update_display()
        self.run_ai_turns()
    
    def add_status_message(self, message: str):
        """Add a message to the status display."""
        self.status_text.config(state=tk.NORMAL)
        self.status_text.insert(tk.END, f"{message}\n")
        self.status_text.see(tk.END)
        self.status_text.config(state=tk.DISABLED)
    
    def run(self):
        """Start the GUI application."""
        self.root.mainloop()


def main():
    """Main function to run the Flip 7 GUI."""
    app = Flip7GUI()
    app.run()


if __name__ == "__main__":
    main()
