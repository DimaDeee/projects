"""
    This is a python script to help developers easily see the ASRank of Dedicated Server providers in their terminals.
    Using the ASRank API, this CLI tool outputs the Organization, ASRank, and Cone Size, sorted by asrank or cone size.
    The following organizations: Zenlayer, Equinix, Linode, Ionos, PhoenixNap.
    The highest rank ASN has been selected for each multi-ASNs provider.

    Sample use:
        python asr_rank.py --sort_by cone_size --order ascending
        python asr_rank.py --sort_by asrank --order descending

    Sample Output:
        Organization   ASRank     ConeSize
        -----------------------------------
        Linode           6949          2
        Ionos             725         49
        PhoenixNap        627         60
        Equinix           200        232
        Zenlayer          122        372
"""
import argparse
import requests
import time
import functools


API_URL = 'https://api.asrank.caida.org/v2'
ORGANIZATIONS = ['Zenlayer', 'Equinix', 'Linode', 'Ionos', 'PhoenixNap']
session = requests.Session()


def timer(func):
    """
    This is a timer function that is used to measure the performance of
    another wrapped function.
    :param func: function under inspection
    :return: timed stamps
    """
    @functools.wraps(func)
    def wrapper_timer(*args, **kwargs):
        tic = time.perf_counter()
        value = func(*args, **kwargs)
        toc = time.perf_counter()
        elapsed_time = toc - tic
        print(f"Elapsed time: {elapsed_time:0.4f} seconds")
        return value
    return wrapper_timer


# The decorator can be uncommented if user wants to perform optimizations.
# @timer
def get_highest_rank_asn(organization):
    """
    This function returns the highest ranking ASN for an organization,
    along with the cone size for that ASN.

    :param organization: name of the organization
    :return: highest ranking asn, along with its cone size
    """
    response = session.get(f'{API_URL}/restful/asns?name={organization}')
    asns = response.json()['data']
    conesize = None
    highest_rank = min(node['node']['rank'] for node in asns['asns']['edges'])
    for node in asns['asns']['edges']:
        if node['node']['rank'] == highest_rank:
            conesize = node['node']['cone']['numberAsns']
    return highest_rank, conesize


def sorting_asns(results, metric, order):
    """
    This function takes the sorting criteria from the CLI,
    and returns the sorted asns for the different organizations.
    :param results: the sorted list of asns
    :param metric: the ASRank or Conesize flag identified by the user
    :param order: ascending or descending order as identified by the user
    :return: the sorted list of asns
    """
    order_flag = True if order == 'descending' else False
    index = 1 if metric == 'asrank' else 2
    sorted_results = sorted(results, key=lambda x: x[index], reverse=order_flag)
    return sorted_results


def beautify(results):
    """
    This functions takes the sorted results and presents them in
    a nicer format.
    :param results: sorted list of asns along with their information
    :return: printed results in a nicer format
    """
    print(f"{'Organization':^10s} {'ASRank':^10s} {'ConeSize':^10s}")
    print(f"{'-' * 35}")
    for result in results:
        print(f"{result[0]:10s} {result[1]:10d} {result[2]:10d}")


def main():
    parser = argparse.ArgumentParser(
                        description='Retrieve ASRank and cone size for selected organizations.')
    parser.add_argument('--sort_by', choices=['asrank', 'cone_size'],
                        default='asrank', help='Sort by ASRank or cone size.')
    parser.add_argument("--order", choices=['ascending', 'descending'],
                        default='ascending', help='Sort by ascending or descending order')
    args = parser.parse_args()

    results = []
    for organization in ORGANIZATIONS:
        try:
            asrank, conesize = get_highest_rank_asn(organization)
            results.append((organization, asrank, conesize))
        except ValueError:
            print(f"the following {organization} does not have information!")

    sorted_results = sorting_asns(results, args.sort_by, args.order)
    beautify(sorted_results)


if __name__ == '__main__':
    main()
