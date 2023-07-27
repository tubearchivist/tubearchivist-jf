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

if [[ $1 == "validate" ]]; then
    validate "$2"
elif [[ $1 == "test" ]]; then
    sync_test
else
    echo "valid options are: validate | test"
fi


##
exit 0
