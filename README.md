## Run docker compose

Docker compose automatically pulls the latest node server image from GHCR. No need to build it yourself.

    docker compose up

## Upload a new image to GHCR

### Build the node docker image

    cd node-app
    docker build . -t ghcr.io/awt-ss22-track-trace-3/awt/track-trace-server:latest

### Sign in to GHCR

Generate a personal access token (PAT) for your GitHub account. See the [docs](https://docs.github.com/en/packages/working-with-a-github-packages-registry/working-with-the-container-registry).

    export PAT=<token>

Login to docker

    echo $PAT | docker login ghcr.io -u <username> --password-stdin


### Push image

    docker push ghcr.io/awt-ss22-track-trace-3/awt/track-trace-server:latest

### Pull image

    docker pull ghcr.io/awt-ss22-track-trace-3/awt/track-trace-server:latest