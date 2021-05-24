cd ../../flask_microservices/audio_microservice
useradd -m $1
echo -e "$2\n$2" | passwd $1
usermod -a -G streamers $1
mkdir -p /static/$1/audio
chown $1 /static/$1/audio
chmod u+w /static/$1/audio