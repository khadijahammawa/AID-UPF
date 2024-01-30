import sys
import cv2
from PyQt5.QtWidgets import  QWidget, QLabel, QMessageBox
from PyQt5.QtGui import QImage
from PyQt5.QtCore import QTimer, Qt
from PyQt5 import uic, QtWidgets
from PyQt5.QtGui import QImage, QPainter
from PyQt5.QtCore import QTime, QSize

import movenet
from circular_progress_bar import CircularProgressBar

class Ui(QtWidgets.QMainWindow):
    def __init__(self):
        super(Ui, self).__init__() # Call the inherited classes __init__ method

        uic.loadUi('ui/MainWindow.ui', self) # Load the .ui file

        self.progressBar.setValue(0)

        pose_time_required = 3000

        self.labelDown = QLabel("Hand is down")
        self.labelPerp = QLabel("Hand is straightened")
        self.labelUp = QLabel("Hand is up")


        # Set the alignment of the text to be centered
        self.labelDown.setAlignment(Qt.AlignCenter)
        self.labelPerp.setAlignment(Qt.AlignCenter)
        self.labelUp.setAlignment(Qt.AlignCenter)

        self.labelsHorizontalLayout.layout().addWidget(self.labelDown)
        self.labelsHorizontalLayout.layout().addWidget(self.labelPerp)
        self.labelsHorizontalLayout.layout().addWidget(self.labelUp)

        self.circularProgressBarUp = CircularProgressBar(pose_time_required)
        self.circularProgressBarDown = CircularProgressBar(pose_time_required)
        self.circularProgressBarPerp = CircularProgressBar(pose_time_required)

        self.horizontalLayout.layout().addWidget(self.circularProgressBarDown)
        self.horizontalLayout.layout().addWidget(self.circularProgressBarPerp)
        self.horizontalLayout.layout().addWidget(self.circularProgressBarUp)

        # Add CameraWidget to the main window
        self.camera_widget = CameraWidget(
            self.circularProgressBarDown, 
            self.circularProgressBarPerp, 
            self.circularProgressBarUp, 
            self.progressBar,
            pose_time_required,
            )
        
        self.cameraWidget.setLayout(QtWidgets.QVBoxLayout())
        self.cameraWidget.layout().addWidget(self.camera_widget)

         # Connect start and end buttons to the exercise methods
        self.startBtn.clicked.connect(self.startExercise)
        self.endBtn.clicked.connect(self.camera_widget.endExercise)

        self.actionSkeleton_view.triggered.connect(lambda checked: self.camera_widget.setIsSkeletonView(checked))

        self.actionAbout_application.triggered.connect(lambda clicked: self.showAboutApplication())
        self.actionAbout_authors.triggered.connect(lambda clicked: self.showAboutAuthors())
        self.actionExit.triggered.connect(lambda clicked: QtWidgets.QApplication.quit())

    def showAboutApplication(self):
        QMessageBox.information(self, "About Application", 
                                "Application Rehabilitation Feedback Assistant v1.0\n"+
                                "Rehabilitation Feedback Assistant is designed to aid patients in their rehabilitation exercises " +
                                "by providing real-time feedback. The app utilizes advanced pose estimation technology to analyze " + 
                                "and evaluate users' movements during exercises. It offers immediate visual or auditory cues, enabling "+ 
                                "users to make instant corrections. This approach ensures correct exercise execution, potentially leading "+
                                "to faster and more effective rehabilitation. Users can select prescribed exercises and receive "+
                                "instantaneous, actionable feedback as they perform each movement."
                                   )

    def showAboutAuthors(self):
        QMessageBox.information(self, "About Authors", 
                                "Elizaveta Pivovarova, Khadija Hammawa")

    def startExercise(self):
        if not self.listWidget.selectedItems():
            # If no item is selected, show a message dialog
            QMessageBox.information(self, "Exercise Selection", 
                                    "Please select an exercise.")
            return
        
        selectedItem = self.listWidget.currentItem()

        if selectedItem.text() == "Left hand":
            # If the selected item is "Left hand", start the exercise
            QMessageBox.information(self, "Left Hand Exercise",
                                    "Exercise 'Left Hand':\n"
                                    "1. First, position your left hand down.\n"
                                    "2. Next, straighten your left hand.\n"
                                    "3. Finally, raise your left hand up.\n\n"
                                    "Observe your progress on the indicators. To end the exercise early, click 'End Exercise'.")
            self.camera_widget.initLeftHandExercise()
            self.camera_widget.startExercise()

        if selectedItem.text() == "Right hand":
            # If the selected item is "Left hand", start the exercise
            QMessageBox.information(self, "Right Hand Exercise",
                                    "Exercise 'Right Hand':\n"
                                    "1. First, position your right hand down.\n"
                                    "2. Next, straighten your right hand.\n"
                                    "3. Finally, raise your right hand up.\n\n"
                                    "Observe your progress on the indicators. To end the exercise early, click 'End Exercise'.")
            self.camera_widget.initRightHandExercise()
            self.camera_widget.startExercise()

class CameraWidget(QWidget):
    def __init__(self, dialDown, dialPerp, dialUp, progressBar, pose_time_required):
        super().__init__()

        self.initUI()

        self.is_skeleton_viewable = False

        self.pose_time_required = pose_time_required  # 3 seconds in milliseconds

        # dials, progress bars
        self.dialDown = dialDown
        self.dialPerp = dialPerp
        self.dialUp = dialUp
        self.progressBar = progressBar

        # Initialize camera
        self.cap = cv2.VideoCapture(0)

        # Create a timer for updating the feed
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.updateFrame)
        self.timer.start(20)

        self.image = None
        self.is_exercising = False

        self.is_left = None
    
    def setIsSkeletonView(self, is_skeleton_viewable):
        self.is_skeleton_viewable = is_skeleton_viewable

    def initUI(self):
        self.resize(640, 480)

    def initLeftHandExercise(self):
        self.is_left = True

        self.pose_sequence = [movenet.POSE_DOWN, movenet.POSE_PERP, movenet.POSE_UP]
        self.current_pose_index = 0
        self.pose_timer = QTime()
    
    def initRightHandExercise(self):
        self.is_left = False

        self.pose_sequence = [movenet.POSE_DOWN, movenet.POSE_PERP, movenet.POSE_UP]
        self.current_pose_index = 0
        self.pose_timer = QTime()

    def updateUI(self, elapsed_time):
        # Update progress bar
        # 33% - 100% - 3000ms
        # 3000s - 33
        # 90s - 1
        if self.current_pose_index == 0:
            progress = int (elapsed_time/90)
        if self.current_pose_index == 1:
            progress = int(33 + (elapsed_time/90))
        if self.current_pose_index == 2:
            progress = int(66 + (elapsed_time/90))

        self.progressBar.setValue(min(progress, 100))

    def startExercise(self):
        self.is_exercising = True
        self.current_pose_index = 0
        self.pose_timer.start()
        self.progressBar.setValue(0)

    def endExercise(self):
        self.progressBar.setValue(0)
        self.resetDials()
        self.is_exercising = False

    def checkPose(self, processed_image):
        current_pose = self.pose_sequence[self.current_pose_index]

        if processed_image.is_pose(current_pose):
            elapsed_time = self.pose_timer.elapsed()

            self.updateDial(current_pose, elapsed_time)
            self.updateUI(elapsed_time)

            if elapsed_time >= self.pose_time_required:
                self.current_pose_index += 1

                if self.current_pose_index < len(self.pose_sequence):
                    self.pose_timer.restart()  # Restart timer for the next pose
                else:
                    self.endExercise()  # End exercise if all poses are done
                    self.showSuccess()
        else:
            # Reset the dials if the pose is not correct
            # self.resetDials()
            self.pose_timer.restart()

    def updateDial(self, pose, value):
        # print(f"pose {pose}, elapsed_time {value}")
        if pose == movenet.POSE_DOWN:
            self.dialDown.setValue(value)
        elif pose == movenet.POSE_PERP:
            self.dialPerp.setValue(value)
        elif pose == movenet.POSE_UP:
            self.dialUp.setValue(value)

    def resetDials(self):
        self.dialDown.setValue(0)
        self.dialPerp.setValue(0)
        self.dialUp.setValue(0)


    def updateFrame(self):
        ret, frame = self.cap.read()
        if ret:
            frame = cv2.flip(frame, 1)
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            if self.is_exercising:
                processed_image = movenet.process_image(frame.copy(), self.is_left)
                self.checkPose(processed_image)

                if self.is_skeleton_viewable:
                    frame = processed_image.img

            self.image = QImage(frame.data, frame.shape[1], frame.shape[0], frame.strides[0], QImage.Format_RGB888)
            self.update()  # Trigger paint event

    def paintEvent(self, event):
        if self.image:
            painter = QPainter(self)
            painter.drawImage(0, 0, self.image.scaled(self.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))

    def closeEvent(self, event):
        self.cap.release()

    def showSuccess(self):
        QMessageBox.information(self, "Well done!", 
                                "You have successfully finished the exercise.")

app = QtWidgets.QApplication(sys.argv) # Create an instance of QtWidgets.QApplication
window = Ui() # Create an instance of our class
window.show()
app.exec_() # Start the application