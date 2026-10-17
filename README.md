# Forensic Sketch Matching Project

This project is a forensic sketch matching application that utilizes machine learning models to assist in the identification of individuals based on forensic sketches. The application is structured into three main components: backend, frontend, and machine learning models.

## Project Structure

```
forensic-sketch-matching
├── backend
│   ├── app.py
│   ├── models.py
│   ├── database.py
│   ├── auth.py
│   ├── requirements.txt
│   └── .env
├── frontend
│   ├── index.html
│   ├── login.html
│   └── sketch_generator.html
├── ml_models
│   ├── image_recognition.py
│   └── sketch_generator.py
└── README.md
```

## Setup Instructions

1. **Clone the repository:**
   ```
   git clone <repository-url>
   cd forensic-sketch-matching
   ```

2. **Set up the backend:**
   - Navigate to the `backend` directory.
   - Create a `.env` file with the necessary environment variables (e.g., database credentials).
   - Install the required dependencies:
     ```
     pip install -r requirements.txt
     ```

3. **Run the backend application:**
   ```
   python app.py
   ```

4. **Set up the frontend:**
   - Open the `frontend/index.html` file in a web browser to access the application.

## Usage

- The application allows users to log in and access the sketch generator interface.
- Users can upload images for recognition and generate sketches based on input data.

## Contributing

Contributions are welcome! Please submit a pull request or open an issue for any enhancements or bug fixes.

## License

This project is licensed under the MIT License. See the LICENSE file for more details.