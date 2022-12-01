# tyler benson and eva vesely 06/09/2020
import argparse
import sys
import socket
import pickle
import PyQt5.QtWidgets
import PyQt5.QtCore
import PyQt5.QtGui


class MyItem(PyQt5.QtWidgets.QListWidgetItem):

    # Constructor takes additional argument; initializes hidden
    # state. Calls constructor for QListWidgetItem to set up additonal
    # state
    def __init__(self, classid, message, hidden_message):
        self._classid = classid
        self._hidden_message = hidden_message
        super().__init__(message)

    # return the classid of a item
    def classid(self):
        return self._classid

    # Reveal the hidden state.
    def hidden(self):
        return self._hidden_message

# from database import query_database_reg


def parse_args():
    # parse command line arguments
    parser = argparse.ArgumentParser(
        allow_abbrev=False,
        description="Client for the registrar application")
    parser.add_argument(
        "host", type=str,
        help="the host on which the server is running")

    parser.add_argument(
        "port", metavar="port", type=int,
        help="the port at which the server is listening")

    args = parser.parse_args()

    return args.host, args.port


def create_labels():
    label_names = ['Dept', 'Number', 'Area', 'Title']
    labels = [None]*len(label_names)
    for i, label_name in enumerate(label_names):
        labels[i] = PyQt5.QtWidgets.QLabel(f'{label_name}:')
        labels[i].setAlignment(PyQt5.QtCore.Qt.AlignRight |
                               PyQt5.QtCore.Qt.AlignVCenter)
        labels[i].setFont(PyQt5.QtGui.QFont('Arial'))
    return labels


def create_lineedits():
    num_line_edits = 4
    line_edits = [None]*num_line_edits
    for i in range(num_line_edits):
        line_edits[i] = PyQt5.QtWidgets.QLineEdit()
    return line_edits


def create_submit_button():
    return PyQt5.QtWidgets.QPushButton("Submit")


def create_control_frame(labels, line_edits, submit):
    grid_layout = PyQt5.QtWidgets.QGridLayout()
    grid_layout.setSpacing(7)
    grid_layout.setContentsMargins(7, 7, 7, 7)
    grid_layout.setRowStretch(0, 0)
    grid_layout.setRowStretch(1, 0)
    grid_layout.setRowStretch(2, 0)
    grid_layout.setRowStretch(3, 0)
    grid_layout.setColumnStretch(0, 0)
    grid_layout.setColumnStretch(1, 1)
    grid_layout.setColumnStretch(2, 0)
    for i, label in enumerate(labels):
        grid_layout.addWidget(label, i, 0)
    for i, line_edit in enumerate(line_edits):
        grid_layout.addWidget(line_edit, i, 1)
    grid_layout.addWidget(submit, 0, 2, 4, 2)
    control_frame = PyQt5.QtWidgets.QFrame()
    control_frame.setLayout(grid_layout)

    return control_frame


def create_listwidget():
    listwidget = PyQt5.QtWidgets.QListWidget()
    listwidget.setCurrentRow(1)
    return listwidget


def create_data_frame(listwidget):
    data_frame_layout = PyQt5.QtWidgets.QGridLayout()
    data_frame_layout.setContentsMargins(0, 0, 0, 0)
    data_frame_layout.addWidget(listwidget, 0, 0)
    data_frame = PyQt5.QtWidgets.QFrame()
    data_frame.setLayout(data_frame_layout)

    return data_frame


def create_central_frame(data_frame, control_frame):
    central_frame_layout = PyQt5.QtWidgets.QGridLayout()
    central_frame_layout.setSpacing(0)
    central_frame_layout.setContentsMargins(0, 0, 0, 0)
    central_frame_layout.setRowStretch(0, 0)
    central_frame_layout.setRowStretch(1, 2)
    central_frame_layout.setColumnStretch(0, 1)
    central_frame_layout.addWidget(control_frame, 0, 0)
    central_frame_layout.addWidget(data_frame, 1, 0)
    central_frame = PyQt5.QtWidgets.QFrame()
    central_frame.setLayout(central_frame_layout)
    return central_frame


def create_window(central_frame):

    window = PyQt5.QtWidgets.QMainWindow()
    window.setWindowTitle('Princeton University Class Search')
    window.setCentralWidget(central_frame)
    screen_size = PyQt5.QtWidgets.QDesktopWidget().screenGeometry()
    window.resize(screen_size.width()//2, screen_size.height()//2)
    return window


def format_list_data(list_data):
    ret = [None]*len(list_data)
    for i, row in enumerate(list_data):
        ret[i] = (
            row[0], f"{row[0]:>5} "\
                        f"{row[1]:>4} {row[2]:>6} "\
                           f"{row[3]:>4} {row[4]:<59}")
    return ret


def show_user_interface():
    app = PyQt5.QtWidgets.QApplication(sys.argv)

    listwidget = create_listwidget()
    labels = create_labels()
    line_edits = create_lineedits()
    submit = create_submit_button()
    control_frame = create_control_frame(labels, line_edits, submit)
    data_frame = create_data_frame(listwidget)
    central_frame = create_central_frame(data_frame, control_frame)
    window = create_window(central_frame)

    window.show()

    def item_slot(item):
        classid = item.classid()
        try:
            hidden_data = get_data("get_detail", classid)
        except Exception as ex:
            PyQt5.QtWidgets.QMessageBox.information(
                window, "Error", str(ex))
            print(ex, file=sys.stderr)
        hidden_message = format_hidden_message(hidden_data)
        PyQt5.QtWidgets.QMessageBox.information(
            window, "Class Details", hidden_message)

    listwidget.itemActivated.connect(item_slot)
    # if user hits enter or submits button
    def clear_and_update_list():
        listwidget.clear()
        course_data = [line_edits[0].text(), line_edits[1].text(),
                    line_edits[2].text(), line_edits[3].text()]
        try:
            new_data = get_data(
                "get_overviews", generate_args(course_data))
            list_data = format_list_data(new_data)
            for row in list_data:
                listwidget.addItem(MyItem(row[0], row[1], ''))
        except Exception as ex:
            if ex is None:
                ex = "classid does not exist"
            elif type(ex) is type(ConnectionError):
                ex = "A server error occurred. " +\
                    "Please contact the system administrator."
            PyQt5.QtWidgets.QMessageBox.information(
                window, "Error", str(ex))

    # perform for initial populating of app
    clear_and_update_list()

    submit.clicked.connect(clear_and_update_list)

    # when enter is pressed, update the display
    for line_edit in line_edits:
        line_edit.returnPressed.connect(clear_and_update_list)

    sys.exit(app.exec_())


def format_hidden_message(rows):
    ret = ""
    ret += f"Course Id: {rows['courses']['courseid']}\n\nDays: " +\
        f"{rows['courses']['days']}\nStart time: "\
        f"{rows['courses']['start_time']}\nEnd time: " +\
        f"{rows['courses']['end_time']}\nBuilding: "\
        f"{rows['courses']['building']}\nRoom: " +\
        f"{rows['courses']['room']}\n"

    for dept in rows['courses']['depts']:
        ret += f"Dept and Number: {dept}"
    ret += f"\nArea: {rows['courses']['area']}\n\n" +\
        f"Title: {rows['courses']['title']}\n\n" +\
        f"Description: {rows['courses']['descrip']}\n\n" +\
        f"Prerequisites: {rows['courses']['prereq']}\n"
    for prof in rows['profs']:
        ret += f"Professor: {prof}"

    return ret


def format_arg(com):
    return "%" + com.replace('%', '\\%').replace('_', '\\_') + "%"


def generate_args(var):
    args = {"dept": "", "coursenum": "", "area": "", "title": ""}
    for i, key in enumerate(args.keys()):
        args[key] = format_arg(var[i])
    return args


if __name__ == "__main__":
    # parse the command line argument and
    # return the value in a dictionary
    host, port = parse_args()

    def get_data(command, query):
        # query is a dict of variables
        # command is get_overviews, get_detail
        with socket.socket() as sock:
            # connect the socket
            sock.connect((host, port))
            # make a out_flow file to tell the server our query
            out_flo = sock.makefile(mode='wb')
            pickle.dump((command, query), out_flo)
            out_flo.flush()
            print(f"Sent command: {command}")
            # get the data back from the server
            in_flo = sock.makefile(mode='rb')
            status, data = pickle.load(in_flo)
            if not status:
                raise Exception(data)
            return data


    # format and print the data
    show_user_interface()