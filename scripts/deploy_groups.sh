folder="./Group"

# create groups
# for group in $folder/*.json
# do
#     echo "processing group '$group'..."
#     body=`cat "$group"`
#     name=`echo $body | jq '.group_name' -r`

#     groups=`databricks groups list --output JSON`
#     id=`echo $groups | jq --arg name "$name" '.[] | select(.displayName==$name) | .id' -r`

#     if [[ -z "$id" ]]
#     then
#         echo "creating group '$name'..."
#         databricks groups create --display-name "$name"
#     fi
# done

# add groups to secret scopes
list=$(databricks secrets list-scopes --output JSON)
dbScopes=`echo $list | jq .[] | jq .name -r`

if [[ $list == *"RESOURCE_DOES_NOT_EXIST"* ]]
then
  echo 'Scope does not existing in workspace.'
else
  echo 'Adding ACL.'

  for dbScope in $dbScopes
  do
    echo "checking databricks scope $dbScope"

    if [ -d "$folder" ]
    then
      for group in $folder/*.json
      do
        echo "processing file '$group'..."
        body=`cat "$group"`
        name=`echo $body | jq '.group_name' -r`

        scopes=`echo $body | jq '.secret_scopes' | jq .[] -r`
        for scope in $scopes
        do
          echo "finding scope $scope in the group file"
          if [ "$scope" = "$dbScope" ]
          then
            echo "Adding $name to $scope"
            databricks secrets put-acl "$scope" "$name" READ
          fi
        done
      done
    fi
  done
fi