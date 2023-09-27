import sys
import requests
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget, QComboBox, QScrollArea, QGroupBox
from PyQt5.QtCore import QTimer, QDateTime, Qt
from PyQt5.QtGui import QFont

class QueueTimeApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setGeometry(100, 100, 480, 320)

        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout()
        
        self.land_combo = QComboBox()
        layout.addWidget(self.land_combo)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True) 
        layout.addWidget(self.scroll_area)

        self.ride_group_box = QGroupBox("Ride Information")
        self.ride_group_box.setFont(QFont("Arial", 15))

        self.ride_layout = QVBoxLayout()

        self.ride_group_box.setLayout(self.ride_layout)

        self.scroll_area.setWidget(self.ride_group_box)

        bottom_layout = QVBoxLayout()

        self.clock_label = QLabel()
        bottom_layout.addWidget(self.clock_label, alignment=Qt.AlignRight)
        self.clock_label.setFont(QFont("Arial", 15)) 

        self.last_updated_label = QLabel()
        bottom_layout.addWidget(self.last_updated_label, alignment=Qt.AlignRight) 

        layout.addLayout(bottom_layout)

        central_widget.setLayout(layout)

        self.json_data = self.fetch_json_data()

        if self.json_data and 'lands' in self.json_data:
            lands = self.json_data['lands']
            for land in lands:
                self.land_combo.addItem(land['name'])

        self.land_combo.currentIndexChanged.connect(self.show_selected_ride)

        self.land_index = 0
        self.cycle_timer = QTimer(self)
        self.cycle_timer.timeout.connect(self.cycle_land)
        self.cycle_timer.start(30000)

        self.clock_timer = QTimer(self)
        self.clock_timer.timeout.connect(self.update_clock)
        self.clock_timer.start(1000)

        self.show_last_updated()

        self.show_selected_ride()

    def fetch_json_data(self):
        url = "https://queue-times.com/parks/16/queue_times.json"
        try:
            response = requests.get(url)
            response.raise_for_status()
            json_data = response.json()
            return json_data
        except Exception as e:
            print(f"Error fetching JSON data: {str(e)}")
            return None

    def show_selected_ride(self):
        selected_land_index = self.land_combo.currentIndex()

        for i in reversed(range(self.ride_layout.count())):
            widget = self.ride_layout.itemAt(i).widget()
            if widget is not None:
                widget.deleteLater()

        if self.json_data and 'lands' in self.json_data:
            lands = self.json_data['lands']
            if 0 <= selected_land_index < len(lands):
                selected_land = lands[selected_land_index]
                rides = selected_land.get('rides', [])
                if rides:
                    for ride in rides:
                        ride_info_label = QLabel()
                        ride_info_label.setWordWrap(True)
                        ride_info_label.setTextFormat(Qt.RichText)
                        
                        ride_info_label.setText(
                            f"<b>{ride['name']}:</b> {ride['wait_time']} minutes (Open)"
                            if ride['is_open']
                            else f"<b>{ride['name']}:</b> Closed"
                        )
                        self.ride_layout.addWidget(ride_info_label)
                else:
                    no_ride_label = QLabel("No rides available in this land.")
                    self.ride_layout.addWidget(no_ride_label)
            else:
                no_land_label = QLabel("Select a land from the dropdown.")
                self.ride_layout.addWidget(no_land_label)
        else:
            fetch_error_label = QLabel("Failed to fetch JSON data.")
            self.ride_layout.addWidget(fetch_error_label)

    def show_last_updated(self):
        if self.json_data and 'lands' in self.json_data:
            last_updated = self.json_data['lands'][0]['rides'][0]['last_updated']
            
            pst_time = self.convert_utc_to_pst(last_updated)
            
            self.last_updated_label.setText(f"Last Updated: {pst_time}---Powered by Queue-Times.com")

    def cycle_land(self):
        self.land_index += 1
        if self.land_index >= self.land_combo.count():
            self.land_index = 0

        self.land_combo.setCurrentIndex(self.land_index)
        self.show_selected_ride()

    def update_clock(self):
        current_time = QDateTime.currentDateTime()
        
        formatted_time = current_time.toString("hh:mm:ss AP")
        self.clock_label.setText(f"Current Time: {formatted_time}")

    def convert_utc_to_pst(self, utc_time):
        utc_datetime = QDateTime.fromString(utc_time, "yyyy-MM-ddTHH:mm:ss.zzzZ")
        pst_datetime = utc_datetime.addSecs(-7 * 3600)
        return pst_datetime.toString("yyyy-MM-dd hh:mm:ss AP")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = QueueTimeApp()
    window.show()
    sys.exit(app.exec_())
