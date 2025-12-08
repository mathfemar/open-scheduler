import sys, traceback

try:
    import backend.app
    print("import ok")
except Exception:
    traceback.print_exc()
    sys.exit(1)
