import sys
import pygame
from settings import Settings
from ship import Ship
from bullet import Bullet
from alien import Alien
from time import sleep
from games_stats import GameStats
from scoreboard import Scoreboard
from button import Button
class AlienInvasion:
    def __init__(self):
        
        pygame.init()
        self.clock=pygame.time.Clock()
        self.settings=Settings()
        self.screen=pygame.display.set_mode((0,0),pygame.FULLSCREEN)
        self.settings.screen_width=self.screen.get_rect().width
        self.settings.screen_height=self.screen.get_rect().height
        pygame.display.set_caption("Alien Invasion")
        
        #create an instace to store game satistics
        self.stats=GameStats(self)
        self.sb=Scoreboard(self)
        
        self.ship = Ship(self)
        self.bullets=pygame.sprite.Group() 
        self.aliens=pygame.sprite.Group()
        self._create_fleet()
        
        #set backgound color
        #self.bg_color=(230,230,230)
        #start alien invasion in an inactive state
        self.game_active=False
        
        #make the play butotn
        self.play_button=Button(self,"Play")
        
        
    def run_game(self):
        while True:
            self._check_events()
            if self.game_active:
                
                self.ship.update()
                self._update_bullets()
                self._update_aliens()
            self._update_screen()
            self.clock.tick(60)
            
    def _update_bullets(self):
        self.bullets.update()
        for bullet in self.bullets.copy():
            if bullet.rect.bottom<=0:
                self.bullets.remove(bullet)
        
        self._check_bullet_alien_collisions()
       
        
        
    def _check_bullet_alien_collisions(self):
        #Respond to bullet-alien collisions
         # Remove any bullets and aliens that have collided. 
        collisions =pygame.sprite.groupcollide(self.bullets,self.aliens,True,True)
        if collisions:
            self.stats.score+=self.settings.alien_points
            self.sb.prep_score()
        
        """if not self.aliens:
            #destroy existing bullets and create new fleet
            self.bullets.empty()
            self.stats.level+=1
            print("Level",self.stats.level)
            self.sb.prep_level()
            
            self.settings.increase_speed()
            self._create_fleet()"""
        if len(self.aliens) == 0:
            print("ALL ALIENS DESTROYED")

            self.bullets.empty()

            self.stats.level += 1
            print("LEVEL:", self.stats.level)

            self.sb.prep_level()

            self.settings.increase_speed()

            self._create_fleet()
            
            
            
            
    def _check_events(self):
        for event in pygame.event.get():
            if event.type==pygame.QUIT:
                sys.exit()
            elif event.type==pygame.KEYDOWN:
                self._check_keydown_events(event)
                
            elif event.type==pygame.KEYUP:
                self._check_keyup_events(event)
                
            elif event.type==pygame.MOUSEBUTTONDOWN:
                mouse_pos=pygame.mouse.get_pos()
                self._check_play_button(mouse_pos)
    
    def _check_play_button(self,mouse_pos):
        button_clicked=self.play_button.rect.collidepoint(mouse_pos)
        if button_clicked and not self.game_active:
            self.settings.initialize_dynamic_settings()
            #reset the game statistics
            self.stats.reset_stats()
            self.sb.prep_score()
            self.sb.prep_level()
            self.sb.prep_ships()
            self.game_active=True
                            
            #get rid of any remaining bullets and aliens
            self.bullets.empty()
            self.aliens.empty()
                            
            #create a new fleet and center the ship
            self._create_fleet()
            self.ship.center_ship()
            
            #hide the mouse cursor
            pygame.mouse.set_visible(False)
            
            
            
                
                
                    
    def _check_keydown_events(self,event):
        if event.key==pygame.K_RIGHT:
            self.ship.moving_right=True
        elif event.key==pygame.K_LEFT:
            self.ship.moving_left=True
        elif event.key==pygame.K_q:
            sys.exit()
        elif event.key==pygame.K_SPACE:
            self._fire_bullet()
    
    
    def _fire_bullet(self):
        if len(self.bullets)<self.settings.bullets_allowed:
            new_bullet=Bullet(self)
            self.bullets.add(new_bullet)
    
    
    def _check_keyup_events(self,event):
        if event.key==pygame.K_RIGHT:
            self.ship.moving_right=False
        elif event.key==pygame.K_LEFT:
            self.ship.moving_left=False
    
    def _create_fleet(self):
        alien=Alien(self)
        alien_width,alien_height=alien.rect.size
        current_x,current_y=alien_width,alien_height
        while current_y<(self.settings.screen_height-3*alien_height):
            while current_x<(self.settings.screen_width-2*alien_width):
                self._create_alien(current_x,current_y)
                current_x+=2*alien_width
            current_x=alien_width
            current_y+=2*alien_height
        #self.aliens.add(alien)
    def _create_alien(self,x_position,y_position):
        
        new_alien=Alien(self)
        new_alien.x=x_position
        new_alien.rect.x=x_position
        new_alien.rect.y=y_position
        self.aliens.add(new_alien)   
        
                 
    def _update_screen(self):
        self.screen.fill(self.settings.bg_color)
        for bullet in self.bullets.sprites():
            bullet.draw_bullet()
        self.ship.blitme()
        self.aliens.draw(self.screen)
        #draw the score information
        self.sb.show_score()
        #draw the play button if the game is inactive
        if not self.game_active:
            self.play_button.draw_button()
            
        
        pygame.display.flip()
    
    
    def _ship_hit(self):
       #respond to ship being hit by alien
       if self.stats.ships_left>1:
           self.stats.ships_left-=1
           self.sb.prep_ships()
           #get rid of any remaining bullets and aliens
           self.bullets.empty()
           self.aliens.empty()
           
                   
            #create a new fleet and center the ship
           self._create_fleet()
           self.ship.center_ship()
           
           sleep(0.5)
       else:
           self.stats.ships_left = 0
           self.sb.prep_ships()
           self.game_active=False
           pygame.mouse.set_visible(True)
         
    
        
    def _update_aliens(self):
        self._check_fleet_edges()
        
        
        self.aliens.update()
        if pygame.sprite.spritecollideany(self.ship,self.aliens):
            #print("Ship hit!!")
            self._ship_hit()
            return
        #look for aliens hitting the bottom of the screen
        self._check_aliens_bottom()
    
    def _check_fleet_edges(self):
        for alien in self.aliens.sprites():
            if alien.check_edges():
                self._change_fleet_direction()
                break
    
    def _change_fleet_direction(self):
        for alien in self.aliens.sprites():
            alien.rect.y+=self.settings.fleet_drop_speed
        self.settings.fleet_direction*=-1
    
    def _check_aliens_bottom(self):
        #check if any aliens have reached the bottom of the screen
        for alien in self.aliens.sprites():
            if alien.rect.bottom>=self.settings.screen_height:
                self._ship_hit()
                break
        
        
if __name__=='__main__':
    ai=AlienInvasion()
    ai.run_game()