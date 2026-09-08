from core.runtime import Runtime


def main():

    runtime = Runtime()

    try:
        runtime.run()

    except KeyboardInterrupt:

        print("\nStopping Runtime...")

        runtime.stop()


if __name__ == "__main__":
    main()