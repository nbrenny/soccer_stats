from datetime import datetime
from utils.utils import save_to_yaml, get_analysis_dir
import sys
import os
from utils.params import params


def get_date():
    return datetime.today().strftime('%Y-%m-%d')


def create_url():
    base_url = params['schedule_url']
    return base_url+get_date()


def create_dict():
    dic = {}
    dic['url'] = create_url()
    dic['outfile'] = f'{get_date()}.json'
    dic['dir'] = f'{get_analysis_dir()}/url/{get_date()}/'
    dic['wait_time'] = 1
    return dic


def main():
    dic=create_dict()
    save_loc=get_analysis_dir()+'/'+params['create_lists_config']
    save_to_yaml(dic,get_analysis_dir()+'/'+params['create_lists_config'],printout=False)
    print(save_loc)


if __name__=="__main__":
    main()