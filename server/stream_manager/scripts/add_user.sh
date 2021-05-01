useradd -m $1
echo -e "$2\n$2" | passwd $1
usermod -a -G streamers $1
mkdir /stream/$1/video
mkdir /stream/$1/audio
chown $1 /stream/video
chown $1 /stream/audio
chmod u+w /stream/video
chmod u+w /stream/audio