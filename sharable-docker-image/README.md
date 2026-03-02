# Sharable Docker Image Project

This project demonstrates how to create a sharable Docker image for a Python application.

## Project Structure

```
sharable-docker-image
├── app
│   └── main.py
├── Dockerfile
├── .dockerignore
├── requirements.txt
└── README.md
```

## Getting Started

To build and run the Docker image for this application, follow the steps below.

### Prerequisites

- Docker installed on your machine.
- Basic knowledge of Docker and Python.

### Building the Docker Image

1. Navigate to the project directory:

   ```
   cd sharable-docker-image
   ```

2. Build the Docker image using the following command:

   ```
   docker build -t sharable-docker-image .
   ```

### Running the Docker Container

After building the image, you can run the application in a container:

```
docker run -it --rm sharable-docker-image
```

### Application Logic

The main application logic is located in `app/main.py`. You can modify this file to change the behavior of the application.

### Dependencies

The required Python packages are listed in `requirements.txt`. Make sure to update this file if you add new dependencies.

### .dockerignore

The `.dockerignore` file is used to exclude files and directories from the Docker build context, which helps to keep the image size small.

## Contributing

Feel free to submit issues or pull requests if you have suggestions or improvements for this project.