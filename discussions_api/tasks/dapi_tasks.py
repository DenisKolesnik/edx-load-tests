"""
This file holds the different tasks for the discussion API.
"""
import json
import random
import time

from locust import task

from task_helpers import (
    get_random_comment,
    get_random_thread,
    create_comment,
    create_response,
    post_thread,
)
from discussions_api import DiscussionsApiTasks
import dapi_constants


class GetThreadsTask(DiscussionsApiTasks):
    """
    Tasks for GETs for threads
    """

    @task(2)
    def get_thread(self):
        """
        GET a thread

        /api/discussion/v1/threads/{thread_id}

        Calls made:
        GET_thread
        """
        choice = random.choice(self.thread_id_list)
        url = "/api/discussion/v1/threads/{}".format(choice)
        self.client.get(url=url, verify=False, name="GET_thread")
        self.stop()

    @task(1)
    def get_thread_list(self, return_id=False):
        """
        GET a thread list

        /api/discussion/v1/threads/?course_id={}...

        Calls made:
        GET_thread_list
        """
        get_random_thread(self, verbose=self.verbose)
        self.stop()


class GetCommentsTask(DiscussionsApiTasks):
    """
    Tasks for GETs for comments
    """

    @task
    def get_comment_list(self):
        """
        GET the comment_list

        /api/discussion/v1/comments/?thread_id=...

        Calls made:
        GET_thread_list
        GET_comment_list
        """
        thread = get_random_thread(self, page=1, page_size=10, prioritize_comments=True)
        time.sleep(1)
        get_random_comment(self, thread=thread, verbose=self.verbose)
        self.stop()

    def _get_comment_and_response_count(self, thread_id):
        """
        Returns the comment_count and response_count for a Thread

        This helper method is used when requiring verbose outputs for threads
        that have high comment_counts. For example, a response with
        1000 comment.

        Calls made:
        GET_thread

        Args:
            thread_id (str): Thread to get the comment_count and response_count

        Returns:
            (tuple): (comment_count, response_count)
        """
        print "in get comment and response count"
        url = "/api/discussion/v1/threads/{}/".format(thread_id)
        response = self.client.get(url, verify=False, name="GET_thread")
        if response.status_code == 200:
            response = response.json()
            return response["comment_count"], response["response_count"]
        else:
            print url
            print "{}: {}".format(response.status_code, response.content[0:200])


class PatchThreadsTask(DiscussionsApiTasks):
    """
    Task for PATCH requests for threads

    /api/discussion/v1/threads/{thread_id}

    EditThread uses the staff role to edit while student roles vote, flag,
    and follow.
    """
    def _get_thread_id(self):
        thread = get_random_thread(self, page=1, page_size=10)
        if not thread:
            self.stop()
        time.sleep(1)
        return thread["id"]

    @task(51)
    def edit_thread(self):
        """
        Edit a thread's raw_body

        Calls made:
        GET_thread_list
        PATCH_thread
        """
        new_body_size = random.choice(dapi_constants.BODY.keys())
        data = {"raw_body": dapi_constants.BODY[new_body_size]}
        url = "/api/discussion/v1/threads/{}/".format(self._get_thread_id())

        name = "edit_thread_with_{}".format(new_body_size) if self.verbose else "PATCH_thread"

        response = self.client.patch(
            url,
            data=json.dumps(data),
            verify=False,
            headers=self._headers,
            name=name
        )

        if response.status_code != 200:
            print url
            print "{}: {}".format(response.status_code, response.content[0:200])
        self.stop()

    @task(3)
    def follow_thread(self):
        """
        Follow a thread

        Calls made:
        GET_thread_list
        PATCH_thread
        """
        data = {"following": random.choice(["true", "false"])}
        url = "/api/discussion/v1/threads/{}/".format(self._get_thread_id())

        name = "following_thread" if self.verbose else "PATCH_thread"

        response = self.client.patch(
            url,
            data=json.dumps(data),
            verify=False,
            headers=self._headers,
            name=name
        )

        if response.status_code != 200:
            print url
            print "{}: {}".format(response.status_code, response.content[0:200])

        self.stop()

    @task(1)
    def abuse_flag_thread(self):
        """
        Flag a thread with

        Calls made:
        GET_thread_list
        PATCH_thread
        """
        data = {"abuse_flagged": random.choice(["true", "false"])}
        url = "/api/discussion/v1/threads/{}/".format(random.choice(self._get_thread_id()))

        name = "abuse_flag_thread" if self.verbose else "PATCH_thread"

        response = self.client.patch(
            url,
            data=json.dumps(data),
            verify=False,
            headers=self._headers,
            name=name
        )
        if response.status_code != 200:
            print url
            print "{}: {}".format(response.status_code, response.content[0:200])

        self.stop()

    @task(47)
    def vote_on_thread(self):
        """
        Vote on a thread

        Calls made:
        GET_thread_list
        PATCH_thread
        """
        data = {"voted": random.choice(["true", "false"])}
        url = "/api/discussion/v1/threads/{}/".format(self._get_thread_id())

        name = "vote_on_thread" if self.verbose else "PATCH_thread"

        response = self.client.patch(
            url,
            data=json.dumps(data),
            verify=False,
            headers=self._headers,
            name=name
        )
        if response.status_code != 200:
            print url
            print "{}: {}".format(response.status_code, response.content[0:200])

        self.stop()


class PatchCommentsTask(DiscussionsApiTasks):
    """
    Task for PATCH requests for comments

    /api/discussion/v1/comments/{comment_id}

    A response can only be edited, flagged, and voted on.
    A comment can only be edited and flagged.
    """

    def _comment_id(self):
        thread = get_random_thread(self, page=1, page_size=10, prioritize_comments=True)
        if not thread:
            self.stop()
        comment = get_random_comment(self, thread=thread)
        if not comment:
            self.stop()
        time.sleep(1)
        return comment["id"]

    @task(30)
    def edit_comment(self):
        """
        Edit a comments's raw_body

        Calls made:
        GET_thread_list
        GET_comment_list
        PATCH_comment
        """
        new_body_size = random.choice(dapi_constants.BODY.keys())
        data = {"raw_body": dapi_constants.BODY[new_body_size]}
        url = "/api/discussion/v1/comments/{}/".format(self._comment_id())

        name = "edit_comment_with_{}".format(new_body_size) if self.verbose else "PATCH_comment"

        response = self.client.patch(
            url,
            data=json.dumps(data),
            verify=False,
            headers=self._headers,
            name=name
        )
        if response.status_code != 200:
            print url
            print "{}: {}".format(response.status_code, response.content[0:200])

        self.stop()

    @task(50)
    def vote_on_comment(self):
        """
        Vote on a comment_response

        Calls made:
        GET_thread_list
        GET_comment_list
        PATCH_comment
        """
        data = {"voted": random.choice(["true", "false"])}
        url = "/api/discussion/v1/comments/{}/".format(self._comment_id())

        name = "vote_on_comment" if self.verbose else "PATCH_comment"

        response = self.client.patch(
            url,
            data=json.dumps(data),
            verify=False,
            headers=self._headers,
            name=name
        )

        if response.status_code != 200:
            print url
            print "{}: {}".format(response.status_code, response.content[0:200])

        self.stop()

    @task(4)
    def abuse_flag_comment(self):
        """
        Flag a thread with

        Calls made:
        GET_thread_list
        GET_comment_list
        PATCH_comment
        """
        data = {"abuse_flagged": random.choice(["true", "false"])}
        url = "/api/discussion/v1/comments/{}/".format(self._comment_id())

        name = "abuse_flag_comment" if self.verbose else "PATCH_comment"

        response = self.client.patch(
            url,
            data=json.dumps(data),
            verify=False,
            headers=self._headers,
            name=name
        )
        if response.status_code != 200:
            print url
            print "{}: {}".format(response.status_code, response.content[0:200])

        self.stop()


class PostThreadsTask(DiscussionsApiTasks):
    """
    Task for POSTing thread

    /api/discussion/v1/threads
    """

    @task
    def create_thread(self):
        """
        POST a thread

        Calls made:
        POST_thread
        """
        post_thread(self)
        self.stop()


class PostCommentsTask(DiscussionsApiTasks):
    """
    Task for POSTing comments

    /api/discussion/v1/comments
    """

    @task(2)
    def post_response(self):
        """
        POST a response (1st level comment) and adds the id to the response list

        Calls made:
        GET_thread_list
        POST_comment_response
        """
        thread = get_random_thread(self, page=1, page_size=10)
        if thread:
            create_response(self, thread_id=thread["id"])
        time.sleep(1)
        self.stop()

    @task(1)
    def post_comment(self):
        """
        POST a comment (2nd level comment) to the response list

        Calls made:
        GET_thread_list
        POST_comment_comment
        """
        thread = get_random_thread(self, page=1, page_size=10)
        time.sleep(1)
        if thread:
            response = create_response(self, thread_id=thread["id"])
            time.sleep(1)
            if response:
                create_comment(self, comment_id=response["id"], thread_id=response["thread_id"])
        self.stop()


class DeleteThreadsTask(DiscussionsApiTasks):
    """
    Tasks for DELETE thread

    /api/discussion/v1/threads/{thread_id}
    """

    @task
    def delete_thread(self):
        """
        DELETE a thread

        A thread will be created with POST, then randomly selected with GET,
        and then DELETED.

        Calls made:
        POST_thread
        GET_thread_list
        POST_comments
        """
        post_thread(self)
        time.sleep(1)
        thread = get_random_thread(self, page=1, page_size=10)
        time.sleep(1)
        if not thread:
            self.stop()
        thread_id = thread["id"]

        url = "/api/discussion/v1/threads/{}".format(thread_id)
        response = self.client.delete(
            url,
            verify=False,
            name="DELETE_thread",
            headers=self._delete_headers
        )

        if response.status_code != 204:
            print url
            print "{}: {}".format(response.status_code, response.content[0:200])

        self.stop()


class DeleteCommentsTask(DiscussionsApiTasks):
    """
    DELETEs a comment from a list of responses/comments

    /api/discussion/v1/comments/{comment_id}
    """

    @task
    def delete_response(self):
        """
        DELETE a response

        A response will be created with POST, then a response will be randomly
        selected with GET and then DELETED.

        Calls made:
        POST_comment
        GET_thread_list
        GET_comment_list
        DELETE_response
        """
        thread = get_random_thread(self, page=1, page_size=10)
        time.sleep(1)
        if not thread:
            self.stop()
        create_response(self, thread_id=thread["id"])
        time.sleep(1)
        comment = get_random_comment(self, thread=thread)
        time.sleep(1)
        if not comment:
            self.stop()
        comment_id = comment["id"]

        url = "/api/discussion/v1/comments/{}".format(comment_id)

        self.client.delete(
            url,
            verify=False,
            name="DELETE_response",
            headers=self._headers
        )
        self.stop()

    @task
    def delete_comment(self):
        """
        DELETE a response

        Retrieve threads to retrieve a response. Create a comment and then
        delete the comment. Unlike delete_response, too many calls would be
        required to find a random comment so instead we just delete the newly
        created comment.

        Calls made:
        GET_thread_list
        GET_comment_list
        POST_comment
        DELETE_comment
        """
        thread = get_random_thread(self, page=1, page_size=10)
        if not thread:
            self.stop()
        comment = get_random_comment(self, thread=thread)
        if not comment:
            self.stop()
        comment_id = comment["id"]
        create_comment(self, comment_id=comment_id, thread_id=thread["id"])

        url = "/api/discussion/v1/comments/{}".format(comment_id)

        self.client.delete(
            url,
            verify=False,
            name="DELETE_comment",
            headers=self._headers
        )
        self.stop()
