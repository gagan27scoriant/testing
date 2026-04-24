pipeline {
    agent { label 'Jenkins-Agent' }
    tools {
        maven 'Maven3'
        jdk 'Java17'
    }
    environment {
	    APP_NAME = "testing"
        RELEASE = "1.0.0"
        DOCKER_USER = "gagan1rr21ai017"
        DOCKER_PASS = 'dockerhub'
        IMAGE_NAME = "${DOCKER_USER}" + "/" + "${APP_NAME}"
        IMAGE_TAG = "${RELEASE}-${BUILD_NUMBER}"
	    JENKINS_API_TOKEN = credentials("JENKINS_API_TOKEN")
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

        stage('Quality Gate') {
            steps {
                script {
                    waitForQualityGate abortPipeline: false, credentialsId: 'Jenkins-sonarqube-token'
                }
            }
        }

        stage("Build & Push Docker Image") {
            steps {
                script {
                    docker.withRegistry('',DOCKER_PASS) {
                        docker_image = docker.build "${IMAGE_NAME}"
                    }

                    docker.withRegistry('',DOCKER_PASS) {
                        docker_image.push("${IMAGE_TAG}")
                        docker_image.push('latest')
                    }
                }
            }
       }

       stage('Trivy Scan') {
            steps {
                script {
                    sh ('docker run --rm -v /var/run/docker.sock:/var/run/docker.sock aquasec/trivy image gagan1rr21ai017/testing:latest --no-progress --scanners vuln --exit-code 0 --severity HIGH,CRITICAL --format table')
                }
            }
        }

        stage('Cleanup Artifacts') {
            steps {
                script {
                    sh 'docker rmi -f ${IMAGE_NAME}:${IMAGE_TAG}'
                    sh 'docker rmi -f ${IMAGE_NAME}:latest'
                }
            }
        }

		stage('Trigger CD Pipeline') {
			steps {
				script {
                    sh "curl -v -k --user clouduser:${JENKINS_API_TOKEN} -X POST -H 'cache-control: no-cache' -H 'content-type: application/x-www-form-urlencoded' --data 'IMAGE_TAG=${IMAGE_TAG}' 'ec2-51-20-4-59.eu-north-1.compute.amazonaws.com:8080/job/gitops-testing-CD/buildWithParameters?token=gitops-token'"
				}
			}
		}
    }
}
