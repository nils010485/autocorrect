pyarmor obfuscate --recursive \
    --output dist \
    --exclude .venv* \
    --exclude __pycache__* \
    --exclude .git* \
    --exclude .idea* \
    --exclude *.sh \
    --exact \
    main.py autocorrect_pro/*.py