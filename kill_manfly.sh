pids=$(ps -ef | grep manfly | grep -v grep | awk '{print $2}')
echo ${pids}
for id in ${pids}
    do
        echo $id
        kill $id
        echo "killed ${id}"
    done
# ps -ef | grep grand | grep -v grep | awk '{print $2}'