import logging
import os
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import worker  # Import the worker module

# Initialize Flask app and CORS
app = Flask(__name__)
cors = CORS(app, resources={r"/*": {"origins": "*"}})
app.logger.setLevel(logging.ERROR)
# Set the upload folder in the Flask app config
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure the upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)


# Define the route for the index page
@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')  # Render the index.html template


# Define the route for processing messages
@app.route('/process-message', methods=['POST'])
def process_message_route():
    user_message = request.json['userMessage']  # Extract the user's message from the request
    print('user_message', user_message)

    bot_response = worker.process_prompt(user_message)  # Process the user's message using the worker module

    # Return the bot's response as JSON
    return jsonify({
        "botResponse": bot_response
    }), 200


# Define the route for processing documents
@app.route('/process-document', methods=['POST'])
def process_document_route():
    # Check if the 'file' key is in the uploaded files
    if 'file' not in request.files:
        return jsonify({
            "botResponse": "It seems like the file was not uploaded correctly. Please try again. If the problem persists, try using a different file."
        }), 500

    file = request.files['file']  # Extract the uploaded file

    # Check if a file was actually uploaded and has a filename
    if file.filename == '':
        return jsonify({
            "botResponse": "No file selected for uploading. Please choose a file and try again."
        }), 500

    try:
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(file_path)

        # Process the document (replace this with your logic)
        worker.process_document(file_path)

        # Return success response
        return jsonify({
            "botResponse": "Document successfully uploaded and processed. You can now ask questions about it."
        }), 200
    except Exception as e:
        # Catch any errors during file handling and processing
        return jsonify({
            "botResponse": f"An error occurred while processing the document: {str(e)}"
        }), 500


@app.route('/upload', methods=['POST'])
def upload_file():
    # Check if the 'file' part is in the request
    if 'file' not in request.files:
        return jsonify({
            "message": "No file part in the request."
        }), 400

    file = request.files['file']  # Get the file from the request

    # Check if a file was uploaded
    if file.filename == '':
        return jsonify({
            "message": "No file selected for uploading."
        }), 400

    # Save the file to the specified folder
    try:
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(file_path)

        return jsonify({
            "message": "File successfully uploaded.",
            "file_path": file_path
        }), 200
    except Exception as e:
        return jsonify({
            "message": f"File upload failed: {str(e)}"
        }), 500


# Run the Flask app
if __name__ == "__main__":
    app.run(debug=True, port=8000, host='0.0.0.0')
