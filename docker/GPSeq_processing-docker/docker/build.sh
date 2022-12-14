#!/bin/bash
cp ../requirements.txt .
image=gpseq
version=1.0
registry=bicrolab
docker image rm $image
docker image rm $registry/$image:$version
docker image rm $registry/$image:latest
docker build -t $image -f ./Dockerfile .
docker tag $image $registry/$image:$version
docker tag $image $registry/$image:latest

#docker push $registry
# docker push $registry/$image:latest
# docker push $registry/$image:$version
