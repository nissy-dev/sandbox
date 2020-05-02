docker run \
    -i -t \
    -p 8888:8888 \
    --name jn \
    -v $PWD/notebooks:/opt/notebooks \
    machine-learning \
    /bin/bash -c "jupyter lab --notebook-dir=/opt/notebooks --ip='0.0.0.0' --no-browser --allow-root"
