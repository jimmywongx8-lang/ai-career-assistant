# Create empty __init__.py file
touch modules/__init__.py

# Or if on Windows PowerShell:
New-Item -Path "modules/__init__.py" -ItemType File

# Or via Git:
git add modules/__init__.py
git commit -m "Add __init__.py to modules folder"
git push