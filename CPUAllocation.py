#!/usr/bin/env python3.7

import sys
import math

class ResourceAllocation:
    """
    Main class for resource allocation code
    """
    cost_dict = {"us-east":{"large":0.12, "xlarge":0.23, "2xlarge":0.45, "4xlarge":0.774, "8xlarge":1.4, "10xlarge":2.82}, "us-west":{"large":0.14, "2xlarge":0.413, "4xlarge":0.89, "8xlarge":1.3, "10xlarge":2.97}, "asia":{"large":0.11, "xlarge":0.20, "4xlarge":0.67, "8xlarge":1.18}}
    # "us-east":{"large":0.12, "xlarge":0.23, "2xlarge":0.45, "4xlarge":0.774, "8xlarge":1.4, "10xlarge":2.82}, "us-west":{"large":0.14, "2xlarge":0.413, "4xlarge":0.89, "8xlarge":1.3, "10xlarge":2.97}, 
    server_cpu_size = {"large":1, "xlarge":2, "2xlarge":4, "4xlarge":8, "8xlarge":16, "10xlarge":32}
    regions = cost_dict.keys()

    def _final_dict_based_on_cpu(cls, cpus, hours):
        """
        Funtion to calculate based on number of CPUs and number of hours

        :return: List of doctionaries for all regions
        """
        combined_list=[]
        
        for _region in ResourceAllocation.regions:
            region_dict = {}
            _cost_per_region = 0
            _min_server = 2
            _server_list = []
            _rem_cpus = cpus
            _sorted_server_cost = sorted(cls.cost_dict[_region].items(), key=lambda x: x[1], reverse=True)
            _max_cpu_size = cls.server_cpu_size[_sorted_server_cost[0][0]]
            # Calculating max CPU size for which atleast 2 servers can be given
            while _max_cpu_size > 1:
                if cpus//_max_cpu_size >= 4:
                    break
                else:
                    _max_cpu_size /= 2
            _sorted_server_cost = sorted(cls.cost_dict[_region].items(), key=lambda x: x[1], reverse=True)
            sorted_cpu_list = [i for i in sorted(cls.server_cpu_size.items(), key=lambda x: x[1], reverse=True) if i[1] <= _max_cpu_size]
            for k,v in sorted_cpu_list:
                server_name = k if _max_cpu_size == v else "" 
                if server_name in cls.cost_dict[_region].keys():
                    _servers_needed_at_cpu_capacity = (_rem_cpus//2)//_max_cpu_size
                    if _servers_needed_at_cpu_capacity >= _min_server:
                        _server_list.append((server_name,_servers_needed_at_cpu_capacity))
                        _rem_cpus = (_rem_cpus - _rem_cpus//2) + (_rem_cpus//2 - _servers_needed_at_cpu_capacity*_max_cpu_size)
                        _cost_per_region += _servers_needed_at_cpu_capacity*hours*(cls.cost_dict[_region][server_name])
                        _min_server *= 2
                    elif _max_cpu_size*_min_server > _rem_cpus//2 and _max_cpu_size*_min_server <= _rem_cpus:
                        _server_list.append((server_name, _min_server))
                        _rem_cpus -= _max_cpu_size*_min_server
                        _cost_per_region += _min_server*hours*(cls.cost_dict[_region][server_name])
                        _min_server *= 2
                    elif _max_cpu_size*_min_server > _rem_cpus:
                        _server_list.append((server_name, int(math.ceil(_rem_cpus/(_max_cpu_size)))))
                        _cost_per_region += int(math.ceil(_rem_cpus/(_max_cpu_size)))*hours*(cls.cost_dict[_region][server_name])
                        break
                _max_cpu_size = _max_cpu_size//2

            region_dict["total_cost"] = _cost_per_region
            region_dict["region"] = _region
            region_dict["servers"] = _server_list
            combined_list.append(region_dict)
        return combined_list

    def _final_dict_based_on_price(cls, price, hours):
        """
        Funtion to calculate based on price and number of hours

        :return: List of doctionaries for all regions
        """
        combined_list=[]

        for _region in ResourceAllocation.regions:
            region_dict = {}
            _server_list = []
            _cost_per_region = 0
            _min_server = 2
            _sorted_server_cost = [i for i in sorted(cls.cost_dict[_region].items(), key=lambda x: x[1], reverse=True) if price//i[1] >= 4]
            _rem_cost = price
            for k,v in _sorted_server_cost:
                _current_server_size = int((_rem_cost//2)/v)
                if _current_server_size >= _min_server:
                    _server_list.append((k, _current_server_size))
                    _rem_cost = (_rem_cost - _rem_cost//2) + (_rem_cost//2 - v*_current_server_size)
                    _cost_per_region += float(_current_server_size*hours*v)
                    _min_server *= 2
                elif _current_server_size < _min_server and v*_min_server <= _rem_cost:
                    _server_list.append((k, _min_server))
                    _rem_cost -= float(v*_min_server)
                    _cost_per_region += float(v*_min_server*hours)
                    _min_server *= 2
                elif v*_min_server > _rem_cost:
                    _server_list.append((k, int(round(_rem_cost/v))))
                    _cost_per_region += float(round(_rem_cost/v)*hours*v)
                    break

            region_dict["total_cost"] = _cost_per_region
            region_dict["region"] = _region
            region_dict["servers"] = _server_list
            combined_list.append(region_dict)
        return combined_list

    def _final_dict_based_on_price_and_cpus(cls, price, cpus, hours):
        """
        Funtion to calculate based on number of CPUs, price and number of hours

        :return: List of doctionaries for all regions
        """
        combined_list=[]
        
        for _region in ResourceAllocation.regions:
            region_dict = {}
            _server_list = []
            _cost_per_region = 0
            _min_server = 2
            _rem_cpus = cpus
            _rem_cost = price
            _sorted_server_cost = [i for i in sorted(cls.cost_dict[_region].items(), key=lambda x: x[1], reverse=True) if price//i[1] >= 4]
            _max_cpu_size = cls.server_cpu_size[_sorted_server_cost[0][0]]
            while _max_cpu_size > 1:
                if cpus//_max_cpu_size >= 4:
                    break
                else:
                    _max_cpu_size /= 2

            sorted_cpu_list = []
            for i,j in _sorted_server_cost:
                sorted_cpu_list.append((i, cls.server_cpu_size[i]))

            for k,v in sorted_cpu_list:
                server_name = k if _max_cpu_size == v else "" 
                if server_name in cls.cost_dict[_region].keys():
                    _servers_needed_at_cpu_capacity = (_rem_cpus//2)//_max_cpu_size
                    if _servers_needed_at_cpu_capacity >= _min_server and (_rem_cost//2)/_servers_needed_at_cpu_capacity <= v:
                        _server_list.append((server_name,_servers_needed_at_cpu_capacity))
                        _rem_cpus = (_rem_cpus - _rem_cpus//2) + (_rem_cpus//2 - _servers_needed_at_cpu_capacity*_max_cpu_size)
                        _rem_cost = (_rem_cost - _rem_cost//2) + (_rem_cost//2 - v*_servers_needed_at_cpu_capacity)
                        _cost_per_region += _servers_needed_at_cpu_capacity*hours*(cls.cost_dict[_region][server_name])
                        _min_server *= 2
                    elif (_max_cpu_size*_min_server > _rem_cpus//2 and _max_cpu_size*_min_server <= _rem_cpus) or (int((_rem_cost//2)/v) < _min_server and v*_min_server <= _rem_cost):
                        _server_list.append((server_name, _min_server))
                        _rem_cpus -= _max_cpu_size*_min_server
                        _rem_cost -= float(v*_min_server)
                        _cost_per_region += _min_server*hours*(cls.cost_dict[_region][server_name])
                        _min_server *= 2
                    elif _max_cpu_size*_min_server > _rem_cpus or v*_min_server > _rem_cost:
                        _rem_cost -= float(v*_min_server)
                        _servers = int(math.ceil(_rem_cpus/decimal.Decimal(_max_cpu_size)))
                        _server_list.append((server_name,_servers))
                        _cost_per_region += _servers*hours*(cls.cost_dict[_region][server_name])
                        break
                _max_cpu_size = _max_cpu_size//2
            region_dict["total_cost"] = _cost_per_region
            region_dict["region"] = _region
            region_dict["servers"] = _server_list
            combined_list.append(region_dict)
        return combined_list

    def get_costs(cls, hours=1, cpus=None, price=None):
        """
        Function to get right region, with total cost and number of servers needed

        :param hours: Number of hours the servers are needed
        :param cpus: Number of CPUs needed
        :param price: Total price willing to pay
        :return: Dict of regions, will cost and server details 
        """
        if price and not cpus:
            list1 = cls._final_dict_based_on_price(price/hours, hours)
            #print(list1)
            print(sorted(list1, key = lambda i: i['total_cost']))
        
        elif cpus and not price:
            list1 = cls._final_dict_based_on_cpu(cpus, hours)
            print(sorted(list1, key = lambda i: i['total_cost']))

        elif cpus and price:
            list1 = cls._final_dict_based_on_price_and_cpus(price/hours, cpus, hours)
            print(sorted(list1, key = lambda i: i['total_cost']))

        else:
            raise Exception("Price and CPUs together couldn't be 0")


if __name__ == '__main__':
    ra = ResourceAllocation()

    #unit test - 1
    ra.get_costs(hours=10,cpus=110)

    #unit test - 2
    ra.get_costs(hours=10,price=90)

    #unit test - 3
    ra.get_costs(hours=10,cpus=110,price=80)
