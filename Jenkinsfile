pipeline {
    agent any

    environment {
        IMAGE_NAME = 'loan-predictor:local'
        CONTAINER_NAME = 'loan-api-local'
    }

    stages {
        stage('Clone & Clean') {
            steps {
                echo 'Cleaning up any leftover project state...'
                // Using standard shell execution for your Linux environment
                sh 'git clean -fdx || true'
            }
        }

        stage('Build Image') {
            steps {
                echo 'Building Docker Image... (Uses cached layers after the first run)'
                sh 'docker build -t ${IMAGE_NAME} .'
            }
        }

        stage('Deploy Local API') {
            steps {
                echo 'Handling port 5001 conflicts and running container...'
                // Best Practice: Check if a container with the same name exists, stop it, and run the new one safely.
                sh '''
                    if [ \$(docker ps -aq -f name=^/${CONTAINER_NAME}\$) ]; then
                        echo "Stopping existing container..."
                        docker stop ${CONTAINER_NAME} || true
                    fi
                    docker run -d --rm -p 5001:5001 --name ${CONTAINER_NAME} ${IMAGE_NAME}
                '''
            }
        }

        stage('Sanity Check') {
            steps {
                echo 'Verifying application health probe...'
                // Wait 3 seconds for Gunicorn workers to initialize inside the container
                sleep 3
                sh 'curl --fail http://localhost:5001/health'
            }
        }
    }
}