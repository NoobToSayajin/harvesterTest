FROM debian:12

# Mettre à jour les sources et installer les dépendances pour compiler Python
RUN apt update && \
    apt install -y git build-essential zlib1g-dev libssl-dev libncurses5-dev libgdbm-dev \
    libnss3-dev libreadline-dev libffi-dev curl libsqlite3-dev libbz2-dev \
    tcl-dev tk-dev libtcl8.6 libtk8.6 \
    iputils-ping x11vnc x11-xserver-utils xvfb fluxbox novnc websockify nmap numlockx && \
    rm -rf /var/lib/apt/lists/*

# Télécharger et compiler Python 3.13 avec le support Tcl/Tk
WORKDIR /usr/src
RUN curl -O https://www.python.org/ftp/python/3.13.0/Python-3.13.0.tgz && \
    tar -xf Python-3.13.0.tgz && \
    cd Python-3.13.0 && \
    ./configure --enable-optimizations --with-tcltk-includes='-I/usr/include/tcl8.6' --with-tcltk-libs='-ltcl8.6 -ltk8.6' && \
    make -j$(nproc) && \
    make altinstall && \
    cd .. && \
    rm -rf Python-3.13.0*

RUN mkdir -p /data/Scans

WORKDIR /app
# Script de démarrage
RUN echo '#!/bin/bash\n\
if [ -d ".git" ]; then\n\
  echo "Récupération de la dernière version du code..."\n\
  git fetch \n\
  git pull\n\
else\n\
  echo "Préparation au clonage du dépôt..."\n\
  if [ -d "/app" ] && [ -n "$(ls -A /app)" ]; then\n\
    echo "le répertoire n est pas vide..."\n\
    mkdir /tmp/app ; mv /app/* /tmp/appr m-fr /app/*\n\
    echo "Clonage du dépôt..."\n\
    git clone http://172.16.2.253/mspr/harvester.git /app && mv /tmp/app/* /app\n\
  else\n\
    echo "le répertoire est vide..."\n\
    echo "Clonage du dépôt..."\n\
    git clone http://172.16.2.253/mspr/harvester.git /app\n\
  fi\n\
fi\n\
echo "Création de l environement virtuel..."\n\
python3.13 -m venv .venv\n\
echo "Activation de l environement virtuel..."\n\
source .venv/bin/activate\n\
if [ -f requirements ]; then\n\
  echo "Installation des dépendances..."\n\
  pip install --no-cache-dir -r requirements\n\
else\n\
  echo "Fichier requirements manquant"\n\
fi\n\
echo "$(git describe --tags $(git rev-list --tags --max-count=1))-$(git rev-parse --short HEAD)" > VERSION\n\
echo "Starting Xvfb..."\n\
Xvfb :99 -screen 0 1920x1080x16 &\n\
export DISPLAY=:99\n\
sleep 10\n\
echo "Starting Fluxbox..."\n\
fluxbox &\n\
sleep 5\n\
echo "Activating NumLock..."\n\
numlockx on &\n\sleep 5\n\
echo "Starting x11vnc..."\n\
x11vnc -xkb -rfbport 5900 -display :99 -nopw -forever -noxdamage -noxinerama -noxrecord -noxfixes -localhost &\n\
sleep 5\n\
echo "Starting websockify..."\n\
websockify --web /usr/share/novnc/ 5901 localhost:5900 &\n\
echo "Starting the application..."\n\
python3.13 main.py' > /start.sh

RUN ln -s /data/Scans /app/Scans

RUN chmod +x /start.sh

# Exposer les ports nécessaires
EXPOSE 5901

# Exécuter le script au démarrage du conteneur
CMD ["/bin/bash", "/start.sh"]