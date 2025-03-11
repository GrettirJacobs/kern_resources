# Restore the files to their original location
git checkout 439f6ff -- kern_resources/.gitignore kern_resources/README.md

# Move them to the current directory if desired
Move-Item kern_resources/.gitignore .gitignore.parent
Move-Item kern_resources/README.md README.md.parent

# Clean up the temporary directory
Remove-Item -Recurse -Force kern_resources