#!/bin/sh
until python ./get_hashtag.py; do
    echo "53cycling crashed with exit code $?.  Respawning.." >&2
    sleep 1
done

