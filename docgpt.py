import os
import pickle
import pdfplumber
import pandas as pd
import numpy as np
import openai
from openai.embeddings_utils import get_embedding, cosine_similarity
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QFileDialog, QCheckBox, QTextEdit, QLineEdit, QButtonGroup
from PyQt5.QtWidgets import QHBoxLayout, QScrollArea, QGroupBox, QInputDialog, QLabel, QSizePolicy, QFrame
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt


current_script_path = os.path.realpath(__file__)
current_script_directory = os.path.dirname(current_script_path)

selector_button_ss = ("QPushButton { background-color: royalblue; border-style: outset; color: white; "
               "font-family: Roboto Light; border-radius: 2px; font: 12px; min-width: 3em; "
               "padding: 6px; border-color: beige; }"
               "QPushButton::hover { background-color: rgb(31, 73, 199); }"
               "QPushButton::checked { background-color: rgb(31, 73, 199); border-style: inset; "
               "border: 4px solid transparent; padding: 0px; border-radius: 4px; }")
clear_button_ss = ("QPushButton { background-color: firebrick; border-style: outset; color: white; "
               "font-family: Roboto Light; border-radius: 2px; font: 12px; min-width: 3em; "
               "padding: 6px; border-color: beige; }"
               "QPushButton::hover { background-color: rgb(144, 4, 4); }"
               "QPushButton::checked { background-color: rgb(144, 4, 4); border-style: inset; "
               "border: 4px solid transparent; padding: 0px; border-radius: 4px; }")
highlight_button_ss = ("QPushButton { background-color: rgb(0, 166, 126); border-style: outset; color: white; "
               "font-family: Roboto Light; border-radius: 2px; font: 12px; min-width: 3em; "
               "padding: 6px; border-color: beige; }"
               "QPushButton::hover { background-color: rgb(0, 136, 96); }"
               "QPushButton::checked { background-color: rgb(31, 73, 199); border-style: inset; "
               "border: 4px solid transparent; padding: 0px; border-radius: 4px; }")


# Function to extract text from each page of a PDF and store as a DataFrame
def pdf_to_df(file_path):
    with pdfplumber.open(file_path) as pdf:
        data = [{'page': i+1, 'text': page.extract_text()} for i, page in enumerate(pdf.pages)]
    return pd.DataFrame(data)

# Function to search the most similar pages to a query
def search_pages(df, query, n=2):
    query_embedding = get_embedding(query, engine="text-embedding-ada-002")
    df["similarity"] = df.embedding.apply(lambda x: cosine_similarity(x, query_embedding))
    return df.sort_values("similarity", ascending=False).head(n)

class FileWidget(QWidget):
    def __init__(self, filename, parent):
        super().__init__()
        self.filename = filename
        self.parent = parent

        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        self.check_box = QCheckBox()
        layout.addWidget(self.check_box)

        self.label = QLabel(os.path.basename(filename))  # Change made here
        self.label.setFont(QFont('Roboto Light'))
        self.label.setToolTip(filename)
        layout.addWidget(self.label)

        self.remove_button = QPushButton('X', self)
        self.remove_button.setStyleSheet("QPushButton { background-color: firebrick; border-style: outset; color: white; "
               "font-family: Roboto Light; border-radius: 2px; font: 12px; max-width: 1em; min-width: 1em;"
               "padding: 6px; border-color: beige; }"
               "QPushButton::hover { background-color: rgb(144, 4, 4); }"
               "QPushButton::checked { background-color: rgb(144, 4, 4); border-style: inset; "
               "border: 4px solid transparent; padding: 0px; border-radius: 4px; }")
        self.remove_button.clicked.connect(self.remove)
        layout.addWidget(self.remove_button)

        self.setLayout(layout)

    def remove(self):
        self.parent.remove_file(self)



class DocGPT(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("DocGPT")
        self.file_widgets = []  # replacing self.check_boxes with self.file_widgets
        self.initUI()
        self.check_boxes = QButtonGroup()


    def load_api_key(self):
        current_script_directory = os.path.dirname(os.path.realpath(__file__))
        api_key_path = os.path.join(current_script_directory, 'metadata', 'api_key.txt')
        try:
            with open(api_key_path, 'r') as file:
                api_key = file.read().strip()
            openai.api_key = api_key
        except FileNotFoundError:
            pass

    def configure_api_key(self):
        current_script_directory = os.path.dirname(os.path.realpath(__file__))
        api_key_path = os.path.join(current_script_directory, 'metadata', 'api_key.txt')
        api_key, ok = QInputDialog.getText(self, 'Set OpenAI API Key',
                'Enter your OpenAI API Key:')

        if ok:
            openai.api_key = api_key
            with open(api_key_path, 'w') as file:
                file.write(api_key)

    def initUI(self):
        self.layout = QHBoxLayout()

        metadata_directory = os.path.join(current_script_directory, 'metadata')
        if not os.path.exists(metadata_directory):
            os.makedirs(metadata_directory)

        self.file_panel = QVBoxLayout()

        self.configure_api_key_button = QPushButton('Configure API Key', self)
        self.configure_api_key_button.clicked.connect(self.configure_api_key)
        self.configure_api_key_button.setStyleSheet(highlight_button_ss)
        self.file_panel.addWidget(self.configure_api_key_button)

        self.add_file_button = QPushButton('Add files', self)
        self.add_file_button.clicked.connect(self.add_file)
        self.add_file_button.setStyleSheet(selector_button_ss)
        self.file_panel.addWidget(self.add_file_button)

        self.line = QFrame()
        self.line.setFrameShape(QFrame.VLine)
        self.line.setFrameShadow(QFrame.Sunken)
        self.line.setFixedHeight(1)
        self.line.setStyleSheet("background-color: grey;")
        self.line.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.file_panel.addWidget(self.line)

        self.info_label = QLabel('Select one file to query', self)
        self.info_label.setFont(QFont('Roboto Light'))
        self.file_panel.addWidget(self.info_label)

        self.load_files()
        self.load_api_key()
        
        self.scroll = QScrollArea()
        self.group = QGroupBox()
        self.group.setLayout(self.file_panel)
        self.group.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)  # Add this line
        self.group.setFixedWidth(260)
        self.scroll.setWidget(self.group)
        self.scroll.setFixedWidth(260)
        self.scroll.setWidgetResizable(True)
        self.layout.addWidget(self.scroll)

        self.query_panel = QVBoxLayout()

        self.query_entry = QLineEdit(self)
        self.query_entry.setPlaceholderText("Enter query here...")
        self.query_entry.setMinimumWidth(500)
        self.query_panel.addWidget(self.query_entry)

        self.submit_button = QPushButton('Submit', self)
        self.submit_button.clicked.connect(self.submit_query)
        self.submit_button.setStyleSheet(selector_button_ss)
        self.query_panel.addWidget(self.submit_button)

        self.answer_text = QTextEdit(self)
        self.answer_text.setReadOnly(True)
        self.answer_text.setFontFamily("Roboto Light")
        self.query_panel.addWidget(self.answer_text)

        self.clear_button = QPushButton('Clear', self)
        self.clear_button.clicked.connect(self.clear_answer_text)
        self.clear_button.setStyleSheet(clear_button_ss)
        self.query_panel.addWidget(self.clear_button)
        
        self.layout.addLayout(self.query_panel)

        self.setLayout(self.layout)

    def clear_answer_text(self):
        self.answer_text.clear()

    def load_files(self):
        current_script_directory = os.path.dirname(os.path.realpath(__file__))
        files_path = os.path.join(current_script_directory, 'metadata', 'files.txt')
        try:
            with open(files_path, 'r') as file:
                files = file.read().splitlines()
            
            for filename in files:
                self.add_file_to_list(filename)
        except FileNotFoundError:
            pass

    def add_file(self):
        file_dialog = QFileDialog()
        file_dialog.setNameFilter("PDF files (*.pdf)")

        filenames, _ = file_dialog.getOpenFileNames()

        for filename in filenames:
            if ".pdf" not in filename:
                continue
            else:
                if filename:
                    # Check if the file is already in the list
                    if any(filename == checkbox.toolTip() for checkbox in self.check_boxes.buttons()):
                        # File is already in the list, do not add it again
                        continue

                    self.add_file_to_list(filename)

        self.update_file_list()


    def add_file_to_list(self, filename):
        file_widget = FileWidget(filename, self)
        self.file_panel.addWidget(file_widget)
        self.file_widgets.append(file_widget)

    def remove_file(self, file_widget):
        self.file_widgets.remove(file_widget)
        file_widget.deleteLater()
        self.update_file_list()

    def update_file_list(self):
        current_script_directory = os.path.dirname(os.path.realpath(__file__))
        files_path = os.path.join(current_script_directory, 'metadata', 'files.txt')

        with open(files_path, 'w') as file:
            file.write('\n'.join([widget.filename for widget in self.file_widgets]))

    def submit_query(self):
        current_script_directory = os.path.dirname(os.path.realpath(__file__))
        pkl_directory = os.path.join(current_script_directory, 'pkl')

        # Create the pkl directory if it does not exist
        if not os.path.exists(pkl_directory):
            os.makedirs(pkl_directory)

        query = self.query_entry.text()
        if not query:
            return

        responses = []

        for file_widget in self.file_widgets:
            if file_widget.check_box.isChecked():
                filename = file_widget.label.toolTip()
                basename = os.path.basename(filename)
                pickle_file = os.path.join(pkl_directory, f"{basename}.pkl")

                if os.path.exists(pickle_file):
                    df = pd.read_pickle(pickle_file)
                else:
                    df = pdf_to_df(filename)
                    df["embedding"] = df.text.apply(lambda x: get_embedding(x, engine="text-embedding-ada-002"))
                    df.to_pickle(pickle_file)

                results = search_pages(df, query)
                combined_text = " ".join(results['text'].tolist())

                response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": f"Answer {query} only using information from the document:"},
                        {"role": "user", "content": combined_text},
                    ]
                )

                    
                responses.append(response.choices[0].message['content'])

        try:
            pages = ', '.join(str(row['page']) for _, row in results.iterrows())
        except:
            print("No file selected!")

        try:
            self.answer_text.append(f"<font color='blue'>Query: {query} (File: {basename})</font><br>")
            self.answer_text.append(f"<font color='green'>Answer found on page(s): {pages}</font><br>")
            self.answer_text.append("<br>".join(f"<font color='black'>{response}</font>" for response in responses) + "<br><br>")
        except:
            self.answer_text.append(f"<font color='red'>No file selected!</font><br>")




app = QApplication([])
ex = DocGPT()
ex.show()
app.exec_()
