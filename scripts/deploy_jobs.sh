echo "First arg: $1"
target_env=$1

raw_storage_account_name='uatsndatarawct7qzyl'
enriched_storage_account_name='uatsndataenrichedct7qzyl'
instance_pool_id='0917-052908-wends191-pool-mzwkjxde'
warehouse_id='6c5c61b7b714a881'
snowflake_table_prefix='UAT_1'

if [[ "$target_env" == "PRD" ]]
then
    raw_storage_account_name='prdsndatarawyugcupl'
    enriched_storage_account_name='prdsndataenrichedyugcupl'
    instance_pool_id='0724-014750-mote2-pool-u7eworea'
    warehouse_id='07c597619e046afa'
    snowflake_table_prefix='PRD_1'
fi

for job in ./Workflow/create/*.json
do
    echo "processing job '$job'..."
    jobResetPath=`echo $job | sed "s@\/create\/@\/reset\/@g"`
    body=`cat "$job"`
    name=`echo $body | jq '.name' -r`
    jobs=`databricks jobs list --output json`
    id=`echo $jobs | jq --arg name "$name" '.[] | select(.settings.name==$name) | .job_id' -r`

    if [[ -z "$id" ]]; then
        echo "creating job '$name'..."
        sed -i "s/\[raw_storage_account_name\]/$raw_storage_account_name/g" "$job"
        sed -i "s/\[enriched_storage_account_name\]/$enriched_storage_account_name/g" "$job"
        sed -i "s/\[instance_pool_id\]/$instance_pool_id/g" "$job"
        sed -i "s/\[warehouse_id\]/$warehouse_id/g" "$job"
        sed -i "s/\[snowflake_table_prefix\]/$snowflake_table_prefix/g" "$job"
        body=`cat $job`
        databricks jobs create --json "$body"
    else
        echo "updating job '$name' ($id)..."
        sed -i "s/\[raw_storage_account_name\]/$raw_storage_account_name/g" "$jobResetPath"
        sed -i "s/\[enriched_storage_account_name\]/$enriched_storage_account_name/g" "$jobResetPath"
        sed -i "s/\[instance_pool_id\]/$instance_pool_id/g" "$jobResetPath"
        sed -i "s/\[warehouse_id\]/$warehouse_id/g" "$jobResetPath"
        sed -i "s/\[snowflake_table_prefix\]/$snowflake_table_prefix/g" "$jobResetPath"
        sed -i "s/\[job_id\]/$id/g" "$jobResetPath"
        body=`cat $jobResetPath`
        databricks jobs reset --json "$body"
    fi
done