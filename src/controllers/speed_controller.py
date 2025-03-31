import time
import threading

class SpeedController:
    def __init__(self, text_processor, display_callback):
        self.text_processor = text_processor
        self.display_callback = display_callback
        self.speed = 200
        self.is_running = False
        self.current_position = 0
        self.thread = None

    def set_speed(self, speed):
        self.speed = speed

    def reading_thread(self):
        words = self.text_processor.get_words()
        while self.current_position < len(words) and self.is_running:
            self.display_callback(words[self.current_position])
            time.sleep(self.speed / 1000.0)
            self.current_position += 1
        if self.current_position >= len(words):
            self.current_position = 0
            self.is_running = False

    def start_reading(self):
        self.is_running = True
        self.thread = threading.Thread(target=self.reading_thread)
        self.thread.daemon = True
        self.thread.start()

    def stop_reading(self):
        self.is_running = False
        if self.thread:
            self.thread.join(timeout=0.5)