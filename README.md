# Tonuino Label Maker

WARNING: In Development

Tonuino Label Maker is a PyQt6 application designed for creating sticker labels for RFID cards. These cards are used with custom music players like Tonuino or ESPuino. The sticker labels are compatible e.g. with Herma 5028 label sheets. Edit the resources/template.json to support your custom label sheets.

![ScreenShot](https://raw.github.com/gbbnq/tonuino-label-maker-pyqt6.git/main/screenshot.png)

## Installation

1. **Clone the repository**:

    ```bash
    git clone https://github.com/gbbnq/tonuino-label-maker-pyqt6.git
    cd tonuino-label-maker-pyqt6
    ```

2. **Install dependencies**:

    Run the following command to set up the virtual environment and install the necessary dependencies:

    ```bash
    install.bat
    ```

3. **Activate virtual environment**:
   
   This is handled within `install.bat`, but if you need to activate the virtual environment manually, run:

   ```bash
   call venv\Scripts\activate
   ```

 4. **Building the Application**:

   To build the application, simply run:

   ```bash
   build.bat
   ```

## Usage

Once installed and built, you can start the application by executing the compiled executable in the dist directory. Select the template and the export path. For each free label, click on it in the preview image, select an image from your local drive, define the label settings and apply the label. Finally, export the PDF.

## Contributing

Contributions are welcome! Please fork the repository and submit pull requests with detailed information on any changes made.

## License

This project is licensed under the MIT License file for details.