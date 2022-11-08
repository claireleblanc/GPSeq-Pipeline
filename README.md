# GPSeq-Pipeline

Tutorial modified from https://github.com/GG-space/gpseq-preprocessing-tutorial


Used this to install docker: https://docs.docker.com/engine/install/ubuntu/

To add user to docker group: sudo usermod -aG docker $USER

if this doesn't work right away, try logging out and logging back in

To see users in docker group: grep /etc/group -e "docker"

To list docker images: docker image ls

Building the docker image (docker build -t $image -f ./Dockerfile .) took roughly 15 minutes. 

If build fails with error "Connection reset by peer" or "error: retrieving gpg key timed out," it could be that your machine is running too many processes at once. Try running it again after some time. 
- can also try running each command in thee build.sh file individually to see which command is causing issues. 

If buiild was sucessfull, docker image ls should show three new entries: 
REPOSITORY       TAG       IMAGE ID       CREATED         SIZE
bicrolab/gpseq   1.0       537f5c282500   3 minutes ago   2.97GB
bicrolab/gpseq   latest    537f5c282500   3 minutes ago   2.97GB
gpseq            latest    537f5c282500   3 minutes ago   2.97GB
