#!/usr/bin/env python3
import resource
import traceback


try:
    for attr_name in filter(lambda item: item.startswith('RLIMIT_'), dir(resource)):
        (rlimit_soft, rlimit_hard) = resource.getrlimit(getattr(resource, attr_name))
        print('{}: S:\"{}\" H:\"{}\"'.format(attr_name, rlimit_soft, rlimit_hard))

except OSError:
    traceback.print_exc()
