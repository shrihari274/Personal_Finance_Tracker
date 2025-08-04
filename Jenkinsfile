pipeline {
    agent any

    environment {
        // --- Application-Specific Configuration ---
        IMAGE_NAME            = "finance-tracker-app:${BUILD_NUMBER}"
        APP_PORT              = 8000
        CONTAINER_NAME        = "finance-tracker-instance"

        // --- ThreatMapper Configuration (from your template) ---
        DEEPFENCE_CONSOLE_URL = '192.168.74.125'
        SCANNER_VERSION       = '2.5.2'
        DEEPFENCE_PRODUCT     = 'ThreatMapper'

        // --- Scan Failure Conditions (from your template) ---
        FAIL_ON_CRITICAL_VULNS = 2
        FAIL_ON_HIGH_VULNS     = 15
        FAIL_ON_MEDIUM_VULNS   = 30
        FAIL_ON_LOW_VULNS      = 10
        FAIL_ON_HIGH_SECRETS   = 3
        FAIL_ON_HIGH_MALWARE   = 1
    }

    stages {
        stage('1. Checkout Code') {
            steps {
                echo "Checking out source code from SCM..."
                checkout scm
            }
        }

        stage('2. Build Docker Image') {
            steps {
                echo "Building Docker image: ${IMAGE_NAME}"
                sh "docker build -t ${IMAGE_NAME} ."
            }
        }

        stage('3. Scan for Vulnerabilities') {
            steps {
                script {
                    echo "Scanning image for vulnerabilities..."
                    withCredentials([
                        string(credentialsId: 'deepfence-api-key', variable: 'DF_API_KEY'),
                        string(credentialsId: 'deepfence-license-key', variable: 'DF_LICENSE_KEY')
                    ]) {
                        // CORRECTED: Removed trailing spaces after each backslash
                        sh """
                            docker run --rm --net=host -v /var/run/docker.sock:/var/run/docker.sock:rw \
                            quay.io/deepfenceio/deepfence_package_scanner_cli:${SCANNER_VERSION} \
                            -console-url=${DEEPFENCE_CONSOLE_URL} \
                            -deepfence-key=${DF_API_KEY} \
                            -license=${DF_LICENSE_KEY} \
                            -product=${DEEPFENCE_PRODUCT} \
                            -source=${IMAGE_NAME} \
                            -scan-type=base,java,python,ruby,php,nodejs,js \
                            -fail-on-critical-count=${FAIL_ON_CRITICAL_VULNS} \
                            -fail-on-high-count=${FAIL_ON_HIGH_VULNS} \
                            -fail-on-medium-count=${FAIL_ON_MEDIUM_VULNS} \
                            -fail-on-low-count=${FAIL_ON_LOW_VULNS}
                         """
                    }
                }
            }
        }

        stage('4. Scan for Secrets') {
            steps {
                script {
                    echo "Scanning image for secrets..."
                    withCredentials([
                        string(credentialsId: 'deepfence-api-key', variable: 'DF_API_KEY'),
                        string(credentialsId: 'deepfence-license-key', variable: 'DF_LICENSE_KEY')
                    ]) {
                        // CORRECTED: Removed trailing spaces after each backslash
                        sh """
                            docker run --rm --net=host -v /var/run/docker.sock:/var/run/docker.sock:rw \
                            quay.io/deepfenceio/deepfence_secret_scanner:${SCANNER_VERSION} \
                            -image-name=${IMAGE_NAME} \
                            -deepfence-key=${DF_API_KEY} \
                            -license=${DF_LICENSE_KEY} \
                            -product=${DEEPFENCE_PRODUCT} \
                            -fail-on-high-count=${FAIL_ON_HIGH_SECRETS}
                        """
                    }
                }
            }
        }

        stage('5. Scan for Malware') {
            steps {
                script {
                    echo "Scanning image for malware..."
                    withCredentials([
                        string(credentialsId: 'deepfence-api-key', variable: 'DF_API_KEY'),
                        string(credentialsId: 'deepfence-license-key', variable: 'DF_LICENSE_KEY')
                    ]) {
                        // CORRECTED: Removed trailing spaces after each backslash
                        sh """
                            docker run --rm --net=host -v /var/run/docker.sock:/var/run/docker.sock:rw \
                            quay.io/deepfenceio/deepfence_malware_scanner:${SCANNER_VERSION} \
                            -image-name=${IMAGE_NAME} \
                            -deepfence-key=${DF_API_KEY} \
                            -license=${DF_LICENSE_KEY} \
                            -product=${DEEPFENCE_PRODUCT} \
                            -fail-on-high-count=${FAIL_ON_HIGH_MALWARE}
                        """
                    }
                }
            }
        }

        stage('6. Deploy Application') {
            when {
                expression { currentBuild.result == null || currentBuild.result == 'SUCCESS' }
            }
            steps {
                script {
                    echo "All scans passed. Deploying the application..."
                    sh "docker stop ${CONTAINER_NAME} || true"
                    sh "docker rm ${CONTAINER_NAME} || true"
                    echo "Starting new container ${CONTAINER_NAME} on port ${APP_PORT}"
                    sh "docker run -d --name ${CONTAINER_NAME} -p ${APP_PORT}:${APP_PORT} ${IMAGE_NAME}"
                }
            }
        }
    }

    post {
        always {
            echo "Pipeline finished. Cleaning up workspace..."
        }
        success {
            echo "Pipeline completed successfully!"
        }
        failure {
            echo "Pipeline failed! Please check the logs for the failing stage."
        }
    }
}

