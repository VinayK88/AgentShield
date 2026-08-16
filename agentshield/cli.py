import json
from .report import build_report

def main():
    print(json.dumps(build_report(), indent=2))

if __name__ == "__main__":
    main()
