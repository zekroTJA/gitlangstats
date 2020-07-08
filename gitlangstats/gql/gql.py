import requests
import json
from typing import Dict


GH_GQL_ENDPOINT = 'https://api.github.com/graphql'


class GQL:
    _headers = {}

    def __init__(self, authorization: str):
        if authorization:
            self._headers['Authorization'] = authorization

    def query(self, query: str) -> Dict:
        return self._do_req(query)

    def query_repos_with_langs(self, username: str, n: int = 100,
                               after: str = None, excludeForks: bool = False,
                               isOrga: bool = False) -> Dict:
        after = (', after: "%s"' % after) if after else ''
        excludeForks = ', isFork: false' if excludeForks else ''
        userQuery = 'organization' if isOrga else 'user'
        query = '''
        query {
          %s(login:"%s") {
            repositories(first: %d%s%s) {
              totalCount,
              edges {
                cursor,
                node {
                  name,
                  owner {
                    login
                  },
                  languages(first: 10) {
                    edges {
                      size,
                      node {
                        name
                      }
                    }
                  }
                }
              }
            }
          }
        }
        '''
        res = self.query(query % (userQuery, username, n, after, excludeForks))
        return res

    def _do_req(self, query: str) -> Dict:
        data = json.dumps({
            'query': query
        })
        r = requests.post(GH_GQL_ENDPOINT, data, headers=self._headers)
        return r.json()
