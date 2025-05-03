# README

## Overview

This project is designed to automate the creation of quote videos based on a provided prompt. The agent leverages various services to generate and compile video content efficiently and effectively.

## Features

- **Automated Video Generation**: Create quote videos seamlessly from textual prompts.
- **Customizable API Calls**: Utilize the `HttpClient` class for flexible API interactions.
- **Modular Design**: Organized codebase for easy maintenance and scalability.

## Project Structure

- `app/`
  - Contains the main application logic.
  - `services/`
    - Includes modules for API calls, LLM integration, and prompt handling.
- `data/`
  - Placeholder for data storage.

## Getting Started

1. Clone the repository:
   ```bash
   git clone <repository-url>
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up environment variables:
   - Copy `example.env` to `.env` and update the values as needed.

4. Run the application:
   ```bash
   python app/main.py
   ```

## Running the Application in VS Code or Other IDEs

### Using VS Code

1. Open the project in VS Code.
2. Ensure you have the Python extension installed.
3. Configure the debugger:
   - Open the `.vscode/launch.json` file.
   - Use the provided configuration for running the application with `uvicorn`.
4. Start debugging:
   - Press `F5` or go to the Run and Debug panel and select "Python Debugger: FastAPI".

### Using Other IDEs

1. Open the project in your preferred IDE.
2. Ensure the IDE supports Python and has `uvicorn` installed.
3. Run the application using the following command:
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 --log-level info
   ```
4. Access the application at `http://127.0.0.1:8000` in your browser.

## Contributing

Contributions are welcome! Please fork the repository and submit a pull request for any enhancements or bug fixes.

## License

This project is licensed under the MIT License. See the LICENSE file for details.