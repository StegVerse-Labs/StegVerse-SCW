git ls-files > filelist.txt
zip -r repo_snapshot.zip $(cat filelist.txt)
