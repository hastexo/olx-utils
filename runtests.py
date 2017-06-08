#!/usr/bin/env python
from unittest import main
from coverage import coverage

if __name__ == '__main__':
    c = coverage(source=['olxutils'],
                 auto_data=True)
    c.start()
    main(module="tests",
         verbosity=1)
    c.stop()
