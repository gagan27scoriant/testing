pipeline {
    agent { label 'Jenkins-Agent' }
    tools {
        maven 'Maven3'
        jdk 'Java17'
    }
    stages {
        stage('Cleaanup Workspace') {
            steps {
                cleanWs()
            }
        }
        stage('Test') {
            steps {
                sh 'mvn test'
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
    }
} 