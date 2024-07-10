# Getting Started with PyBLEToolkit

Welcome to PyBLEToolkit! This guide will walk you through setting up and starting to use the PyBLEToolkit to create and
manage Bluetooth Low Energy (BLE) service GUIs with Python and tkinter.

## Prerequisites

Before you begin, ensure you have the following installed on your system:

- Python 3.6 or newer
- pip (Python package installer)
- Git (for version control)

## Installation

1. **Clone the Repository**
   Clone PyBLEToolkit to your local machine using Git:
   ```bash
   git clone https://github.com/muhamm-ad/PyBLEToolkit.git
   ```

2. **Navigate to the Project Directory**
   Change into the project directory:
   ```bash
   cd PyBLEToolkit
   ```

3. **Create a Virtual Environment**
   Create a virtual environment to manage dependencies:
   ```bash
   python -m venv venv
   ```

4. **Activate the Virtual Environment**
    - On Linux:
      ```bash
      source venv/bin/activate
      ```
    - On Windows (Command Prompt):
      ```sh
      venv\Scripts\activate
      ```
    - On Windows (PowerShell):
      ```sh
      .\venv\Scripts\Activate.ps1
      ```

5. **Install Dependencies**
   Install the required Python libraries:
   ```bash
   pip install -r requirements.txt
   ```

## Setting Up Your Development Environment

1. **Open Your IDE**
   Open your preferred Integrated Development Environment (IDE) or code editor. We recommend using Visual Studio Code or
   PyCharm for Python development.

2. **Explore the Source Code**
   Take a moment to explore the structure of the project. Familiarize yourself with the content in the `src`
   and `examples` directories.

## Running the Code

### On Linux

1. **Navigate to the Project Directory**
   Ensure you are in the root directory of the project:
   ```bash
   cd /path/to/PyBLEToolkit
   ```

2. **Activate the Virtual Environment**
   ```bash
   source venv/bin/activate
   ```

3. **Run the Main Script**
   Use the following command to run the main script:
   ```bash
   python3 -m src.main
   ```

### On Windows

1. **Navigate to the Project Directory**
   Ensure you are in the root directory of the project. You can navigate using the Command Prompt or PowerShell:
   ```sh
   cd \path\to\PyBLEToolkit
   ```

2. **Activate the Virtual Environment**
    - Command Prompt:
      ```sh
      venv\Scripts\activate
      ```
    - PowerShell:
      ```sh
      .\venv\Scripts\Activate.ps1
      ```

3. **Run the Main Script**
   Use the following command to run the main script:
   ```sh
   python -m src.main
   ```

## Getting Help

If you encounter any issues or have questions, please check out
our [issues page](https://github.com/muhamm-ad/PyBLEToolkit/issues) on GitHub.