import os
import gql
import csv
import argparse


def get_args():
    p = argparse.ArgumentParser('gitlangstats')

    p.add_argument(
        'mode', metavar='MODE', type=str,
        help="The mode: Either size or langs.")

    p.add_argument(
        '--user', '-u', type=str, nargs='*',
        help='The users or to analyze.')

    p.add_argument(
        '--organization', '-o', type=str, nargs='*',
        help='The organizations or to analyze.')

    p.add_argument(
        '--token', type=str,
        help='The GitHub access token to be used.')

    return p.parse_args()


def main():
    args = get_args()

    users = args.user or []
    orgas = args.organization or []

    if not users and not orgas:
        print('ERROR: At least one user or organization must be given.')
        exit(1)

    ghtoken = args.token or os.environ.get('GITHUB_TOKEN')
    if not ghtoken:
        print('ERROR: GitHub access token musst be passed by GITHUB_TOKEN environment ' +
              'variable or by --token parameter.')
        exit(1)

    c = gql.GQL(authorization="bearer {}".format(ghtoken))

    repos = []
    already_analyzed = []
    langs = {}

    for user in users:
        repos += collect_user(c, user)
    for orga in orgas:
        repos += collect_user(c, orga, isOrga=True)

    if args.mode == "langs":
        for repo in repos:
            repo = repo.get('node')

            owner = repo.get('owner').get('login')
            if owner not in users and owner not in orgas:
                continue

            full_name = "{}/{}".format(owner, repo.get('name'))
            if full_name in already_analyzed:
                continue
            already_analyzed.append(full_name)

            for lang in repo.get('languages').get('edges'):
                name = lang.get('node').get('name')
                size = lang.get('size') / 1024
                if name not in langs:
                    langs[name] = 0
                langs[name] += size

        csvres = csv.csv_from_dict(langs)
        print(csvres)

    elif args.mode == "size":
        repo_sizes = {}
        for repo in repos:
            repo = repo.get('node')
            owner_name = repo.get('owner').get('login')
            repo_name = repo.get('name')
            name = '{}/{}'.format(owner_name, repo_name)
            size = 0

            if owner_name not in users and owner_name not in orgas:
                continue

            if name in already_analyzed:
                continue
            already_analyzed.append(name)

            for lang in repo.get('languages').get('edges'):
                size += lang.get('size') / 1024
            repo_sizes[name] = size

        csvres = csv.csv_from_dict(repo_sizes)
        print(csvres)

    else:
        print('ERROR: Invalid mode.')
        exit(1)

    print('Analyzed {} repositories.'.format(len(already_analyzed)))


def collect_user(c: gql.GQL, user: str, isOrga: bool = False):
    userQuery = 'organization' if isOrga else 'user'
    size = 1
    collected = 0
    n = 100
    repos = []
    after = None
    while collected < size:
        res = c.query_repos_with_langs(user, n, after, excludeForks=True, isOrga=isOrga)
        repoCollector = res.get('data').get(userQuery).get('repositories')
        size = repoCollector.get('totalCount')
        collected += n
        repos += repoCollector.get('edges')
        after = repos[-1].get('cursor')
    return repos


if __name__ == '__main__':
    main()
