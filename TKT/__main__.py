try:
    from TKT.cli import main
except ImportError:
    from cli import main  # type: ignore

main()
