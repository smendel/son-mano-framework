[![Build Status](http://jenkins.sonata-nfv.eu/buildStatus/icon?job=son-mano-framework)](http://jenkins.sonata-nfv.eu/job/son-mano-framework)

# son-mano-framework

SONATA's MANO framework is the core of SONATA's service platform and builds a flexible orchestration system. It consists of a set of loosely coupled components (micro services) that use a message broker to communicate. These components are called MANO plugins and can easily be replaced to customize the orchestration functionalities of the platform.

The main orchestration functionalities are currently implemented in the [service lifecycle management plugin (SLM)](https://github.com/sonata-nfv/son-mano-framework/tree/master/plugins/son-mano-service-lifecycle-management) which receives instantiation requests from the [gatekeeper](https://github.com/sonata-nfv/son-gkeeper) and instructs the [infrastructure adapter](https://github.com/sonata-nfv/son-sp-infrabstract) to deploy a service. The SLM is also responsible to create the service and function records in the [repositories](https://github.com/sonata-nfv/son-catalogue-repos) once a service is instantiated and to inform the [Monitoring Manager](https://github.com/sonata-nfv/son-monitor) which metrics to monitor and on which triggers to send an alarm.

More details about the service platform's architecture are available on SONATA's website:

* [SONATA Architecture](http://sonata-nfv.eu/content/architecture)
* [SONATA Architecture Deliverable 2.2](http://sonata-nfv.eu/sites/default/files/sonata/public/content-files/pages/SONATA_D2.2_Architecture_and_Design.pdf)

## Development

SONATA's MANO framework is organized as micro services. The following micro services are currently implemented:

1. [`son-mano-base`](https://github.com/sonata-nfv/son-mano-framework/tree/master/son-mano-base): not a standalone service but a collection of base classes that are used by the other MANO plugins, also contains a message abstraction layer that encapsulates the RabbitMQ related communication code
2. [`son-mano-pluginmanager`](https://github.com/sonata-nfv/son-mano-framework/tree/master/son-mano-pluginmanager): every MANO plugin registers to this service, the PM provides a CLI to control and monitor active plugins
3. [`plugins/son-mano-service-lifecycle-management`](https://github.com/sonata-nfv/son-mano-framework/tree/master/plugins/son-mano-service-lifecycle-management): main orchestration component, gets service and function descriptors, instructs the infrastructure adapter to start service components in the infrastructure, stores records on services and functions once instantiated, informs Monitoring Manager
4. [`plugins/son-mano-test-plugin`](https://github.com/sonata-nfv/son-mano-framework/tree/master/plugins/son-mano-test-plugin): the most simple implementation of a MANO plugin, used for integration tests and as an example for plugin developers

Each of these components is entirely implemented in Python.

Other MANO plugins (e.g. a placement and scaling plugin) will appear during the course of the project.)

### Building

Each micro service of the framework is executed in its own Docker container. So 'building' the framework becomes building all the containers. The build steps for this are described in a `Dockerfile` that is placed in the folder of each micro service.


1. `docker build -t registry.sonata-nfv.eu:5000/pluginmanager -f son-mano-pluginmanager/Dockerfile .`
2. `docker build -t registry.sonata-nfv.eu:5000/testplugin -f plugins/son-mano-test-plugin/Dockerfile .`
3. `docker build -t registry.sonata-nfv.eu:5000/servicelifecyclemanagement -f plugins/son-mano-service-lifecycle-management/Dockerfile .`
4. `docker build -t registry.sonata-nfv.eu:5000/specificmanagerregistry -f son-mano-specificmanager/son-mano-specific-manager-registry/Dockerfile .`


### Dependencies

Son-mano-framework expects the following environment:

* Python 3.4
* [Docker](https://www.docker.com) >= 1.10 (Apache 2.0)
* [RabbitMQ](https://www.rabbitmq.com) >= 3.5 (Mozilla Public License)
* [MongoDB] (https://www.mongodb.com/community) >= 3.2 (AGPLv3)

Son-mano-framework has the following dependencies:

* [amqpstorm](https://pypi.python.org/pypi/AMQPStorm) >= 1.4 (MIT)
* [argparse](https://pypi.python.org/pypi/argparse) >= 1.4.0 (Python software foundation License)
* [docker-py](https://pypi.python.org/pypi/docker-py) == 1.7.1(Apache 2.0)
* [Flask](https://pypi.python.org/pypi/Flask) >= 0.11 (BSD)
* [flask_restful](https://pypi.python.org/pypi/Flask-RESTful) >= 0.3 (BSD)
* [mongoengine](https://pypi.python.org/pypi/mongoengine) >= 0.10.6 (MIT)
* [pytest-runner](https://pypi.python.org/pypi/pytest-runner) >= 2.8 (MIT)
* [pytest](https://pypi.python.org/pypi/pytest) >= 2.9 (MIT)
* [PyYAML](https://pypi.python.org/pypi/PyYAML) >= 3.11 (MIT)
* [requests](https://pypi.python.org/pypi/requests) >= 2.10 (Apache 2.0)

### Contributing
Contributing to the son-mano-framework is really easy. You must:

1. Clone [this repository](http://github.com/sonata-nfv/son-mano-framework);
2. Work on your proposed changes, preferably through submiting [issues](https://github.com/sonata-nfv/son-mano-framework/issues);
3. Submit a Pull Request;
4. Follow/answer related [issues](https://github.com/sonata-nfv/son-mano-framework/issues) (see Feedback-Chanel, below).

## Installation

If you do not want to execute the components within a Docker container, you can also install them on a normal machine. Each micro service contains a `setup.py` file so that you can follow the standard Python installation procedure by doing:

```
python setup.py install
```

or 


```
python setup.py develop
```

## Usage

To run all components of the MANO framework you have to start their containers. Additionally, a container that runs RabbitMQ and a container that runs MongoDB has to be started.

1. `docker run -d -p 5672:5672 --name broker rabbitmq:3`
2. `docker run -d -p 27017:27017 --name mongo mongo`
3. `docker run -it --rm --link broker:broker --link mongo:mongo --name pluginmanager registry.sonata-nfv.eu:5000/pluginmanager`
4. `docker run -it --rm --link broker:broker --name slm registry.sonata-nfv.eu:5000/servicelifecyclemanagement`
5. `sudo docker run -it --rm --link broker:broker -e broker_name:broker,broker -v '/var/run/docker.sock:/var/run/docker.sock' --name specificmanagerregistry registry.sonata-nfv.eu:5000/specificmanagerregistry`

### Unit tests
#### Container-based unit tests

This is how the Jenkins CI runs the unit tests:

* `./run_tests.sh`

This script builds all required containers, starts them, and executes the unit tests within them.

#### Manual unit tests

Runs unit tests on a local installation.

* NOTICE: The tests need a running RabbitMQ broker to test the messaging subsystem! Without this, tests will fail.
* `cd son-mano-framework`
* `py.test -v son-mano-base/`


## License

Son-mano-framework is published under Apache 2.0 license. Please see the LICENSE file for more details.

## Useful Links

* Paper: [SONATA: Service Programming and Orchestration for Virtualized Software Networks](http://arxiv.org/abs/1605.05850)

---
#### Lead Developers

The following lead developers are responsible for this repository and have admin rights. They can, for example, merge pull requests.

* Sharon Mendel-Brin (https://github.com/mendel) 
* Manuel Peuster (https://github.com/mpeuster)
* Felipe Vicens (https://github.com/felipevicens)
* Thomas Soenen (https://github.com/tsoenen)
* Adrian Rosello (https://github.com/adrian-rosello)
+ Hadi Razzaghi Kouchaksaraei (https://github.com/hadik3r)

#### Feedback-Chanel

* You may use the mailing list [sonata-dev@lists.atosresearch.eu](mailto:sonata-dev@lists.atosresearch.eu)
* [GitHub issues](https://github.com/sonata-nfv/son-mano-framework/issues)
