"""
Copyright (c) 2015 SONATA-NFV
ALL RIGHTS RESERVED.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

Neither the name of the SONATA-NFV [, ANY ADDITIONAL AFFILIATION]
nor the names of its contributors may be used to endorse or promote
products derived from this software without specific prior written
permission.

This work has been performed in the framework of the SONATA project,
funded by the European Commission under Grant number 671517 through
the Horizon 2020 and 5G-PPP programmes. The authors would like to
acknowledge the contributions of their colleagues of the SONATA
partner consortium (www.sonata-nfv.eu).
"""
'''
This is the engine module of SONATA's Specific Manager Registry.
'''

import logging
import os
import docker

logging.basicConfig(level=logging.INFO)
LOG = logging.getLogger("son-mano-specific-manager-registry-engine")
LOG.setLevel(logging.DEBUG)
logging.getLogger("son-mano-base:messaging").setLevel(logging.INFO)


class SMREngine(object):
    def __init__(self):
        self.dc = self.connect()

    def connect(self):
        """
        Connect to a Docker service on which FSMs/SSMs shall be executed.
        The connection information for this service should be specified with the following
        environment variables (example for a docker machine installation):

            export DOCKER_TLS_VERIFY="1"
            export DOCKER_HOST="tcp://192.168.99.100:2376"
            export DOCKER_CERT_PATH="/Users/<user>/.docker/machine/machines/default"
            export DOCKER_MACHINE_NAME="default"

            Docker machine hint: eval $(docker-machine env default) sets all needed ENV variables.

        If DOCKER_HOST is not set, the default local Docker socket will be tried.
        :return: client object
        """
        # lets check if Docker ENV information is set and use local socket as fallback
        if os.environ.get("DOCKER_HOST") is None:
            os.environ["DOCKER_HOST"] = "unix://var/run/docker.sock"
            LOG.warning("ENV variable 'DOCKER_HOST' not set. Using {0} as fallback.".format(os.environ["DOCKER_HOST"]))

        # lets connect to the Docker instance specified in current ENV
        # cf.: http://docker-py.readthedocs.io/en/stable/machine/
        dc = docker.from_env(assert_hostname=False)
        # do a call to ensure that we are connected
        dc.info()
        LOG.info("Connected to Docker host: {0}".format(dc.base_url))
        return dc

    def pull(self, image):#, ssm_name):

        """
        Process of pulling / importing a SSM given as Docker image.

        SSM can be specified like:
        - ssm_uri = "registry.sonata-nfv.eu:5000/my-ssm" -> Docker PULL (opt B)
        or
        - ssm_uri = "file://this/is/a/path/my-ssm.tar" -> Docker LOAD (opt A)
        :return: ssm_image_name
        """
        if "file://" in image:
            # opt A: file based import
            ssm_path = image.replace("file://", "")
            ssm_image_name = os.path.splitext(os.path.basename(ssm_path))[0]
            img = self.dc.images(name=image)
            return self.dc.import_image(ssm_path, repository=ssm_image_name)
            #LOG.debug('{0} pull: succeeded'.format( ssm_name))
        else:
            # opt B: repository pull
            return self.dc.pull(image) # image name and uri are the same
            #LOG.debug('{0} pull: succeeded'.format(ssm_name))

    def start(self, id, image, uuid):

        if 'broker_host' in os.environ:
            broker_host = os.environ['broker_host']
        else:
            broker_host = 'amqp://guest:guest@broker:5672/%2F'

        if 'network_id' in os.environ:
            network_id = os.environ['network_id']
        else:
            network_id = 'sonata-plugins'

        if 'broker_name' in os.environ:
            broker = self.retrieve_broker_name(os.environ['broker_name'])
        else:
            broker = {'name': 'broker', 'alias': 'broker'}


        if "file://" in image:
            image_name = image.replace("file://", "")

        container = self.dc.create_container(image=image,
                                             tty=True,
                                             name=id,
                                             environment={'broker_host':broker_host, 'sf_uuid':uuid})

        networks = self.dc.networks(names= [network_id])

        if len (networks) != 0 and networks[0]['Name'] == network_id:
                self.dc.connect_container_to_network(container=container, net_id=network_id, aliases=[id])
                self.dc.start(container=container.get('Id'))
        else:
            LOG.warning('Docker --link is deprecated. use docker network instead')
            self.dc.start(container=container.get('Id'), links=[(broker['name'], broker['alias'])])




    def stop(self, ssm_name):
        self.dc.kill(ssm_name)

    def rm (self,id, image):
        self.dc.stop(container=id)
        self.dc.remove_container(container= id, force= True)
        self.dc.remove_image(image= image, force= True)

    def retrieve_broker_name(self, broker):
        mid = broker.find(',')
        name = broker[:mid]
        alias = broker[mid+1:]
        return {'name':name, 'alias':alias}

    def rename(self, current_name, new_name):
        self.dc.rename(current_name,new_name)
