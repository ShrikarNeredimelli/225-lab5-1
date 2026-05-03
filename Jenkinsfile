pipeline {
    agent any
    environment {
        DOCKER_CREDENTIALS_ID = 'roseaw-dockerhub'
        DOCKER_IMAGE = 'cithit/neredis'
        IMAGE_TAG = "build-${BUILD_NUMBER}"
        GITHUB_URL = 'https://github.com/ShrikarNeredimelli/225-lab5-1.git'
        KUBECONFIG = credentials('neredis-225-sp26')
    }
    stages {
        stage('Checkout') {
            steps {
                cleanWs()
                checkout([$class: 'GitSCM', branches: [[name: '*/main']],
                          userRemoteConfigs: [[url: "${GITHUB_URL}"]]])
            }
        }
        stage('Static Code Analysis') {
            steps {
                script {
                    sh 'docker run --rm -v $WORKSPACE:/app -w /app python:3.9-slim sh -c "pip install pyflakes --quiet && python -m pyflakes main.py"'
                }
            }
        }
        stage('Run Tests') {
            steps {
                script {
                    sh 'docker run --rm -v $WORKSPACE:/app -w /app python:3.9-slim sh -c "pip install pytest flask --quiet && pytest test_app.py -v"'
                }
            }
        }
        stage('Security Scan') {
            steps {
                script {
                    sh 'docker run --rm -v $WORKSPACE:/app -w /app python:3.9-slim sh -c "pip install bandit --quiet && bandit -r . -x ./test_app.py --exit-zero"'
                }
            }
        }
        stage('Build Docker Image') {
            steps {
                script {
                    docker.withRegistry('https://registry-1.docker.io', 'roseaw-dockerhub') {
                        docker.build("${DOCKER_IMAGE}:${IMAGE_TAG}")
                    }
                }
            }
        }
        stage('Push Docker Image') {
            steps {
                script {
                    docker.withRegistry('https://index.docker.io/v1/', "${DOCKER_CREDENTIALS_ID}") {
                        docker.image("${DOCKER_IMAGE}:${IMAGE_TAG}").push()
                    }
                }
            }
        }
        stage('Deploy to Dev Environment') {
            steps {
                script {
                    def kubeConfig = readFile(KUBECONFIG)
                    sh "sed -i 's|${DOCKER_IMAGE}:latest|${DOCKER_IMAGE}:${IMAGE_TAG}|' deployment-dev.yaml"
                    sh "kubectl apply -f deployment-dev.yaml"
                }
            }
        }
        stage('Check Kubernetes Cluster') {
            steps {
                script {
                    sh "kubectl get all"
                }
            }
        }
    }
    post {
        success {
            slackSend color: "good", message: "Build Completed: ${env.JOB_NAME} ${env.BUILD_NUMBER}"
        }
        unstable {
            slackSend color: "warning", message: "Build Completed: ${env.JOB_NAME} ${env.BUILD_NUMBER}"
        }
        failure {
            slackSend color: "danger", message: "Build Completed: ${env.JOB_NAME} ${env.BUILD_NUMBER}"
        }
    }
}
