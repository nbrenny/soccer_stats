scripts_dir=${MLS_DIR}/scripts

case $1 in 

    run)
        config=$(python3 ${scripts_dir}/launch_list.py)
        new_dir=`python3 ${scripts_dir}/create_match_list.py --config ${config}`
        #python3 ${scripts_dir}/code.py -i 
        #tail -n 1 "$(echo "${new_dir}")"

    ;;

esac