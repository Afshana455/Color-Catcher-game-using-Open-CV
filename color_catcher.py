import cv2
import numpy as np
import random
import time

class ColorCatcherGame:
    def __init__(self):
      
        self.score = 0
        self.lives = 3
        self.level = 1
        self.falling_objects = []
        self.game_over = False
        self.game_started = False
        
  
        self.width = 1280
        self.height = 720
        
  
        self.lower_color = np.array([0, 120, 70])
        self.upper_color = np.array([10, 255, 255])

        self.lower_color2 = np.array([170, 120, 70])
        self.upper_color2 = np.array([180, 255, 255])
       
        self.colors = [
            (255, 0, 0),    # Blue
            (0, 255, 0),    # Green
            (0, 0, 255),    # Red
            (255, 255, 0),  
            (255, 0, 255), 
            (0, 255, 255),  
        ]
        
      
        self.particles = []
        
  
        self.calibration_mode = True
        
    def create_falling_object(self):
      
        x = random.randint(50, self.width - 50)
        y = -50
        speed = 3 + (self.level * 0.5)
        size = random.randint(30, 60)
        color = random.choice(self.colors)
        obj_type = random.choice(['circle', 'star', 'heart'])
        
        return {
            'x': x,
            'y': y,
            'speed': speed,
            'size': size,
            'color': color,
            'type': obj_type,
            'caught': False
        }
    
    def draw_star(self, img, center, size, color):
      
        pts = []
        for i in range(10):
            angle = i * 36 * np.pi / 180
            r = size if i % 2 == 0 else size // 2
            x = int(center[0] + r * np.sin(angle))
            y = int(center[1] - r * np.cos(angle))
            pts.append([x, y])
        pts = np.array(pts, np.int32)
        cv2.fillPoly(img, [pts], color)
    
    def draw_heart(self, img, center, size, color):
    
        cv2.circle(img, (center[0] - size//4, center[1] - size//4), size//3, color, -1)
        cv2.circle(img, (center[0] + size//4, center[1] - size//4), size//3, color, -1)
        pts = np.array([
            [center[0] - size//2, center[1] - size//6],
            [center[0] + size//2, center[1] - size//6],
            [center[0], center[1] + size//2]
        ], np.int32)
        cv2.fillPoly(img, [pts], color)
    
    def draw_object(self, img, obj):
       
        center = (int(obj['x']), int(obj['y']))
        
        if obj['type'] == 'circle':
            cv2.circle(img, center, obj['size']//2, obj['color'], -1)
            cv2.circle(img, center, obj['size']//2, (255, 255, 255), 2)
        elif obj['type'] == 'star':
            self.draw_star(img, center, obj['size']//2, obj['color'])
        elif obj['type'] == 'heart':
            self.draw_heart(img, center, obj['size']//2, obj['color'])
    
    def create_particles(self, x, y, color):
       
        for _ in range(20):
            angle = random.uniform(0, 2 * np.pi)
            speed = random.uniform(2, 8)
            self.particles.append({
                'x': x,
                'y': y,
                'vx': speed * np.cos(angle),
                'vy': speed * np.sin(angle),
                'color': color,
                'life': 30
            })
    
    def update_particles(self, img):
        for particle in self.particles[:]:
            particle['x'] += particle['vx']
            particle['y'] += particle['vy']
            particle['life'] -= 1
            
            if particle['life'] <= 0:
                self.particles.remove(particle)
            else:
                alpha = particle['life'] / 30
                size = max(1, int(5 * alpha))
                cv2.circle(img, (int(particle['x']), int(particle['y'])), 
                          size, particle['color'], -1)
    
    def detect_colored_object(self, frame):
       
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
       
        mask1 = cv2.inRange(hsv, self.lower_color, self.upper_color)
        mask2 = cv2.inRange(hsv, self.lower_color2, self.upper_color2)
        mask = cv2.bitwise_or(mask1, mask2)
        
        kernel = np.ones((5, 5), np.uint8)
        mask = cv2.erode(mask, kernel, iterations=2)
        mask = cv2.dilate(mask, kernel, iterations=2)
        
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        if contours:
         
            largest_contour = max(contours, key=cv2.contourArea)
            area = cv2.contourArea(largest_contour)
            
            if area > 500:  
                M = cv2.moments(largest_contour)
                if M["m00"] != 0:
                    cx = int(M["m10"] / M["m00"])
                    cy = int(M["m01"] / M["m00"])
                    return cx, cy, mask
        
        return None, None, mask
    
    def check_collision(self, hand_x, hand_y, obj):
   
        distance = np.sqrt((hand_x - obj['x'])**2 + (hand_y - obj['y'])**2)
        return distance < (obj['size'] + 40)
    
    def draw_ui(self, img):
        overlay = img.copy()
        cv2.rectangle(overlay, (0, 0), (self.width, 80), (0, 0, 0), -1)
        cv2.addWeighted(overlay, 0.3, img, 0.7, 0, img)
        
        
        cv2.putText(img, f"SCORE: {self.score}", (20, 50),
                   cv2.FONT_HERSHEY_DUPLEX, 1.2, (0, 255, 255), 3)
        
        for i in range(self.lives):
            cv2.circle(img, (self.width - 50 - i*60, 40), 20, (0, 0, 255), -1)
       
        cv2.putText(img, f"LEVEL: {self.level}", (self.width//2 - 100, 50),
                   cv2.FONT_HERSHEY_DUPLEX, 1.2, (255, 255, 0), 3)
        
        if self.calibration_mode:
       
            cv2.putText(img, "CALIBRATION MODE", (self.width//2 - 200, 150),
                       cv2.FONT_HERSHEY_DUPLEX, 1.2, (0, 255, 255), 3)
            cv2.putText(img, "Hold a RED object (ball, glove, marker)", 
                       (self.width//2 - 350, 220),
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
            cv2.putText(img, "Press SPACE when ready to start", 
                       (self.width//2 - 300, 270),
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
            cv2.putText(img, "Or press 'C' to use different color", 
                       (self.width//2 - 300, 320),
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (200, 200, 200), 2)
        elif not self.game_started:
            text = "Move your object to start!"
            text_size = cv2.getTextSize(text, cv2.FONT_HERSHEY_DUPLEX, 1.5, 3)[0]
            text_x = (self.width - text_size[0]) // 2
            text_y = (self.height + text_size[1]) // 2
            cv2.putText(img, text, (text_x, text_y),
                       cv2.FONT_HERSHEY_DUPLEX, 1.5, (255, 255, 255), 3)
        
        if self.game_over:
            overlay = img.copy()
            cv2.rectangle(overlay, (0, 0), (self.width, self.height), (0, 0, 0), -1)
            cv2.addWeighted(overlay, 0.7, img, 0.3, 0, img)
            
            cv2.putText(img, "GAME OVER!", (self.width//2 - 200, self.height//2 - 50),
                       cv2.FONT_HERSHEY_DUPLEX, 2.5, (0, 0, 255), 5)
            cv2.putText(img, f"Final Score: {self.score}", (self.width//2 - 180, self.height//2 + 50),
                       cv2.FONT_HERSHEY_DUPLEX, 1.5, (255, 255, 255), 3)
            cv2.putText(img, "Press 'R' to restart or 'Q' to quit", 
                       (self.width//2 - 300, self.height//2 + 120),
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
    
    def change_color_preset(self):
     
        presets = [
       
            (np.array([0, 120, 70]), np.array([10, 255, 255]), 
             np.array([170, 120, 70]), np.array([180, 255, 255]), "RED"),
      
            (np.array([100, 150, 0]), np.array([140, 255, 255]),
             np.array([100, 150, 0]), np.array([140, 255, 255]), "BLUE"),
      
            (np.array([40, 40, 40]), np.array([80, 255, 255]),
             np.array([40, 40, 40]), np.array([80, 255, 255]), "GREEN"),
   
            (np.array([20, 100, 100]), np.array([30, 255, 255]),
             np.array([20, 100, 100]), np.array([30, 255, 255]), "YELLOW"),
        ]
        
     
        if not hasattr(self, 'color_index'):
            self.color_index = 0
        
        self.color_index = (self.color_index + 1) % len(presets)
        preset = presets[self.color_index]
        
        self.lower_color = preset[0]
        self.upper_color = preset[1]
        self.lower_color2 = preset[2]
        self.upper_color2 = preset[3]
        
        print(f"Color changed to: {preset[4]}")
    
    def run(self):
     
        cap = cv2.VideoCapture(0)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
        
        last_spawn_time = time.time()
        spawn_interval = 1.5
        
        print("🎮 Color Catcher Game Started!")
        print("📋 Instructions:")
        print("   1. Hold a RED colored object (ball, marker, glove)")
        print("   2. Press SPACE to start game")
        print("   3. Press 'C' to change tracked color")
        print("   4. Move the colored object to catch falling items")
        print("   5. Press 'Q' to quit")
        
        while cap.isOpened():
            success, frame = cap.read()
            if not success:
                break
            
            frame = cv2.flip(frame, 1)
          
            tracker_x, tracker_y, mask = self.detect_colored_object(frame)
            
            if tracker_x is not None:
                if self.calibration_mode:
                
                    cv2.circle(frame, (tracker_x, tracker_y), 40, (0, 255, 0), 3)
                    cv2.circle(frame, (tracker_x, tracker_y), 35, (0, 255, 0), -1)
                    cv2.putText(frame, "Object Detected!", (tracker_x - 70, tracker_y - 50),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                
                elif not self.game_started:
                    self.game_started = True
                
                if self.game_started and not self.game_over and not self.calibration_mode:
            
                    cv2.circle(frame, (tracker_x, tracker_y), 40, (0, 255, 0), 3)
                    cv2.circle(frame, (tracker_x, tracker_y), 35, (0, 255, 0), -1)
            
            if self.game_started and not self.game_over and not self.calibration_mode:
           
                current_time = time.time()
                if current_time - last_spawn_time > spawn_interval:
                    self.falling_objects.append(self.create_falling_object())
                    last_spawn_time = current_time
                
                for obj in self.falling_objects[:]:
                    if not obj['caught']:
                        obj['y'] += obj['speed']
                       
                        if tracker_x and tracker_y and self.check_collision(tracker_x, tracker_y, obj):
                            obj['caught'] = True
                            self.score += 10 * self.level
                            self.create_particles(int(obj['x']), int(obj['y']), obj['color'])
                            self.falling_objects.remove(obj)
                            continue
                        
                        if obj['y'] > self.height + 50:
                            self.lives -= 1
                            self.falling_objects.remove(obj)
                            if self.lives <= 0:
                                self.game_over = True
                            continue
                        
                        self.draw_object(frame, obj)
             
                self.update_particles(frame)
              
                new_level = (self.score // 100) + 1
                if new_level > self.level:
                    self.level = new_level
                    spawn_interval = max(0.5, 1.5 - (self.level * 0.1))
            
            self.draw_ui(frame)
            
            if self.calibration_mode:
                small_mask = cv2.resize(mask, (320, 180))
                small_mask_bgr = cv2.cvtColor(small_mask, cv2.COLOR_GRAY2BGR)
                frame[self.height-190:self.height-10, 10:330] = small_mask_bgr
                cv2.putText(frame, "Detection View", (15, self.height-200),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
            
            cv2.imshow('Color Catcher Game', frame)
            
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord(' ') and self.calibration_mode:
                self.calibration_mode = False
                print("✅ Game started!")
            elif key == ord('c'):
                self.change_color_preset()
            elif key == ord('r') and self.game_over:
            
                self.__init__()
                last_spawn_time = time.time()
        
        cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    game = ColorCatcherGame()
    game.run()