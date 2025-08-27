#!/usr/bin/env python3
"""Simple command line Cluedo sheet assistant."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

try:
    from tabulate import tabulate
except Exception:  # pragma: no cover - tabulate provides nicer table but not required
    tabulate = None


def get_game_cards(game_type: str):
    """Return suspect, weapon and room lists for a given game type.

    Only the classic board is bundled. Any other request falls back to it."""

    classic = {
        "suspects": [
            "Mustard",
            "Scarlet",
            "White",
            "Green",
            "Peacock",
            "Plum",
        ],
        "weapons": [
            "Candlestick",
            "Dagger",
            "Lead Pipe",
            "Revolver",
            "Rope",
            "Wrench",
        ],
        "rooms": [
            "Kitchen",
            "Ballroom",
            "Conservatory",
            "Dining Room",
            "Billiard Room",
            "Library",
            "Lounge",
            "Hall",
            "Study",
        ],
    }

    return classic["suspects"], classic["weapons"], classic["rooms"]


@dataclass
class CluedoGame:
    players: List[str]
    cards: List[str]
    my_player: str
    sheet: Dict[str, Dict[str, str]] = field(default_factory=dict)

    @classmethod
    def create(cls, players: List[str], suspects: List[str], weapons: List[str], rooms: List[str], my_player: str,
               my_cards: List[str]) -> "CluedoGame":
        cards = suspects + weapons + rooms
        sheet = {card: {p: "" for p in players} for card in cards}
        game = cls(players=players, cards=cards, my_player=my_player, sheet=sheet)
        for card in my_cards:
            game.mark_yes(my_player, card)
        return game

    def mark_yes(self, player: str, card: str) -> None:
        """Mark that a player definitely has a card."""
        self.sheet[card][player] = "Y"
        for p in self.players:
            if p != player and self.sheet[card][p] != "Y":
                self.sheet[card][p] = "N"

    def mark_no(self, player: str, card: str) -> None:
        """Mark that a player does not have a card."""
        if self.sheet[card][player] == "":
            self.sheet[card][player] = "N"

    def update(self, guesser: str, suspect: str, weapon: str, room: str,
               responder: Optional[str] = None, shown_card: Optional[str] = None) -> None:
        """Update sheet based on a guess and its response."""
        cards = [suspect, weapon, room]
        g_idx = self.players.index(guesser)
        if responder:
            r_idx = self.players.index(responder)
            idx = (g_idx + 1) % len(self.players)
            while idx != r_idx:
                p = self.players[idx]
                for c in cards:
                    self.mark_no(p, c)
                idx = (idx + 1) % len(self.players)
            if shown_card:
                self.mark_yes(responder, shown_card)
            else:
                for c in cards:
                    if self.sheet[c][responder] == "":
                        self.sheet[c][responder] = "?"
        else:
            for p in self.players:
                if p != guesser:
                    for c in cards:
                        self.mark_no(p, c)

    def table(self) -> str:
        headers = ["Card"] + self.players
        rows = []
        for card in self.cards:
            rows.append([card] + [self.sheet[card][p] for p in self.players])
        if tabulate:
            return tabulate(rows, headers=headers, tablefmt="grid")
        # Fallback minimal formatting
        col_widths = [max(len(str(cell)) for cell in col) for col in zip(*([headers] + rows))]
        fmt = " | ".join("{:" + str(w) + "}" for w in col_widths)
        lines = [fmt.format(*headers)]
        lines.append("-+-".join("-" * w for w in col_widths))
        for row in rows:
            lines.append(fmt.format(*row))
        return "\n".join(lines)


def setup_interactive() -> CluedoGame:
    num_players = int(input("Number of players: "))
    players = []
    for i in range(num_players):
        players.append(input(f"Initials for player {i + 1}: ").strip())
    my_player = input("Your initials (must match one above): ").strip()
    game_type = input("Game type (classic): ").strip().lower() or "classic"
    suspects, weapons, rooms = get_game_cards(game_type)
    my_cards_in = input("Cards in your hand (comma separated): ")
    my_cards = [c.strip() for c in my_cards_in.split(",") if c.strip()]
    return CluedoGame.create(players, suspects, weapons, rooms, my_player, my_cards)


def interactive_loop(game: CluedoGame) -> None:
    print("\nInitial sheet:")
    print(game.table())
    while True:
        cmd = input("Enter 'turn', 'show' or 'quit': ").strip().lower()
        if cmd == "quit":
            break
        if cmd == "show":
            print(game.table())
            continue
        if cmd == "turn":
            guesser = input("Guesser initials: ").strip()
            suspect = input("Suspect guessed: ").strip()
            weapon = input("Weapon guessed: ").strip()
            room = input("Room guessed: ").strip()
            responder = input("Responder initials (blank if none): ").strip()
            if responder == "":
                responder = None
                shown = None
            else:
                shown = input("Card shown (blank if unknown): ").strip() or None
            game.update(guesser, suspect, weapon, room, responder, shown)
            print(game.table())
            continue
        print("Unknown command.")


def run_demo() -> None:
    suspects, weapons, rooms = get_game_cards("classic")
    players = ["AA", "BB", "CC"]
    game = CluedoGame.create(players, suspects, weapons, rooms, "AA", ["Mustard", "Revolver", "Kitchen"])
    print("Demo: initial sheet with our cards marked")
    print(game.table())
    game.update("BB", "Scarlet", "Dagger", "Hall", responder="AA", shown_card="Scarlet")
    print("\nAfter BB's guess which we answered with Scarlet:")
    print(game.table())


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Simple Cluedo sheet helper")
    parser.add_argument("--demo", action="store_true", help="run a small demonstration")
    args = parser.parse_args()
    if args.demo:
        run_demo()
    else:
        interactive_loop(setup_interactive())
