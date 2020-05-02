docker run \
    -it \
    --rm \
    -w /home \
    -v $PWD/scripts:/home \
    machine-learning \
    bash