#!/bin/bash

set -e

function validate {

    if [[ $1 ]]; then
        check_path="$1"
    else
        check_path="."
    fi

    echo "run validate on $check_path"

    # note: this logic is duplicated in the `./github/workflows/lint_python.yml` config
    # if you update this file, you should update that as well
    echo "running black"
    black --force-exclude "migrations/*" --diff --color --check -l 79 "$check_path"
    echo "running codespell"
    codespell --skip="./.git,./.venv,./.mypy_cache" "$check_path"
    echo "running flake8"
    flake8 "$check_path" --exclude "migrations,.venv" --count --max-complexity=10 \
        --max-line-length=79 --show-source --statistics
    echo "running isort"
    isort --skip "migrations" --skip ".venv" --check-only --diff --profile black -l 79 "$check_path"
    printf "    \n> all validations passed\n"

}

function sync_test {

    # docker commands don't need sudo in testing vm

    host="tubearchivist.local"
    # make base folder
    ssh "$host" "mkdir -p docker"

    # copy project files to build image
    rsync -a --progress --delete-after \
        --exclude ".git" \
        --exclude ".gitignore" \
        --exclude "**/cache" \
        --exclude "**/__pycache__/" \
        --exclude ".venv" \
        --exclude "db.sqlite3" \
        --exclude ".mypy_cache" \
        . -e ssh "$host":tubearchivist-jf

    ssh "$host" "docker buildx build --build-arg INSTALL_DEBUG=1 -t bbilly1/tubearchivist-jf:latest tubearchivist-jf --load"
    ssh "$host" 'docker compose -f docker/docker-compose.yml up -d'

}

# old local release build
function sync_docker_old {

    # check things
    if [[ $(git branch --show-current) != 'master' ]]; then
        echo 'you are not on master, dummy!'
        return
    fi

    if [[ $(systemctl is-active docker) != 'active' ]]; then
        echo "starting docker"
        sudo systemctl start docker
    fi

    echo "latest tags:"
    git tag | tail -n 5 | sort -r

    printf "\ncreate new version:\n"
    read -r VERSION

    echo "build and push $VERSION?"
    read -rn 1

    # start build
    docker buildx build \
        --platform linux/amd64,linux/arm64 \
        -t bbilly1/tubearchivist-jf \
        -t bbilly1/tubearchivist-jf:"$VERSION" --push .

    # create release tag
    echo "commits since last version:"
    git log "$(git describe --tags --abbrev=0)"..HEAD --oneline
    git tag -a "$VERSION" -m "new release version $VERSION"
    git push origin "$VERSION"

}


function sync_docker {

    # check things
    if [[ $(git branch --show-current) != 'master' ]]; then
        echo 'you are not on master, dummy!'
        return
    fi

    echo "latest tags:"
    git tag | tail -n 5 | sort -r

    printf "\ncreate new version:\n"
    read -r VERSION

    echo "push new tag: $VERSION?"
    read -rn 1

    # create release tag
    echo "commits since last version:"
    git log "$(git describe --tags --abbrev=0)"..HEAD --oneline
    git tag -a "$VERSION" -m "new release version $VERSION"
    git push origin "$VERSION"

}


if [[ $1 == "validate" ]]; then
    validate "$2"
elif [[ $1 == "test" ]]; then
    sync_test
elif [[ $1 == "docker" ]]; then
    sync_docker
else
    echo "valid options are: validate | test | docker"
fi


##
exit 0
