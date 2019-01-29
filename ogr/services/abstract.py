import datetime
from dataclasses import dataclass
from typing import List, Optional, Match, Dict, Any

from ogr.utils import PRStatus, search_in_comments, filter_comments


class GitService:
    def __init__(self):
        pass

    @classmethod
    def create_from_remote_url(cls, remote_url) -> GitService:
        """
        Create instance of service from provided remote_url.

        :param remote_url: str
        :return: GitService
        """
        raise NotImplementedError()

    def get_project(self, **kwargs) -> GitProject:
        """
        Get the GitProject instance

        :param namespace: str
        :param user: str
        :param repo: str
        :return: GitProject
        """
        raise NotImplementedError

    @property
    def user(self) -> GitUser:
        """
        GitUser instance for used token.

        :return: GitUser
        """
        raise NotImplementedError

    def change_token(self, new_token: str) -> None:
        """
        Change an API token.

        Only for this instance and newly created Projects via get_project.
        """
        raise NotImplementedError


class GitProject:
    def __init__(self, repo: str, service: GitService, namespace: str) -> None:
        """
        :param repo: name of the project
        :param service: GitService instance
        :param namespace:   github: username or org name
                            gitlab: username or org name
                            pagure: namespace (e.g. "rpms")
                                for forks: "fork/{username}/{namespace}"
        """
        self.service = service
        self.repo = repo
        self.namespace = namespace

    def is_forked(self) -> bool:
        """
        True, if the project is forked by the user.

        :return: Bool
        """
        raise NotImplementedError()

    @property
    def is_fork(self) -> bool:
        """True if the project is a fork."""
        raise NotImplementedError()

    @property
    def full_repo_name(self) -> str:
        """
        Get repo name with namespace
        e.g. 'rpms/python-docker-py'

        :return: str
        """
        return f"{self.namespace}/{self.repo}"

    def get_branches(self) -> List[str]:
        """
        List of project branches.

        :return: [str]
        """
        raise NotImplementedError()

    def get_description(self) -> str:
        """
        Project description.

        :return: str
        """
        raise NotImplementedError()

    def get_fork(self) -> Optional[GitProject]:
        """
        GitProject instance of the fork if the fork exists, else None

        :return: GitProject or None
        """
        raise NotImplementedError()

    def get_pr_list(self, status: PRStatus = PRStatus.open) -> List[PullRequest]:
        """
        List of pull requests (dics)

        :param status: PRStatus enum
        :return: [PullRequest]
        """
        raise NotImplementedError()

    def get_pr_info(self, pr_id: int) -> PullRequest:
        """
        Get pull request info

        :param pr_id: int
        :return: PullRequest
        """
        raise NotImplementedError()

    def _get_all_pr_comments(self, pr_id: int) -> List[PRComment]:
        """
        Get list of pull-request comments.

        :param pr_id: int
        :return: [PRComment]
        """
        raise NotImplementedError()

    def get_pr_comments(
            self, pr_id, filter_regex: str = None, reverse: bool = False
    ) -> List[PRComment]:
        """
        Get list of pull-request comments.

        :param pr_id: int
        :param filter_regex: filter the comments' content with re.search
        :param reverse: reverse order of comments
        :return: [PRComment]
        """
        all_comments = self._get_all_pr_comments(pr_id=pr_id)
        if reverse:
            all_comments.reverse()
        if filter_regex:
            all_comments = filter_comments(all_comments, filter_regex)
        return all_comments

    def search_in_pr(
            self,
            pr_id: int,
            filter_regex: str,
            reverse: bool = False,
            description: bool = True,
    ) -> Optional[Match[str]]:
        """
        Find match in pull-request description or comments.

        :param description: bool (search in description?)
        :param pr_id: int
        :param filter_regex: filter the comments' content with re.search
        :param reverse: reverse order of comments
        :return: re.Match or None
        """
        all_comments: List[Any] = self.get_pr_comments(pr_id=pr_id, reverse=reverse)
        if description:
            description_content = self.get_pr_info(pr_id).description
            if reverse:
                all_comments.append(description_content)
            else:
                all_comments.insert(0, description_content)

        return search_in_comments(comments=all_comments, filter_regex=filter_regex)

    def pr_create(
            self, title: str, body: str, target_branch: str, source_branch: str
    ) -> PullRequest:
        """
        Create a new pull request.

        :param title: str
        :param body: str
        :param target_branch: str
        :param source_branch: str
        :return: PullRequest
        """
        raise NotImplementedError()

    def pr_comment(
            self,
            pr_id: int,
            body: str,
            commit: str = None,
            filename: str = None,
            row: int = None,
    ) -> PRComment:
        """
        Add new comment to the pull request.

        :param pr_id: int
        :param body: str
        :param commit: str
        :param filename: str
        :param row: int
        :return: PRComment
        """
        raise NotImplementedError()

    def pr_close(self, pr_id: int) -> PullRequest:
        """
        Close the pull-request.

        :param pr_id: int
        :return:  PullRequest
        """
        raise NotImplementedError()

    def pr_merge(self, pr_id: int) -> PullRequest:
        """
        Merge the pull request.

        :param pr_id: int
        :return: PullRequest
        """
        raise NotImplementedError()

    def get_git_urls(self) -> Dict[str, str]:
        raise NotImplementedError()

    def fork_create(self):
        """
        Create a fork of the project.

        :return: GitProject
        """
        raise NotImplementedError()

    def change_token(self, new_token: str):
        """
        Change an API token.

        Only for this instance.
        """
        raise NotImplementedError


class GitUser:
    def __init__(self, service) -> None:
        self.service = service

    def get_username(self) -> str:
        raise NotImplementedError()


@dataclass
class PullRequest:
    title: str
    id: int
    status: PRStatus
    url: str
    description: str
    author: str
    source_branch: str
    target_branch: str
    created: datetime.datetime


@dataclass
class PRComment:
    comment: str
    author: str
    created: datetime.datetime
    edited: datetime.datetime
