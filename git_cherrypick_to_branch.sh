#!/bin/bash

branch="release/1.0.8"

git checkout $branch &&                     \
git fetch &&                                \
git rebase -v origin/$branch &&             \
#git cherry-pick $1 &&                       \
for commitid in $@; do
    git cherry-pick $commitid
done
git push origin HEAD:refs/for/$branch &&    \
git checkout master
