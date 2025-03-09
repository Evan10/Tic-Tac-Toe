import pygame
from client.gui.element import button
from client.gui.game_screen import (
    connecting_screen,
    disconnected_screen,
    game_screen,
    main_menu_screen,
    match_screen,
    username_screen,
)


class gui_handler:

    def __init__(self, game):
        self.game=game
        self.game_screens: dict[str, game_screen] = self.create_screens(game)
        self.active_screen: game_screen = self.game_screens[
            connecting_screen.SCREEN_NAME
        ]

    def handle_event(self, event: pygame.event.Event):
        self.active_screen.on_event(event)

    def draw(self, canvas: pygame.Surface):
        self.active_screen.draw(canvas)

    def create_screens(self, game):
        return {
            connecting_screen.SCREEN_NAME: connecting_screen(game),
            username_screen.SCREEN_NAME: username_screen(game),
            main_menu_screen.SCREEN_NAME: main_menu_screen(game),
            match_screen.SCREEN_NAME: match_screen(game),
            disconnected_screen.SCREEN_NAME: disconnected_screen(game),
        }

    def switch_screen(self, screen_name):
        self.active_screen: game_screen = self.game_screens.get(
            screen_name, self.game_screens[username_screen.SCREEN_NAME]
        )
        self.active_screen.reset()

    def get_screen(self, screen_name):
        return self.game_screens.get(screen_name, None)
