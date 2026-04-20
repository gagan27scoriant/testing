pipeline {
    agent { label 'Jenkins-Agent' }
    tools {
        maven 'Maven3'
        jdk 'Java17'
    }
    stages {
        stage('Cleanup Workspace') {
            steps {
                cleanWs()
            }
        }

        stage('Checkout from SCM') {
            steps {
                git branch: 'main', credentialsId: 'github', url: 'https://github.com/gagan27scoriant/testing'
            }
        }

        stage('Build Application') {
            steps {
                sh 'mvn clean package'
            }
        }
        
        stage('Test Application') {
            steps {
                sh 'mvn test'
            }
        }

        stage('Sonarqube-Analysis') {
            steps {
                script {
                    withSonarQubeEnv(credentialsId: 'Jenkins-sonarqube-token') {
                        sh 'mvn sonar:sonar'
                    }
                }
            }
        }
    }
}
