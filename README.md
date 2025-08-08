
---

````markdown
#  PDF Merger Tool

A simple web-based PDF merging tool built with **Python Flask** for the backend and **HTML/CSS/JavaScript** for the frontend. Upload multiple PDF files and get a single merged document in seconds — all within your browser.

##  Features

- Merge multiple PDFs into one
- Simple drag-and-drop or file upload interface
- No files stored on the server — privacy-first
- Responsive and user-friendly design

---

##  Tech Stack

- **Backend:** Python, Flask
- **Frontend:** HTML, CSS, JavaScript
- **PDF Handling:** PyPDF2 or PyMuPDF (fitz)

---

##  Installation

### Prerequisites
- Python 3.7+
- `pip` (Python package manager)

### Clone the Repository

```bash
git clone https://github.com/yourusername/pdf-merger-tool.git
cd pdf-merger-tool
````

### Install Dependencies

```bash
pip install -r requirements.txt
```

> Make sure your `requirements.txt` includes:
>
> ```
> Flask
> PyPDF2
> ```

### Run the App

```bash
python app.py
```

Open your browser and go to [http://127.0.0.1:5000](http://127.0.0.1:5000)

---

##  Project Structure

```
pdf-merger-tool/
│
├── static/
│   ├── css/
│   └── js/
│
├── templates/
│   └── index.html
│
├── uploads/               # Temporary storage for uploaded PDFs
│
├── app.py                 # Flask backend
├── requirements.txt
└── README.md
```

---

##  Usage

1. Open the web app in your browser.
2. Drag and drop or select multiple PDF files.
3. Click "Merge PDFs".
4. The merged file will be generated and offered for download.

---

##  Notes

* All processing is done server-side, and files are removed after merging.
* Ideal for small to medium-sized PDF files.
* You can deploy it to platforms like **Heroku**, **Render**, or **Vercel (via serverless Flask wrappers)**.

---

##  License

This project is licensed under the [MIT License](LICENSE).

---

##  Acknowledgements

* [Flask](https://flask.palletsprojects.com/)
* [PyPDF2](https://pypi.org/project/PyPDF2/)
* [PDF.js](https://mozilla.github.io/pdf.js/) (if preview support is added)
