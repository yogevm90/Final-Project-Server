groupadd streamers
cd ../../../flask_microservices/audio_microservice
chgrp streamers ./statoc
chmod -R g+rwx ./static