import sys
import cv2
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QPushButton
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import QTimer, Qt
from deepface import DeepFace


class EmotionGame(QWidget):
    def __init__(self):
        super().__init__()
        
        # Define some emotions and their corresponding winning conditions
        self.emotions = ['happy', 'sad', 'angry', 'neutral']
        self.target_emotion = self.emotions[0]  # Start with happy as the target emotion
        
        self.rounds = 4
        self.current_round = 1
        self.score = 0
        
        self.initUI()
        self.initCamera()
    
    def initUI(self):
        layout = QVBoxLayout()
        
        self.label = QLabel("Welcome to the Emotion Game!")
        layout.addWidget(self.label)
        
        self.current_emotion_label = QLabel(f"Current Target Emotion: {self.target_emotion}")
        layout.addWidget(self.current_emotion_label)
        
        self.round_label = QLabel(f"Round: {self.current_round}/{self.rounds}")
        layout.addWidget(self.round_label)
        
        self.result_label = QLabel("")
        layout.addWidget(self.result_label)
        
        self.score_label = QLabel(f"Score: {self.score}")
        layout.addWidget(self.score_label)
        
        self.setLayout(layout)
        self.setWindowTitle('Emotion Game')
        self.show()
    
    def initCamera(self):
        self.cap = cv2.VideoCapture(0)
        
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(10)  # Update frame every 10 ms
        
        self.round_timer = QTimer()
        self.round_timer.setSingleShot(True)
        self.round_timer.timeout.connect(self.end_round)
        
        self.start_new_round()
    
    def start_new_round(self):
        if self.current_round > self.rounds:
            self.end_game()
            return
        
        self.target_emotion = self.emotions[(self.current_round - 1) % len(self.emotions)]
        self.current_emotion_label.setText(f"Current Target Emotion: {self.target_emotion}")
        self.round_label.setText(f"Round: {self.current_round}/{self.rounds}")
        self.result_label.setText("Show the emotion in 2 seconds!")
        self.round_timer.start(2000)  # Start a 2-second timer
    
    def end_round(self):
        if self.current_round <= self.rounds:
            self.result_label.setText("")
            self.check_emotion()
            self.current_round += 1
            self.start_new_round()
        else:
            self.end_game()
    
    def check_emotion(self):
        ret, frame = self.cap.read()
        if ret:
            try:
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                
                result = DeepFace.analyze(rgb_frame, actions=['emotion'], enforce_detection=False)
                
                if isinstance(result, list) and len(result) > 0:
                    result = result[0]
                
                if result and 'dominant_emotion' in result:
                    detected_emotion = result['dominant_emotion']
                    
                    if detected_emotion == self.target_emotion:
                        self.result_label.setText("Congratulations! You've matched the target emotion!")
                        self.score += 1
                    else:
                        self.result_label.setText(f"Try again! The target emotion was {self.target_emotion}.")
                
                self.score_label.setText(f"Score: {self.score}")
            except Exception as e:
                print(f"Error analyzing frame: {e}")

    def update_frame(self):
        ret, frame = self.cap.read()
        if ret:
            image = QImage(frame.data, frame.shape[1], frame.shape[0], QImage.Format_RGB888).rgbSwapped()
            self.label.setPixmap(QPixmap.fromImage(image))
    
    def end_game(self):
        self.result_label.setText(f"Game Over! Your final score is {self.score}/{self.rounds}")
        self.round_label.setText(f"Round: {self.current_round-1}/{self.rounds}")  # Adjusted to show correct round count
        self.round_timer.stop()
        self.timer.stop()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = EmotionGame()
    sys.exit(app.exec_())