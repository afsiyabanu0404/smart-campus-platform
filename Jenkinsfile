pipeline {
    agent any
    environment {
        IMAGE_NAME = 'smart-campus-platform'
    }
    stages {
        stage('Checkout') {
            steps { checkout scm }
        }
        stage('Install Dependencies') {
            steps {
                bat 'python -m pip install -r requirements.txt'
            }
        }
        stage('Automated Tests') {
            steps {
                bat 'python -m pytest -q'
            }
        }
        stage('Build Docker Image') {
            steps {
                bat 'docker build -t %IMAGE_NAME%:%BUILD_NUMBER% .'
            }
        }
        stage('Deploy to Test Environment') {
            steps {
                bat 'docker rm -f campus-test || exit /b 0'
                bat 'docker run -d --name campus-test -p 5001:5000 %IMAGE_NAME%:%BUILD_NUMBER%'
            }
        }
        stage('Smoke Test') {
            steps {
                bat 'python -c "import urllib.request; print(urllib.request.urlopen(\'http://localhost:5001/health\', timeout=10).read().decode())"'
            }
        }
    }
    post {
        always { echo 'Pipeline execution completed. Review test and deployment results.' }
    }
}
