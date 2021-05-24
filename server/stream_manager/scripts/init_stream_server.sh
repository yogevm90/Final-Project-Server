groupadd streamers
cd ../../../flask_microservices/audio_microservice
chgrp streamers ./static
chmod -R g+rwx ./static