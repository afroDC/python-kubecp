# Copyright 2019 The Kubernetes Authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Shows the functionality of exec using a Busybox container.
"""

import datetime
import logging
# TODO: Skip requiring tar on the local environment and use python tarfile.
# This will require walking the directory structure
from io import BytesIO
from tempfile import TemporaryFile
import tarfile

from kubernetes import config
from kubernetes.client import Configuration
from kubernetes.client.apis import core_v1_api
from kubernetes.client.rest import ApiException
from kubernetes.stream import stream


def exec_commands(api_instance):
    # TODO: Take the namespace and name from an env variable
    # TODO: Figure out if I can consume the pod using selector
    # and list_namespaced_pod_with_http_info()
    name = 'jenkins-6bd7d77f68-npbt4'
    namespace = 'default'
    resp = None
    date = datetime.datetime.now()
    archive = "~/jenkins_home-{}.tar".format(date.strftime('%Y-%m-%d-%H%M'))

    logging.info("Checking if Jenkins pod exists.")
    try:
        resp = api_instance.read_namespaced_pod(name=name,
                                                namespace=namespace)
        logging.info("{} exists and is addressable.".format(name))
    except ApiException as e:
        if e.status != 404:
            logging.error("Unknown error: %s" % e)
            exit(1)

    # logging.info(
    #     "Starting archiving of /var/jenkins_home/ as {}.".format(archive))
    # Archive
    # TODO: Output the tarball to stdout and save that in memory
    # so I can write that directly to disk
    # exec_command = [
    #     "/bin/sh",
    #     "-c",
    #     "tar --exclude='./caches' \
    #         --exclude='./workspace' \
    #             -cf  {} -C /var/jenkins_home .".format(archive)]

    # exec_command = ["/bin/sh", "-c", "tar --exclude='/var/jenkins_home/caches' --exclude='/var/jenkins_home/workspace' -cf - -C /var/jenkins_home/"]
    exec_command = ["/bin/sh", "-c", "cd /bin && cat cp"]

    logging.info("Archiving directory.")
    # exec_command = ['tar', '-cf', '-', '/bin/touch']

    # with open('test.tar', 'wb') as fw:
    #     while resp.is_open():
    #         resp.update(timeout=1)
    #         if resp.peek_stdout():
    #             out = str.encode(resp.read_stdout())
    #             print(type(out))
    #             fw.write(out)
    resp = stream(api_instance.connect_get_namespaced_pod_exec, name,
                    namespace,
                    command=exec_command,
                    stderr=True, stdin=True,
                    stdout=True, tty=False,
                    _preload_content=True)

    with open('cp', 'w') as fw:
        fw.write(resp)
    logging.info("Saved to disk.")

    # logging.info("Downloading archive.")
    # # Cat the archive to a local file
    # exec_command = [
    #     '/bin/sh',
    #     '-c',
    #     'cat {}'.format(archive)]
    # resp = stream(api_instance.connect_get_namespaced_pod_exec,
    #               name,
    #               namespace,
    #               command=exec_command,
    #               stderr=False, stdin=False,
    #               stdout=True, tty=False)
    # with open('test.tar', 'w') as file:
    #     file.write(resp)

    # Cleanup
    # exec_command = [
    #     '/bin/sh',
    #     '-c',
    #     'rm {}'.format(archive)]
    # resp = stream(api_instance.connect_get_namespaced_pod_exec,
    #               name,
    #               namespace,
    #               command=exec_command,
    #               stderr=False, stdin=False,
    #               stdout=True, tty=False)


def main():
    logging.basicConfig(format='%(levelname)s %(asctime)s %(message)s',
                        datefmt='%m/%d/%Y %I:%M:%S ', level=logging.INFO)

    config.load_kube_config()
    c = Configuration()
    c.assert_hostname = False
    Configuration.set_default(c)
    core_v1 = core_v1_api.CoreV1Api()

    exec_commands(core_v1)


if __name__ == '__main__':
    main()
