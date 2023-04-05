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
    black --exclude "migrations/*" --diff --color --check -l 79 "$check_path"
    echo "running codespell"
    codespell --skip="./.git,./package.json,./package-lock.json,./node_modules,./.mypy_cache" "$check_path"
    echo "running flake8"
    flake8 "$check_path" --exclude "migrations" --count --max-complexity=10 \
        --max-line-length=79 --show-source --statistics
    echo "running isort"
    isort --skip "migrations" --check-only --diff --profile black -l 79 "$check_path"
    printf "    \n> all validations passed\n"

}

if [[ $1 == "validate" ]]; then
    validate "$2"
else
    echo "valid options are: validate"
fi


##
exit 0
