if [ $# -eq 1 ] && [ $1 == "destroy" ]
then
  docker compose -f dc.validators.yml down --rmi all --volumes
  rm -r node1/db
  rm -r node2/db
  rm -r node3/db
else
  docker compose -f dc.validators.yml down --rmi all --volumes
fi
