
pipeline {
    agent any

    environment {
        IMAGE_NAME = 'smart-campus-platform'
        PYTHON = 'C:\\Users\\acer\\AppData\\Local\\Programs\\Python\\Python313\\python.exe'
        DOCKER_HOST = 'npipe:////./pipe/dockerDesktopLinuxEngine'
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Install Dependencies') {
            steps {
                bat '"%PYTHON%" -m pip install -r requirements.txt'
            }
        }

        stage('Automated Tests') {
            steps {
                bat '"%PYTHON%" -m pytest -q'
            }
        }

        stage('Verify Docker') {
            steps {
                bat 'docker version'
            }
        }

        stage('Build Docker Image') {
            steps {
                bat 'docker build -t %IMAGE_NAME%:%BUILD_NUMBER% .'
            }
        }

        stage('Deploy to Test Environment') {
            steps {
                bat 'docker rm -f campus-test 2>NUL || exit /b 0'
                bat 'docker run -d --name campus-test -p 5001:5000 %IMAGE_NAME%:%BUILD_NUMBER%'
            }
        }

        stage('Smoke Test') {
            steps {
                bat '"%PYTHON%" -c "import urllib.request; r=urllib.request.urlopen(\'http://127.0.0.1:5001/health\', timeout=15); print(r.status); print(r.read().decode())"'
            }
        }
    }

    post {
        always {
            echo 'Pipeline execution completed. Review test and deployment results.'
        }
    }
}
