# Student Performance check Project

## Overview
This project is designed to display the performance of the students. Admin can upload the file in Excel format, and teachers can visualize all these.

## Features
- Admin can upload student performance data in Excel format.
- Teachers can view and analyze student performance.
- User-friendly interface for data visualization.

## Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/barun11kumar/student_performance_report.git
   ```
2. Navigate to the project directory:
   ```bash
   cd student_marks_card
   ```
3. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
5. Apply migrations:
   ```bash
   python manage.py migrate
   ```

## Usage
Run the development server:
```bash
python manage.py runserver
```
Access the application at `http://127.0.0.1:8000/`.

## Adding the Project to GitHub
1. Initialize a Git repository:
   ```bash
   git init
   ```
2. Add all files to the repository:
   ```bash
   git add .
   ```
3. Commit the changes:
   ```bash
   git commit -m "Initial commit"
   ```
4. Add the remote repository:
   ```bash
   git remote add origin https://github.com/barun11kumar/student_performance_report.git
   ```
5. Push the changes to GitHub:
   ```bash
   git push -u origin main
   ```

## Contributing
Contributions are welcome! Please follow these steps:
1. Fork the repository.
2. Create a new branch for your feature or bug fix.
3. Commit your changes and push the branch.
4. Submit a pull request.

## License
This project is licensed under the [License Name]. See the `LICENSE` file for details.

![admin dashboard](image.png)

![teacher dashboard](image-1.png)

![performanc](image-2.png)



