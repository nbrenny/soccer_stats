from datetime import datetime
from datetime import timedelta
from utils.utils import save_to_yaml, get_analysis_dir
import sys
import os
from utils.params import params
import argparse



def parse_args(args):
    parser = argparse.ArgumentParser(description='Create config file for aggregation loop')
    parser.add_argument('-s', '--shift', help='Lookback in integer days', required=False, default=None, type=int)
    args = vars(parser.parse_args(args))
    return args

    
def get_date(shift=None):
    '''shift (optional): integer number of days to lookback'''
    if shift:
        tod = datetime.now()
        d = timedelta(days=shift)
        return (tod - d).strftime('%Y-%m-%d') 
    else:
        return datetime.today().strftime('%Y-%m-%d') 


def create_url(shift=None):
    base_url = params['schedule_url']
    return base_url+get_date(shift=shift)


def create_dict(shift=None):
    dic = {}
    date = get_date(shift=shift)
    dic['url'] = create_url(shift=shift)
    dic['outfile'] = f'{date}.json'
    dic['dir'] = f'{get_analysis_dir()}/url/{date}/'
    dic['wait_time'] = params['default_wait_time']
    return dic


def main():
    args=parse_args(args)
    dic=create_dict(shift=args['shift'])
    save_loc=get_analysis_dir()+'/'+params['create_lists_config']
    save_to_yaml(dic,save_loc,printout=False)
    print(save_loc)


if __name__=="__main__":
    main(sys.argv[1:])