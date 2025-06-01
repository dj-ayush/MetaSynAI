🎛️ MetaSynAI
MetaSynAI is an innovative project that integrates voice commands, hand gestures, and eye-tracking to create an accessible and intuitive user interface. It aims to enhance user interaction by providing multiple input modalities, making technology more inclusive and user-friendly.

🚀 Features
Voice Assistant: Control applications and navigate interfaces using voice commands.

Hand Gesture Recognition: Utilize hand gestures for seamless interaction without physical contact.

Eye-Tracking Integration: Navigate and interact with interfaces using eye movement, enhancing accessibility.

Responsive Web Interface: A user-friendly web interface that adapts to various devices and screen sizes.

🛠️ Technologies Used
Frontend: HTML, CSS, JavaScript

Backend: Python (Flask)

Machine Learning: TensorFlow, OpenCV

Voice Recognition: SpeechRecognition API

Eye-Tracking: Dlib, OpenCV

📁 Project Structure
pgsql
Copy
Edit
MetaSynAI/
├── assets/
├── css/
├── js/
├── templates/
│   ├── index.html
│   ├── voice-assistant.html
│   ├── hand-gestures.html
│   └── eye-gaze.html
├── app.py
├── gesture_server.py
├── voice-assistant-server.js
└── README.md
🧪 Setup and Installation
Clone the repository:

bash
Copy
Edit
git clone https://github.com/dj-ayush/MetaSynAI.git
cd MetaSynAI
Create a virtual environment:

bash
Copy
Edit
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
Install the dependencies:

bash
Copy
Edit
pip install -r requirements.txt
Run the application:

bash
Copy
Edit
python app.py
Access the application:
Open your browser and navigate to http://localhost:5000

🤝 Contributing
Contributions are welcome! Please follow these steps:

Fork the repository

Create a new branch:

bash
Copy
Edit
git checkout -b feature-name
Commit your changes:

bash
Copy
Edit
git commit -m "Add feature"
Push to the branch:

bash
Copy
Edit
git push origin feature-name
Open a pull request

📄 License
This project is licensed under the MIT License.
