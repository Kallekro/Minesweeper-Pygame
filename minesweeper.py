import sys, subprocess

if __name__ == "__main__":
    try:
        import pygame
    except:
        try:
            import pip
        except:
            sys.exit("Could not import pip package manager. Please install pip for your python distribution.")

        subprocess.check_call(["python", '-m', 'pip', 'install', 'pygame']) # install pkg
        subprocess.check_call(["python", '-m', 'pip', 'install',"--upgrade", 'pygame']) # upgrade pkg

    sys.path.insert(0, 'src')

    import main

    main.main()