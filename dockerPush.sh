# Récupération de la dernière version du code
git fetch
git pull

SPECIFIC_TAG=$(git describe --tags $(git rev-list --tags --max-count=1))-$(git rev-parse --short HEAD)

# compilation de l'image
docker build -t harvester:$SPECIFIC_TAG .

# Créer le tag spécifique docker hub
docker tag harvester:$SPECIFIC_TAG mspr2025grp2/harvester:latest
docker tag harvester:$SPECIFIC_TAG mspr2025grp2/harvester:$SPECIFIC_TAG

# Créer le tag spécifique docker gitlab local
docker tag harvester:$SPECIFIC_TAG 172.16.2.253:5001/harvester:latest
docker tag harvester:$SPECIFIC_TAG 172.16.2.253:5001/harvester:$SPECIFIC_TAG

# Pousser le tag spécifique
docker push mspr2025grp2/harvester:$SPECIFIC_TAG

# Pousser le tag latest
docker push mspr2025grp2/harvester:latest