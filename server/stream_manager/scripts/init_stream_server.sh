mkdir /stream
groupadd streamers
chgrp streamers ../../../flask_microservices/static/stream
chmod -R g+r ./static/stream