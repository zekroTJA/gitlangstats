from typing import Dict


def csv_from_dict(d: Dict) -> str:
    res = ''
    for k, v in d.items():
        res += '{},{}\n'.format(k, v)
    return res
