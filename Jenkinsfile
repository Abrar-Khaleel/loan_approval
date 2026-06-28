pipeline {
    agent any

    environment {
        IMAGE_NAME = 'loan-predictor:local'
        CONTAINER_NAME = 'loan-api-local'
        // FIX: Inject the standard macOS Docker binary paths directly into the Jenkins runtime execution path
        PATH = "/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin:${env.PATH}"
    }

    stages {
        stage('Clone & Clean') {
            steps {
                echo 'Cleaning up any leftover project state...'
                sh 'git clean -fdx || true'
            }
        }

        stage('Build Image') {
            steps {
                echo 'Building Docker Image...'
                sh 'docker build -t ${IMAGE_NAME} .'
            }
        }

        stage('Deploy Local API') {
            steps {
                echo 'Handling port 5001 conflicts and running container...'
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
                sleep 3
                sh 'curl --fail http://localhost:5001/health'
            }
        }
    }
}