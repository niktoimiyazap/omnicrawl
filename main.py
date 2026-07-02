import sys
from omnicrawl.cli import run_cli

def main():
    try:
        run_cli()
    except KeyboardInterrupt:
        print("\n\033[91m[!] OmniCrawl interrupted by user.\033[0m")
        sys.exit(0)

if __name__ == "__main__":
    main()
