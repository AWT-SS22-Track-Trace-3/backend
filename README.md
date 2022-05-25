## Setup

### Build the node docker image

    docker build . -t awt-node-app

### Run the docker image

    docker run -p <port>:8080 -d awt-node-app