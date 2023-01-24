#!/usr/bin/env python3
# -*- encoding: utf-8 -*-

import sys, uuid


if __name__ == '__main__':

    url = sys.argv[1] if len(sys.argv) > 1 else ''
    print(url)

    print(f"""
uuid1: {uuid.uuid1()}
uuid4: {uuid.uuid4()}
uuid3: {uuid.uuid3(uuid.NAMESPACE_URL, url)}
uuid5: {uuid.uuid5(uuid.NAMESPACE_URL, url)}
""".strip())
