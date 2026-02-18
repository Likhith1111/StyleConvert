# StyleConvert - Image Style Transfer App

A modern web application built with Flask and OpenCV to apply artistic filters (B&W, Retro, Vintage) to images.

## Features

-   **Converting Images**: Easily switch between Original, B&W, Retro, and apply Vintage effects.
-   **Live Preview**: Instantly see changes without reloading the page.
-   **Download**: Save your processed images in high quality.
-   **Responsive Design**: Works on desktop and mobile.

## Tech Stack

-   **Backend**: Python (Flask)
-   **Image Processing**: OpenCV (cv2), NumPy
-   **Frontend**: HTML5, CSS3, JavaScript (Vanilla)

## Setup Instructions

1.  **Install Python**: Ensure Python 3.x is installed on your system.
2.  **Install Dependencies**:
    Run the following command in your terminal to install the required libraries:
    ```bash
    pip install -r requirements.txt
    ```

3.  **Run the Application**:
    Start the Flask server:
    ```bash
    python app.py
    ```

4.  **Open in Browser**:
    Open your web browser and go to: `http://127.0.0.1:5000/`

## Project Structure

-   `app.py`: Main Flask application.
-   `utils/`: Contains image processing logic.
-   `templates/`: HTML templates.
-   `static/`: CSS styles and JavaScript files.
