from git import Repo
import os
import sys


def list_git_repo(path: str) -> list:
    """
    :path : file_path
    """
    return __list_git_repo(path)


def __list_git_repo(path: str) -> list:
    """
    :path : file_path
    """
    ret = []
    files = os.listdir(path)
    for file in files:
        file_path = os.path.join(path, file)
        if os.path.isdir(file_path):
            if __is_git_repo(file_path):
                ret.append(file_path)
            else:
                ret.extend(__list_git_repo(file_path))
    return ret


def dirty(path: str):
    dirty_repos = __list_dirty_repo(path)
    for dirty_repo in dirty_repos:
        repo = Repo(dirty_repo)
        changed_files = [item.a_path for item in repo.index.diff(None)]
        print(dirty_repo)
        print(changed_files)
        print(repo.untracked_files)
        print('---------')


def push(path: str, msg):
    dirty_repos = __list_dirty_repo(path)
    for dirty_repo in dirty_repos:
        repo = Repo(dirty_repo)
        changed_files = [item.a_path for item in repo.index.diff(None)]
        repo.index.add(changed_files)
        repo.index.commit(msg)
        repo.remote().fetch()
        repo.remote().pull()
        repo.remote().push(repo.active_branch())


def __list_dirty_repo(path: str):
    git_repos = list_git_repo(path)
    dirty_repos = []
    for git_repo in git_repos:
        repo = Repo(git_repo)
        if repo.is_dirty():
            dirty_repos.append(git_repo)
    return dirty_repos


def __is_git_repo(dir_path: str) -> bool:
    files = os.listdir(dir_path)
    for file in files:
        if file == r'.git':
            return True
    return False


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print('请输入参数')
        sys.exit(0)
    command = sys.argv[1]
    path = sys.argv[2]
    if command == 'push':
        if len(sys.argv) < 4:
            print('请输入commit message')
            sys.exit(0)
        msg = sys.argv[4]
        push(path, msg)
    else:
        dirty(path)
