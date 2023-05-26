if [ $# -eq 1 ] && [ $1 == "destroy" ]
then
  docker compose -f dc.peers.yml down --rmi all --volumes
  rm -r node4/db
else
  docker compose -f dc.peers.yml down --rmi all --volumes
fi
