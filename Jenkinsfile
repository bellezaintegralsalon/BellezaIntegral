pipeline {
    agent any
    options {
        skipDefaultCheckout(true)
        disableConcurrentBuilds()
        timeout(time: 35, unit: 'MINUTES')
        buildDiscarder(logRotator(numToKeepStr: '15'))
    }
    parameters {
        booleanParam(name: 'DEPLOY_STAGING', defaultValue: false, description: 'Activar cuando el servicio y las credenciales de staging estén configurados')
        string(name: 'RAILWAY_PROJECT_ID', defaultValue: '', description: 'Proyecto Railway de pruebas')
        string(name: 'RAILWAY_SERVICE_ID', defaultValue: '', description: 'Servicio Railway de staging')
        string(name: 'STAGING_URL', defaultValue: '', description: 'URL HTTPS del servicio de staging')
    }
    environment {
        SERVICE = 'all'
        TZ = 'America/Guatemala'
        CHROME_NO_SANDBOX = '1'
    }
    stages {
        stage('Checkout') {
            steps { checkout scm }
        }
        stage('Build') {
            steps {
                sh '''
                    python3 -m venv .venv
                    .venv/bin/python -m pip install -r requirements-test.txt
                    .venv/bin/python -m compileall -q app scripts tests
                    .venv/bin/python -m pip check
                    command -v docker
                '''
            }
        }
        stage('Test') {
            steps { sh 'bash scripts/ci_jenkins.sh' }
        }
        stage('Deploy staging') {
            when { expression { params.DEPLOY_STAGING } }
            steps {
                script {
                    if (!params.RAILWAY_PROJECT_ID.trim() || !params.RAILWAY_SERVICE_ID.trim() || !params.STAGING_URL.trim()) {
                        error('Completar proyecto, servicio y URL de staging antes del despliegue')
                    }
                }
                withCredentials([string(credentialsId: 'railway-staging-token', variable: 'RAILWAY_TOKEN')]) {
                    withEnv(["RAILWAY_PROJECT_ID=${params.RAILWAY_PROJECT_ID.trim()}", "RAILWAY_SERVICE_ID=${params.RAILWAY_SERVICE_ID.trim()}", "STAGING_URL=${params.STAGING_URL.trim()}"]) {
                        sh 'bash scripts/deploy_staging.sh'
                    }
                }
            }
        }
    }
    post {
        always {
            junit testResults: 'artifacts/*.xml', allowEmptyResults: true
            archiveArtifacts artifacts: 'artifacts/**', allowEmptyArchive: true
        }
    }
}
