cd ../../flask_microservices/audio_microservice
useradd -m $1
echo -e "$2\n$2" | passwd $1
usermod -a -G streamers $1