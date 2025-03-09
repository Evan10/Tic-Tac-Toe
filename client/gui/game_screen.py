import pygame

from client.gui.element import (
    button,
    element,
    input_box,
    interactable_element,
    pop_up_text_element,
    text_element,
    text_stack,
)
from client.gui.tic_tac_toe_board import match_board
from client import consts
from client.gui import screen_rect_locations as srl
from common.tic_tac_toe_game import X


class game_screen:

    SCREEN_NAME = "default"

    def __init__(self, game):
        self.game = game
        self.renderable_elements: list[element] = []
        self.interactable_elements: list[interactable_element] = []
        self.element_with_focus: interactable_element = None
        pass

    def draw(self, canvas: pygame.Surface):
        for ele in self.renderable_elements:
            if ele.visible:
                ele.draw(canvas)

    def order_renderable_elements(self):
        self.renderable_elements.sort(key=lambda ele: ele.layer)

    def create_button(
        self, rect, button_effect, button_text="", index=-1, text_size=45, layer=1
    ):
        btn = button(rect, button_effect, button_text, index, text_size, layer)
        self.interactable_elements.append(btn)
        self.renderable_elements.append(btn)
        self.order_renderable_elements()
        return btn

    def create_input_box(
        self, rect, press_enter_effect, default_text="...", text_size=45, layer=1
    ):
        inpt_bx = input_box(rect, press_enter_effect, default_text, text_size, layer)
        self.interactable_elements.append(inpt_bx)
        self.renderable_elements.append(inpt_bx)
        self.order_renderable_elements()
        return inpt_bx

    def create_text_element(self, rect, text="", text_size=45, layer=1):
        txt_ele = text_element(rect, text, text_size, layer)
        self.renderable_elements.append(txt_ele)
        self.order_renderable_elements()
        return txt_ele

    def create_pop_up_element(self, rect, text="", text_size=45, layer=1):
        pop_up = pop_up_text_element(rect, text, text_size, layer)
        self.renderable_elements.append(pop_up)
        self.order_renderable_elements()
        return pop_up

    def create_text_stack(self, rect, text_size=20, layer=1):
        txt_ele = text_stack(rect, text_size, layer)
        self.renderable_elements.append(txt_ele)
        self.order_renderable_elements()
        return txt_ele

    def on_event(self, event: pygame.event.Event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.element_with_focus = None
            for ele in self.interactable_elements:
                x, y = event.dict["pos"]
                if ele.rect.collidepoint(x, y):
                    ele.mouse_pressed()
                    self.element_with_focus = ele
                else:
                    ele.click_off()
        if event.type == pygame.MOUSEBUTTONUP:
            x, y = event.dict["pos"]
            for ele in self.interactable_elements:
                if ele.rect.collidepoint(x, y):
                    ele.mouse_released()
        elif event.type == pygame.KEYDOWN:
            if self.element_with_focus is not None:
                self.element_with_focus.keyboard_input(event)

    def reset(self):
        pass


class username_screen(game_screen):
    SCREEN_NAME = "username_screen"

    def __init__(self, game):
        super().__init__(game)
        self.fnt = pygame.font.Font(size=100)

        def ss_enter_effect(name):
            game.send_client_info(name)

        self.create_input_box(srl.CENTER_RECT, ss_enter_effect, "Enter Username")

        pass

    def draw(self, canvas: pygame.Surface):
        canvas.fill(color=(255, 0, 0))
        super().draw(canvas)


class main_menu_screen(game_screen):
    SCREEN_NAME = "main_menu_screen"

    JOIN_QUEUE_TEXT = "Join Queue"
    LEAVE_QUEUE_TEXT = "Leave Queue"
    TITLE = "Tic Tac Toe"

    def __init__(self, game):
        super().__init__(game)
        self.Title = self.create_text_element(srl.TOP_LEFT_RECT, main_menu_screen.TITLE)

        def queue_bttn_effect(btn: button):
            if btn.button_text == main_menu_screen.JOIN_QUEUE_TEXT:
                game.join_game_queue()
                btn.change_text(main_menu_screen.LEAVE_QUEUE_TEXT)
            elif btn.button_text == main_menu_screen.LEAVE_QUEUE_TEXT:
                game.leave_game_queue()
                btn.change_text(main_menu_screen.JOIN_QUEUE_TEXT)

        self.queue_button = self.create_button(
            srl.CENTER_RECT,
            queue_bttn_effect,
            button_text=main_menu_screen.JOIN_QUEUE_TEXT,
        )
        pass

    def draw(self, canvas: pygame.Surface):
        canvas.fill(color=(0, 0, 255))
        super().draw(canvas)

    def reset_queue_button(self):
        self.queue_button.change_text(main_menu_screen.JOIN_QUEUE_TEXT)

    def reset(self):
        self.reset_queue_button()


class connecting_screen(game_screen):
    SCREEN_NAME = "connecting_screen"

    def __init__(self, game):
        super().__init__(game)

        self._connecting_text = "Connecting"
        self.frame = 0
        self._animation_characters = "..."

        self.txt_ele = self.create_text_element(srl.CENTER_RECT, self._connecting_text)
        pass

    def draw(self, canvas: pygame.Surface):
        canvas.fill(color=(0, 0, 255))

        self.frame = self.frame + 1 if self.frame < 200 else 0

        self.txt_ele.set_text(
            self._connecting_text + self._animation_characters[: self.frame // 50]
        )

        super().draw(canvas)


class match_screen(game_screen):
    SCREEN_NAME = "match_screen"

    def __init__(self, game):
        super().__init__(game)
        self._current_match = None

        self.tic_tac_toe_board: match_board = match_board(self)

        self.game_over_message: text_element = self.create_text_element(
            srl.TOP_MIDDLE_RECT.inflate(-20, -20), text_size=35, layer=5
        )
        self.game_over_message.set_visible(False)

        def to_mm_button_effect(btn):
            game.switch_current_screen(main_menu_screen.SCREEN_NAME)

        self.back_to_main_menu_screen_button: button = self.create_button(
            srl.CENTER_RECT.inflate(-30, -30),
            to_mm_button_effect,
            button_text="Main Menu",
            layer=5,
        )

        self.pop_up_message: pop_up_text_element = self.create_pop_up_element(
            srl.CENTER_RECT.inflate(-30, -30), layer=3
        )

        self.back_to_main_menu_screen_button.set_visible(False)

        self.game_info_box: text_stack = self.create_text_stack(
            srl.BOTTOM_MIDDLE_RECT.inflate(-20, -20)
        )

        self.chat_element: text_stack = self.create_text_stack(
            srl.TOP_RIGHT_RECT.union(srl.MIDDLE_RIGHT_RECT)
        )
        self.move_log: text_stack = self.create_text_stack(srl.BOTTOM_LEFT_RECT)

        def chat_input_enter_effect(message):
            self._current_match.player_chat_message(message)
            self.update_chat_element()

        self.chat_input: input_box = self.create_input_box(
            srl.BOTTOM_RIGHT_RECT,
            chat_input_enter_effect,
            "send chat message...",
            text_size=30,
        )
        pass

    def set_current_match(self, match):
        self._current_match = match
        self.tic_tac_toe_board.set_TTT_game(match)
        self.tic_tac_toe_board.setup_interactables(self)
        self.reset()
        self.set_game_info_box()

        starter_msg = (
            "You start!" if match.player.team == X else f"{match.opponent.name} Starts!"
        )
        self.pop_up_message.set_text(starter_msg)
        self.pop_up_message.show(2)

    def set_game_info_box(self):
        game_info_lines = []
        game_info_lines.append(f"You:")
        game_info_lines.append(f"   Name: {self._current_match.player.name}")
        game_info_lines.append(f"   Team: {self._current_match.player.team}")
        game_info_lines.append("")
        game_info_lines.append(f"Opponent:")
        game_info_lines.append(f"   Name: {self._current_match.opponent.name}")
        game_info_lines.append(f"   Team: {self._current_match.opponent.team}")
        self.game_info_box.set_stack(game_info_lines)

    def draw(self, canvas: pygame.Surface):
        canvas.fill(color=(255, 0, 0))
        super().draw(canvas)

    def reset(self):
        self.tic_tac_toe_board.reset_buttons()
        self.game_over_message.set_visible(False)
        self.back_to_main_menu_screen_button.set_visible(False)
        self.chat_element.reset()
        self.move_log.reset()

    def trigger_game_over_message(self, message):
        self.game_over_message.set_text(message)
        self.game_over_message.set_visible(True)
        self.back_to_main_menu_screen_button.set_visible(True)
        self.pop_up_message.hide()

    def update_move_log(self):
        evnt_stck = self._current_match.TTT_game.event_stack
        evnt_stck = [str(evnt) for evnt in evnt_stck]
        self.move_log.set_stack(evnt_stck)

    def update_chat_element(self):
        self.chat_element.set_stack(self._current_match.chat_log)


class disconnected_screen(game_screen):

    def __init__(self, game):
        super().__init__(game)
        self._reason = "Unknown reason"
        cstm_rect = srl.BOTTOM_LEFT_RECT.copy()
        cstm_rect.width = consts.WINDOW_DIMENSIONS["width"]
        self.txt_ele = self.create_text_element(
            cstm_rect,
            self._reason,
        )
        self.create_text_element(
            srl.CENTER_RECT,
            "Reason:",
        )
        self.create_text_element(
            srl.TOP_MIDDLE_RECT,
            "Disconnected",
        )

    def set_reason(self, reason):
        self._reason = reason
        self.txt_ele.set_text(self._reason)

    def draw(self, canvas: pygame.Surface):
        canvas.fill(color=(255, 0, 0))

        super().draw(canvas)
