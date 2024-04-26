node {
    withCredentials([[$class: 'UsernamePasswordMultiBinding',
        credentialsId: 'coachcoach-docker-username',
        usernameVariable: 'DOCKER_USER_ID',
        passwordVariable: 'DOCKER_USER_PASSWORD'
    ]]) {
        stage('Pull') {
            git branch: 'main', credentialsId: 'github-username-token-credential', url: 'https://github.com/COACH-COACH/Flask-Back-End.git'
        }

        stage('Build') {
       		sh 'yes | sudo docker image prune -a'
            sh 'sudo docker build -t flask-server .'
        }

        stage('Tag') {
            sh 'sudo docker tag flask-server ${DOCKER_USER_ID}/flask-server:${BUILD_NUMBER}'
        }
        
       	stage('Push') {
            sh 'sudo docker login -u $DOCKER_USER_ID -p $DOCKER_USER_PASSWORD'
            sh 'sudo docker push ${DOCKER_USER_ID}/flask-server:${BUILD_NUMBER}'      	
       	}

        stage('Deploy') {
            sshagent(credentials: ['ec2-flask-server-ssh']) {
                sh 'ssh -o StrictHostKeyChecking=no ubuntu@52.78.60.160 "sudo docker rm -f docker-flask"'
                sh 'ssh ubuntu@52.78.60.160 "sudo docker run --name docker-flask --env-file .env -e TZ=Asia/Seoul -p 80:80 -d -t \${DOCKER_USER_ID}/flask-server:\${BUILD_NUMBER}'
            }
        }
        
        stage('Cleaning Up') {
        	sh 'sudo docker rmi ${DOCKER_USER_ID}/flask-server:${BUILD_NUMBER}'
        }
    }
}
