import sys
required_modules = ['os', 're', 'pathlib', 'datetime', 'tkinter', 'threading', 
                    'queue', 'traceback', 'time', 'json', 'concurrent.futures',
                    'collections', 'hashlib', 'mmap', 'gc', 'configparser']

missing = []
for module in required_modules:
    try:
        __import__(module)
        print(f"✓ {module}")
    except ImportError:
        print(f"✗ {module} - MISSING")
        missing.append(module)

if missing:
    print(f"\nMissing modules: {missing}")
    if 'tkinter' in missing:
        print("Install tkinter: sudo apt-get install python3-tk")
else:
    print("\n✅ All modules available! Ready to run the application.")
