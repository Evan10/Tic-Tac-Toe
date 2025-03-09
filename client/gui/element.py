


import pygame

from client import consts



class element:

    def __init__(self, rect: pygame.rect.Rect, text_size = 45, layer = 1):
        self.rect:pygame.rect.Rect = rect
        self.fnt = pygame.font.Font(size=text_size)
        self.visible = True
        self.layer = layer #controls render order elements on higher layers are rendered on top
        pass
   
    def draw(self, surface: pygame.Surface):
        pass
    
    def set_visible(self, visible):
        self.visible = visible




class text_element(element):
    TE_COLOR = (255,255,255)
    def __init__(self, rect, text = "", text_size = 45, layer = 1):
        super().__init__(rect, text_size, layer)
        self.text = text
        pass

    def draw(self, surface: pygame.Surface):

        surface.fill(text_element.TE_COLOR, rect = self.rect)
        txt = self.fnt.render(self.text , True, (200,50,50))
        surface.blit(txt, dest = self.rect.move(10 ,self.rect.height/4))

    def set_text(self, text):
        self.text = text


class pop_up_text_element(text_element):
    TE_COLOR = (255,255,255)
    def __init__(self, rect, text = "", text_size = 45, layer = 1):
        super().__init__(rect,text, text_size, layer)
        self.text = text
        self.ticks = 0
        pass

    def draw(self, surface: pygame.Surface):
        if self.ticks <=0:
            self.set_visible(False)
            return
        self.ticks-=1

        surface.fill(text_element.TE_COLOR, rect = self.rect)
        txt = self.fnt.render(self.text , True, (200,50,50))
        surface.blit(txt, dest = self.rect.move(10 ,self.rect.height/4))

    def show(self, seconds = 2):
        self.ticks = consts.FRAME_RATE*seconds
        self.set_visible(True)

    def hide(self):
        self.ticks = 0

    def set_text(self, text):
        self.text = text


class text_stack(element):
    TE_COLOR = (255,255,255)
    def __init__(self, rect, size = 20, layer = 1):
        super().__init__(rect, size, layer)
        self.msgs = []
        self.max_text_messages = 10
        pass

    def draw(self, surface: pygame.Surface):
        surface.fill(text_element.TE_COLOR, rect = self.rect)
        txts = []
        increment = self.rect.height // self.max_text_messages
        for i in range(len(self.msgs)):
            msg = self.msgs[i]
            txts.append((self.fnt.render(msg , True, (50,50,50)), self.rect.move(10 ,increment*i)))
        surface.blits(txts)

    def append_text(self, text):
        self.msgs.append(text)
        self.msgs = self.msgs[max(0,len(self.msgs) - self.max_text_messages):]

    def set_stack(self, msgs: list):
        self.msgs = msgs[max(0,len(msgs) - self.max_text_messages):]

    def pop_text(self):
        return self.msgs.pop()
    
    def reset(self):
        self.msgs.clear()

class interactable_element(element):

    def __init__(self, rect: pygame.rect.Rect, text_size = 45, layer = 1):
        super().__init__(rect, text_size, layer)
        self.has_focus = False
        self.disabled = False
        pass
        
    def set_disabled(self, disabled):
        self.disabled = disabled

    def set_focus(self, focus):
        self.has_focus = focus

    def click_off(self):
        pass

    def mouse_pressed(self):
        pass
    def mouse_released(self):
        pass

    def keyboard_input(self, event: pygame.event.Event) -> bool:
        return False

class input_box(interactable_element):
    TB_COLOR_1 = (255,255,255)
    TB_COLOR_2 = (220,220,220)
    def __init__(self, rect, press_enter_effect, default_text = "...", text_size = 45, layer = 1):
        super().__init__(rect, text_size, layer)
        self.press_enter_effect = press_enter_effect
        self.default_text = default_text
        self.text = ""
        pass

    def draw(self, surface: pygame.Surface):
        surface.fill(input_box.TB_COLOR_2 if self.has_focus else input_box.TB_COLOR_1, rect = self.rect)
        txt = self.fnt.render( self.text if self.text != "" else self.default_text, True, (0,0,0))
        surface.blit(txt, dest = self.rect.move(10 ,self.rect.height/3))

    def click_off(self):
        if self.disabled or not self.visible:
            return
        self.set_focus(False)
        

    def mouse_pressed(self):
        if self.disabled or not self.visible:
            return
        self.set_focus(True)


    def keyboard_input(self, event: pygame.event.Event):
        if event.type != pygame.KEYDOWN or self.disabled or not self.visible:
            return
        if event.dict["key"] == pygame.K_BACKSPACE:
            if len(self.text)>0:
                self.text = self.text[:-1]
        elif event.dict["key"] == pygame.K_RETURN:
            self.press_enter_effect(self.text)
            self.text = ""
        else:
            self.text += event.dict["unicode"] 
        

class button(interactable_element):
    B_COLOR_1 = (255,255,255)
    B_COLOR_2 = (220,220,220)
    B_COLOR_3 = (180,180,180)

    def __init__(self, rect, click_effect, button_text, index = -1, text_size = 45, layer = 1):
        super().__init__(rect, text_size, layer)
        self.click_effect = click_effect
        self.button_text=button_text
        self.is_pressed = False
        self.disabled = False
        self.index = index
        pass
    
    def draw(self, surface: pygame.Surface):
        current_color = button.B_COLOR_3 if self.disabled else button.B_COLOR_2 if self.is_pressed else button.B_COLOR_1
        surface.fill(current_color, rect = self.rect)
        txt = self.fnt.render(self.button_text, True, (0,0,0))
        surface.blit(txt, dest = self.rect.move(10 ,self.rect.height/3))
        
    def change_text(self, button_text):
        self.button_text = button_text

    def mouse_pressed(self):
        if self.disabled or not self.visible:
            return
        self.is_pressed = True

    def mouse_released(self):
        if self.disabled or not self.visible:
            return
        self.is_pressed = False
        self.click_effect(self)


