#!/usr/bin/env python3
from ui_t.ui_main_ import LoudApp
import sys

def main():
    try:
        app=LoudApp()
        app.run()
    except KeyboardInterrupt:
        sys.exit(0)

if __name__ == "__main__":
    main()
