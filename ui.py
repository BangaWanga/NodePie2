from PyQt5.QtWidgets import QApplication, QLineEdit, QLabel, QVBoxLayout, QPushButton, QMessageBox, QDialog, QGroupBox, QGridLayout
from twitter import TwitterNode


class Twitter(QDialog):
    def __init__(self, parent=None):
        super(Twitter, self).__init__(parent)
        self.param_edits = {
            'consumer_key': QLineEdit(),
            'consumer_secret': QLineEdit(),
            'access_token': QLineEdit(),
            'access_token_secret': QLineEdit()
        }
        self.login_tweepy_screen = None
        self.authenticate_tweepy()

        main_layout = QGridLayout()
        main_layout.addWidget(self.login_tweepy_screen, 3, 0)
        self.setLayout(main_layout)

        self.twitter_node = None

    def authenticate_tweepy(self):
        self.login_tweepy_screen = QGroupBox("Tweepy Connection")
        layout = QVBoxLayout()

        labels = []
        for param in self.param_edits:
            l = QLabel(param)
            layout.addWidget(l)
            labels.append(l)
            layout.addWidget(self.param_edits[param])

        def on_button_clicked():
            alert = QMessageBox()
            params = {
                k: v.text() for k, v in self.param_edits.items()
            }
            self.twitter_node = TwitterNode(params=params)
            if self.twitter_node.is_tweepy_connected():
                self.login_tweepy_screen = QGroupBox("Tweepy Connection")
                alert.setText("Tweepy is connected")
            else:
                alert.setText("Tweepy is connected")
            alert.exec_()

        button = QPushButton('Connect')
        layout.addWidget(button)
        button.clicked.connect(on_button_clicked)
        layout.addWidget(button)
        self.login_tweepy_screen.setLayout(layout)


if __name__=='__main__':
    app = QApplication([])

    gallery = Twitter()
    gallery.show()
    app.exec_()