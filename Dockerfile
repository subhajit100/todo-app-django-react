# Use an official Python base image
FROM python:3.13.1-slim

# Set environment variables
# ENV PYTHONDONTWRITEBYTECODE 1
# ENV PYTHONUNBUFFERED 1

# Set the working directory in the container
WORKDIR /app

# Copy requirements and install dependencies
COPY todo_project/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire backend(todo_project) code (including the React build)
COPY todo_project /app

# Expose the port the app runs on
EXPOSE 8000

# Run the Django development server
# CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]

# Run the application with Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "todo_project.wsgi:application"]