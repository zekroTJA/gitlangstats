import os
import gql
import csv


def main():
    ghtoken = os.environ.get('GITHUB_TOKEN')
    if not ghtoken:
        raise 'GITHUB_TOKEN environment variable is not specified'
    c = gql.GQL(authorization="bearer {}".format(ghtoken))

    repos = []
    repos += collect_user(c, 'zekroTJA')
    repos += collect_user(c, 'myrunes', isOrga=True)

    langs = {}
    for repo in repos:
        repo = repo.get('node')
        for lang in repo.get('languages').get('edges'):
            name = lang.get('node').get('name')
            size = lang.get('size') / 1024
            if name not in langs:
                langs[name] = 0
            langs[name] += size

    csvres = csv.csv_from_dict(langs)
    print(csvres)

    repo_sizes = {}
    for repo in repos:
        repo = repo.get('node')
        owner_name = repo.get('owner').get('login')
        repo_name = repo.get('name')
        name = '{}/{}'.format(owner_name, repo_name)
        size = 0
        for lang in repo.get('languages').get('edges'):
            size += lang.get('size') / 1024
        repo_sizes[name] = size

    csvres = csv.csv_from_dict(repo_sizes)
    print(csvres)


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
