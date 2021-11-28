cp -r ../protos .

docker run --rm \
    --platform linux/x86_64 \
    -v $(pwd)/protos:/protos \
    -v $(pwd)/src/deepthought:/deepthought \
    grpc-web \
    protoc -I /protos deepthought.proto \
    --js_out=import_style=commonjs:/deepthought \
    --grpc-web_out=import_style=typescript,mode=grpcwebtext:/deepthought

rm -rf ./protos
