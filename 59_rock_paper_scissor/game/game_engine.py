import random
import pygame
from game.button import ChoiceButton


class GameEngine:
    def __init__(self, width, height):
        self.width = width
        self.height = height

        self.choices = ["ROCK", "PAPER", "SCISSORS"]

        # Adaptive AI settings
        self.player_history = []
        self.history_limit = 5

        # Match settings
        self.target_score = 3
        self.match_over = False
        self.match_winner = None

        btn_w, btn_h = 130, 50
        gap = 20
        total_w = 3 * btn_w + 2 * gap
        start_x = (width - total_w) // 2
        btn_y = height - 85

        self.buttons = [
            ChoiceButton(
                "ROCK",
                pygame.Rect(start_x, btn_y, btn_w, btn_h),
                (160, 50, 50),
                (200, 70, 70)
            ),
            ChoiceButton(
                "PAPER",
                pygame.Rect(
                    start_x + btn_w + gap,
                    btn_y,
                    btn_w,
                    btn_h
                ),
                (40, 100, 170),
                (60, 130, 210)
            ),
            ChoiceButton(
                "SCISSORS",
                pygame.Rect(
                    start_x + 2 * (btn_w + gap),
                    btn_y,
                    btn_w,
                    btn_h
                ),
                (180, 140, 30),
                (220, 180, 50)
            ),
        ]

        self.player_choice = None
        self.cpu_choice = None

        self.result_text = "Make your move!"
        self.result_color = (220, 225, 235)

        self.player_score = 0
        self.cpu_score = 0

        self.round_resolved_time = 0
        self.display_duration = 1800
        self.showing_result = False

        self.font_title = pygame.font.SysFont(None, 36)
        self.font_hud = pygame.font.SysFont(None, 26)
        self.font_arena = pygame.font.SysFont(None, 32)
        self.font_match = pygame.font.SysFont(None, 42)

    def determine_winner(self, player, cpu):
        if player == cpu:
            return "TIE"

        rules = {
            ("ROCK", "SCISSORS"): "PLAYER",
            ("SCISSORS", "PAPER"): "PLAYER",
            ("PAPER", "ROCK"): "PLAYER",

            ("SCISSORS", "ROCK"): "CPU",
            ("PAPER", "SCISSORS"): "CPU",
            ("ROCK", "PAPER"): "CPU",
        }

        return rules.get((player, cpu), "TIE")

    def get_cpu_choice(self):
        # Not enough history, so choose randomly
        if len(self.player_history) < 3:
            return random.choice(self.choices)

        recent_choices = self.player_history[-self.history_limit:]

        counts = {
            "ROCK": recent_choices.count("ROCK"),
            "PAPER": recent_choices.count("PAPER"),
            "SCISSORS": recent_choices.count("SCISSORS"),
        }

        most_common = max(counts, key=counts.get)

        # Only adapt when there is a clear tendency
        if counts[most_common] < 3:
            return random.choice(self.choices)

        counter_moves = {
            "ROCK": "PAPER",
            "PAPER": "SCISSORS",
            "SCISSORS": "ROCK",
        }

        counter = counter_moves[most_common]

        # 70% chance of choosing the counter,
        # 30% chance of choosing randomly
        if random.random() < 0.7:
            return counter

        return random.choice(self.choices)

    def play_round(self, choice):
        # Do not allow another round after match ends
        if self.match_over:
            return

        self.player_choice = choice

        # Record player's recent choice
        self.player_history.append(choice)

        if len(self.player_history) > self.history_limit:
            self.player_history.pop(0)

        # Adaptive CPU choice
        self.cpu_choice = self.get_cpu_choice()

        outcome = self.determine_winner(
            self.player_choice,
            self.cpu_choice
        )

        if outcome == "PLAYER":
            self.player_score += 1
            self.result_text = (
                f"You Win! {self.player_choice} "
                f"beats {self.cpu_choice}."
            )
            self.result_color = (80, 230, 120)

        elif outcome == "CPU":
            self.cpu_score += 1
            self.result_text = (
                f"You Lose! {self.cpu_choice} "
                f"beats {self.player_choice}."
            )
            self.result_color = (240, 80, 80)

        else:
            self.result_text = (
                f"It's a Draw! Both picked {self.player_choice}."
            )
            self.result_color = (240, 210, 80)

        self.showing_result = True
        self.round_resolved_time = pygame.time.get_ticks()

        # Check whether the match has been won
        if self.player_score >= self.target_score:
            self.match_over = True
            self.match_winner = "PLAYER"

        elif self.cpu_score >= self.target_score:
            self.match_over = True
            self.match_winner = "CPU"

    def restart_match(self):
        self.player_score = 0
        self.cpu_score = 0

        self.player_choice = None
        self.cpu_choice = None

        # Reset adaptive AI history
        self.player_history = []

        self.result_text = "Make your move!"
        self.result_color = (220, 225, 235)

        self.showing_result = False
        self.round_resolved_time = 0

        self.match_over = False
        self.match_winner = None

    def handle_event(self, event):
        # Restart match with R
        if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
            if self.match_over:
                self.restart_match()
            return

        # Ignore mouse input after match ends
        if self.match_over:
            return

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for btn in self.buttons:
                if btn.contains(event.pos):
                    self.play_round(btn.choice_name)
                    break

    def update(self):
        now = pygame.time.get_ticks()

        # Keep final match state visible
        if self.match_over:
            return

        if (
            self.showing_result
            and now - self.round_resolved_time >= self.display_duration
        ):
            self.player_choice = None
            self.cpu_choice = None

            self.result_text = "Make your move!"
            self.result_color = (190, 195, 205)

            self.showing_result = False

    def render(self, screen):
        screen.fill((24, 28, 36))

        title_surf = self.font_title.render(
            "Rock Paper Scissors",
            True,
            (245, 245, 245)
        )

        screen.blit(
            title_surf,
            (
                self.width // 2 - title_surf.get_width() // 2,
                14
            )
        )

        p_surf = self.font_hud.render(
            f"Player Score: {self.player_score}",
            True,
            (100, 180, 255)
        )

        c_surf = self.font_hud.render(
            f"CPU Score: {self.cpu_score}",
            True,
            (255, 120, 120)
        )

        screen.blit(p_surf, (35, 52))

        screen.blit(
            c_surf,
            (
                self.width - c_surf.get_width() - 35,
                52
            )
        )

        target_surf = self.font_hud.render(
            f"First to {self.target_score}",
            True,
            (200, 200, 210)
        )

        screen.blit(
            target_surf,
            (
                self.width // 2 - target_surf.get_width() // 2,
                52
            )
        )

        pygame.draw.line(
            screen,
            (45, 52, 66),
            (25, 82),
            (self.width - 25, 82),
            2
        )

        p_str = self.player_choice if self.player_choice else "--"
        c_str = self.cpu_choice if self.cpu_choice else "--"

        arena_p = self.font_arena.render(
            f"Your Pick:  {p_str}",
            True,
            (225, 225, 230)
        )

        arena_c = self.font_arena.render(
            f"CPU Pick:  {c_str}",
            True,
            (225, 225, 230)
        )

        screen.blit(
            arena_p,
            (
                self.width // 2 - arena_p.get_width() // 2,
                115
            )
        )

        screen.blit(
            arena_c,
            (
                self.width // 2 - arena_c.get_width() // 2,
                155
            )
        )

        res_surf = self.font_arena.render(
            self.result_text,
            True,
            self.result_color
        )

        screen.blit(
            res_surf,
            (
                self.width // 2 - res_surf.get_width() // 2,
                205
            )
        )

        # Display final match winner
        if self.match_over:
            if self.match_winner == "PLAYER":
                winner_text = "MATCH WON! YOU WIN!"
                winner_color = (80, 230, 120)
            else:
                winner_text = "MATCH OVER! CPU WINS!"
                winner_color = (240, 80, 80)

            winner_surf = self.font_match.render(
                winner_text,
                True,
                winner_color
            )

            screen.blit(
                winner_surf,
                (
                    self.width // 2 - winner_surf.get_width() // 2,
                    245
                )
            )

            restart_surf = self.font_hud.render(
                "Press R to restart",
                True,
                (230, 230, 230)
            )

            screen.blit(
                restart_surf,
                (
                    self.width // 2 - restart_surf.get_width() // 2,
                    285
                )
            )

        for btn in self.buttons:
            btn.render(screen)