# DocGPT

DocGPT is an interactive GUI application that allows users to upload PDF files and ask GPT-3.5 questions about the content of those files.

## Getting Started

### Prerequisites

Before running this script, please ensure you have the following python packages installed:

- os
- pickle
- pdfplumber
- pandas
- numpy
- openai
- PyQt5

You can install these packages using pip:
```shell
pip install pdfplumber pandas numpy openai PyQt5

### Installation
No specific installation is required for this application. Simply download and save the python file in your desired directory. Make sure you also have your OpenAI API Key to hand, as you'll need to configure this in the GUI.

## Usage
To start the application, run the python script from your terminal:
```shell
python your_script_name.py

Once the GUI has started, you can:

- Configure your OpenAI API Key: You'll need to input your OpenAI API Key here before you can use the GPT-3.5 model. Click the 'Configure API Key' button to do this.

- Add PDF Files: Click the 'Add files' button to select the PDF files you want to ask questions about. You can select multiple files.

- Ask Questions: Enter your question in the provided field and click the 'Submit' button. The GPT-3.5 model will then analyze your files, find the most relevant parts to your question, and generate an answer. You can view this answer in the response box.

- Clear Response: If you want to clear the response box, click the 'Clear' button.

- Remove Files: You can remove a file from your selection by clicking the 'X' button next to the file name.

Please note that all the files you add will be saved to a list, so when you restart the application, your previous files will still be there. You can remove these files if you no longer need them.

The response from GPT-3.5 will be based on the content of your uploaded files. If the answer to your question isn't found in the files, GPT-3.5 may not be able to provide a suitable answer.

## Troubleshooting

If you encounter issues, check the following:

Ensure that the API key is correctly configured.
Confirm that the PDF files are valid and not corrupt.
Verify that all prerequisites are correctly installed and up to date.

## Disclaimer

Disclaimer
This application uses OpenAI's GPT-3.5 model, which requires an API key that comes with associated costs. Use this application responsibly to manage your API usage.
