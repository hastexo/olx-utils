from __future__ import unicode_literals

import logging
import re
import tarfile
import time

import requests
import xmltodict


class UploadHelperException(Exception):
    pass


class UploadHelper(object):

    UPLOAD_URL_FORMAT = '%s/api/courses/v0/import/%s/'

    def __init__(self, url, archive, token=None, course_id=None):
        self.url = url
        self.archive = archive
        self.token = token
        if course_id:
            self.course_id = course_id
        else:
            self.course_id = self.course_id_from_archive()

        self.upload_url = self.UPLOAD_URL_FORMAT % (self.url,
                                                    self.course_id)

    def course_id_from_archive(self):
        # Detect course ID from course.xml
        #
        # The only format currently supported by Open edX Studio
        # is gztar, i.e. a gzip-compressed tarball. If that ever
        # changes, we need to more cleverly detect the format here.
        mode = 'r:gz'
        try:
            with tarfile.open(self.archive, mode) as tf:
                # The course.xml file must be in the top-level
                # directory of the archive. That directory can be
                # arbitrarily named. Since we can't apply a shell glob
                # like "*/course.xml" to the items of a list, we use a
                # regex instead.
                match_members = [n for n in tf.getnames()
                                 if re.match('[^/]+/course\\.xml$', n)]
                if len(match_members) == 0:
                    msg = ("Can't find course.xml "
                           "in root directory "
                           "of archive %s") % self.archive
                    raise UploadHelperException(msg)
                if len(match_members) > 1:
                    # This should never happen, except in the case of
                    # a tarball that has both course.xml and
                    # COURSE.xml in its root directory, was created on
                    # a filesystem that is case-sensitive, and is now
                    # being opened on a case-insensitive filesystem.
                    msg = ("Found more than one course.xml "
                           "in root directory "
                           "of archive %s") % self.archive
                    raise UploadHelperException(msg)

                coursexml = tf.extractfile(match_members[0])
                course = xmltodict.parse(coursexml.read())['course']
                course_id = 'course-v1:%s+%s+%s' % (course['@org'],
                                                    course['@course'],
                                                    course['@url_name'])
        except Exception as e:
            msg = "Unable to determine course ID from archive: %s" % e
            raise UploadHelperException(msg)

        return course_id

    def upload(self, wait=False):
        request_headers = {
            'Authorization': 'JWT %s' % self.token,
        }
        request_files = {
            'course_data': (self.archive,
                            open(self.archive, 'rb')),
        }
        r = requests.post(self.upload_url,
                          files=request_files,
                          headers=request_headers)

        logging.debug("Request took %s to complete" % r.elapsed)
        # Raise an HTTPError if we didn't get an OK response
        r.raise_for_status()

        json_result = r.json()
        logging.debug("Request returned JSON result %s" % json_result)

        self.task_id = json_result['task_id']

        if wait:
            while True:
                task_state = self.fetch_upload_task_state()
                if task_state == 'Succeeded':
                    logging.info('Course upload to %s '
                                 'from %s succeeded.' % (self.course_id,
                                                         self.archive))
                    break
                elif task_state == 'Failed':
                    msg = ('Course upload to %s '
                           'from %s failed') % (self.course_id,
                                                self.archive)
                    raise UploadHelperException(msg)
                else:
                    time.sleep(1)
        else:
            return self.task_id

    def fetch_upload_task_state(self, task_id=None):
        request_headers = {
            'Authorization': 'JWT %s' % self.token,
        }
        request_params = {
            'task_id': task_id or self.task_id,
            'filename': self.archive,
        }
        r = requests.get(self.upload_url,
                         params=request_params,
                         headers=request_headers)
        logging.debug("Request took %s to complete" % r.elapsed)
        # Raise an HTTPError if we didn't get an OK response
        r.raise_for_status()

        json_result = r.json()
        logging.debug("Request returned JSON result %s" % json_result)

        return json_result['state']
