useradd -m $1
echo -e "$2\n$2" | passwd $1
usermod -a -G streamers $1
mkdir -p /stream/$1/video
mkdir -p /stream/$1/audio
chown $1 /stream/$1/video
chown $1 /stream/$1/audio
chmod u+w /stream/$1/video
chmod u+w /stream/$1/audio