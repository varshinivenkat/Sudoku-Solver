import pygame
import constants as c

#============================DEFINING A BUTTON AND ROUNDED RECTANGLE=================================#

class Button:
    def __init__(self, x, y, width, height, text):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.font = pygame.font.Font(None, 36)
        
    def draw(self, surface):
        draw_rounded_rect(surface, c.DARK_PASTEL_BLUE, self.rect, 10)
        text_surface = self.font.render(self.text, True, c.WHITE)
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)

def draw_rounded_rect(surface, color, rect, radius):
    x, y, width, height = rect
    pygame.draw.rect(surface, color, (x + radius, y + radius, width - 2*radius, height - 2*radius))
    pygame.draw.rect(surface, color, (x + radius, y, width - 2*radius, radius)) 
    pygame.draw.rect(surface, color, (x + radius, y + height - radius, width - 2*radius, radius))  
    pygame.draw.rect(surface, color, (x, y + radius, radius, height - 2*radius))  
    pygame.draw.rect(surface, color, (x + width - radius, y + radius, radius, height - 2*radius))  
    pygame.gfxdraw.filled_circle(surface, x + radius, y + radius, radius, color) 
    pygame.gfxdraw.filled_circle(surface, x + width - radius - 1, y + radius, radius, color)
    pygame.gfxdraw.filled_circle(surface, x + radius, y + height - radius - 1, radius, color)  
    pygame.gfxdraw.filled_circle(surface, x + width - radius - 1, y + height - radius - 1, radius, color)
