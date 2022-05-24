## Setup

### Build the node docker image

    docker build . -t <image-name>

### Run the docker image

    docker run -p <port>:8080 -d <image-name>