def main():
    """The main routine."""
    import sys
    args = sys.argv[1:]

    # print("This is the main routine. Args: {}".format(args))
    if len(args) > 0:

        if args[0] == 'update':

            import os
            os.system('pip uninstall asimov_database -y')
            os.system('pip install git+ssh://git@gitlab.com/asimov_trading/database.git')

        elif args[0] == 'update3':
            import os
            os.system('pip3 uninstall asimov_database -y')
            os.system('pip3 install git+ssh://git@gitlab.com/asimov_trading/database.git')
        
        elif '@' in args[0] and 'update' in args[0]:
            import os
            branch = args[0].split("@")[1]
            pip_type = args[0].split("@")[0]

            if len(branch) > 0 and pip_type == "update":
                os.system('pip uninstall asimov_database -y')
                os.system('pip install git+ssh://git@gitlab.com/asimov_trading/database.git')
            else:
                os.system('pip3 uninstall asimov_database -y')
                os.system('pip3 install git+ssh://git@gitlab.com/asimov_trading/database.git@' + branch)


imc = 20

if __name__ == "__main__":
    main()
