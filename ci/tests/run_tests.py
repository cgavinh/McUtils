"""
Tests for things in the McUtils packages
"""

if __name__ == '__main__':

    import os, sys
    test_dir = os.path.dirname(os.path.abspath(__file__))
    root, pkg = os.path.split(test_dir)

    from Peeves.TestUtils import TestManager

    # provide a nice way to automatically pipe print output to stderr so it appears in the regular
    # output area for the unit tests
    TestManager.run(test_root=root, test_pkg=pkg, cmd_line=True)