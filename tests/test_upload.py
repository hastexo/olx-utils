from __future__ import unicode_literals

from olxutils.upload import UploadHelper, UploadHelperException

from tempfile import NamedTemporaryFile, gettempdir

from requests.exceptions import HTTPError

import os
import re

import requests
import requests_mock

try:
    from urllib.parse import urlencode
except ImportError:
    # Python 2
    from urllib import urlencode

from unittest import TestCase


class UploadHelperTestCase(TestCase):

    FAKE_CMS_URL = 'https://cms.pohgha9thaom4ii7.6t8'

    DEMO_COURSE_URL = 'https://github.com/edx/edx-demo-course/archive/open-release/ironwood.1.tar.gz'  # noqa: E501

    def setUp(self):
        # Create a local copy of the edX demo course.
        #
        # Just so we don't download the course archive on every test
        # run, do a HEAD request first, and only follow up with a GET
        # if the local copy doesn't already exist.
        h = requests.head(self.DEMO_COURSE_URL,
                          allow_redirects=True)
        filename = re.findall('filename=(.+)',
                              h.headers.get('content-disposition'))[0]
        tmpfile = os.path.join(gettempdir(),
                               filename)
        if not os.path.exists(tmpfile):
            g = requests.get(self.DEMO_COURSE_URL,
                             allow_redirects=True)
            with open(tmpfile, 'wb') as f:
                f.write(g.content)

        self.local_demo_course_archive = tmpfile

    def test_upload(self):
        token = 'caisieJaiweixieremein2AiRie9ahl2'
        course_id = 'course-v1:example+course+run'

        post_uri = '%s/api/courses/v0/import/%s/' % (self.FAKE_CMS_URL,
                                                     course_id)
        expected_task_id = '01c47bac-89a5-41d0-a968-961dce5212f2'
        with NamedTemporaryFile() as archive:
            helper = UploadHelper(self.FAKE_CMS_URL,
                                  archive.name,
                                  token,
                                  course_id)
            with requests_mock.Mocker() as m:
                m.register_uri('POST',
                               post_uri,
                               json={'task_id': expected_task_id})
                task_id = helper.upload()

            self.assertTrue(m.called)
            self.assertEqual(task_id, expected_task_id)

    def test_course_id_from_archive(self):
        expected_course_id = 'course-v1:edX+DemoX+Demo_Course'
        helper = UploadHelper(self.FAKE_CMS_URL,
                              self.local_demo_course_archive)
        self.assertEqual(helper.course_id,
                         expected_course_id)

    def test_upload_with_autodetected_course_id(self):
        fake_token = 'caisieJaiweixieremein2AiRie9ahl2'
        expected_course_id = 'course-v1:edX+DemoX+Demo_Course'
        expected_task_id = 'fd73c4bb-f1f1-4117-83db-f3cc571eca2a'
        post_uri = '%s/api/courses/v0/import/%s/' % (self.FAKE_CMS_URL,
                                                     expected_course_id)
        helper = UploadHelper(self.FAKE_CMS_URL,
                              self.local_demo_course_archive,
                              fake_token)
        with requests_mock.Mocker() as m:
            m.register_uri('POST',
                           post_uri,
                           json={'task_id': expected_task_id})
            task_id = helper.upload()
        self.assertTrue(m.called)
        self.assertEqual(task_id, expected_task_id)

    def test_fetch_upload_task_state(self):
        fake_token = 'Ahchai7eitheetai6ohHei2shah2ith9'
        expected_course_id = 'course-v1:edX+DemoX+Demo_Course'
        task_id = '07627226-de82-49bb-862e-c855432391cc'
        helper = UploadHelper(self.FAKE_CMS_URL,
                              self.local_demo_course_archive,
                              fake_token)
        get_uri = '%s/api/courses/v0/import/%s/' % (self.FAKE_CMS_URL,
                                                    expected_course_id)
        request_headers = {
            'Authorization': 'JWT %s' % fake_token,
        }
        request_params = {
            'task_id': task_id,
            'filename': self.local_demo_course_archive,
        }
        query = urlencode(request_params)

        with requests_mock.Mocker() as m:
            m.register_uri('GET',
                           '%s?%s' % (get_uri, query),
                           request_headers=request_headers,
                           json={'state': 'Succeeded'})
            task_state = helper.fetch_upload_task_state(task_id)
        self.assertTrue(m.called)
        self.assertEqual(task_state, 'Succeeded')

    def test_fetch_upload_task_state_500(self):
        fake_token = 'Ahchai7eitheetai6ohHei2shah2ith9'
        expected_course_id = 'course-v1:edX+DemoX+Demo_Course'
        task_id = '07627226-de82-49bb-862e-c855432391cc'
        helper = UploadHelper(self.FAKE_CMS_URL,
                              self.local_demo_course_archive,
                              fake_token)
        get_uri = '%s/api/courses/v0/import/%s/' % (self.FAKE_CMS_URL,
                                                    expected_course_id)
        request_headers = {
            'Authorization': 'JWT %s' % fake_token,
        }
        request_params = {
            'task_id': task_id,
            'filename': self.local_demo_course_archive,
        }
        query = urlencode(request_params)

        with requests_mock.Mocker() as m:
            m.register_uri('GET',
                           '%s?%s' % (get_uri, query),
                           request_headers=request_headers,
                           status_code=500)
            with self.assertRaises(HTTPError):
                helper.fetch_upload_task_state(task_id)

    def test_upload_wait_failed(self):
        fake_token = 'caisieJaiweixieremein2AiRie9ahl2'
        expected_course_id = 'course-v1:edX+DemoX+Demo_Course'
        expected_task_id = 'fd73c4bb-f1f1-4117-83db-f3cc571eca2a'
        post_uri = '%s/api/courses/v0/import/%s/' % (self.FAKE_CMS_URL,
                                                     expected_course_id)
        get_uri = post_uri

        request_headers = {
            'Authorization': 'JWT %s' % fake_token,
        }
        request_params = {
            'task_id': expected_task_id,
            'filename': self.local_demo_course_archive,
        }
        query = urlencode(request_params)

        helper = UploadHelper(self.FAKE_CMS_URL,
                              self.local_demo_course_archive,
                              fake_token)
        with requests_mock.Mocker() as m:
            m.register_uri('POST',
                           post_uri,
                           request_headers=request_headers,
                           json={'task_id': expected_task_id})
            m.register_uri('GET',
                           '%s?%s' % (get_uri, query),
                           request_headers=request_headers,
                           json={'state': 'Failed'})
            with self.assertRaises(UploadHelperException):
                helper.upload(wait=True)
