#!/bin/bash
scripts_dir=${MLS_DIR}/scripts

case $1 in 

    run)
        config=$(python3 ${scripts_dir}/launch_list.py)
        new_dir=`python3 ${scripts_dir}/create_match_list.py --config ${config}`
        #python3 ${scripts_dir}/code.py -i 
        #tail -n 1 "$(echo "${new_dir}")"

    ;;

    run_shift)
        shift=$2
        config=$(python3 ${scripts_dir}/launch_list.py --shift ${shift})

        exec 3>&1  # Open FD 3 as a duplicate of stdout
        out=$(python3 "${scripts_dir}/create_match_list.py" --config "${config}" --wait 10 2>&1 | tee >(cat >&3))
        exec 3>&-  # Close FD 3

        match_list_json=$(echo "$out" | tail -1 | awk '{print $(NF)}')        
        python3 ${scripts_dir}/code.py --config ${config} --wait 20
        #tail -n 1 "$(echo "${new_dir}")"

    ;;

esac