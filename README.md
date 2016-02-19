# son-mano-framework
SONATA's Service Platform MANO Framework


## Folder structure

* `plugins` contains MANO plugin implementations
* `son-mano-base` abstract plugin classes, helpers used by all plugins, ...
* `son-mano-broker` the message broker (start with a Dockerimage containing a default RabbitMQ installation)
* `son-mano-pluginmanager` the plugin manager component
* ... (there will be more)


## TODOs:
* Prepare for CI/CD integration
    * Dockerfiles for each component
    * Tests
* Add automated setup to each component
    * Python: https://docs.python.org/2/distutils/introduction.html
    * Python: http://docs.python-guide.org/en/latest/writing/structure/
     

## Run the PoC code

### Requirements
* Running RabbitMQ broker instance on local machine (localhost)
* Python Pika: `sudo pip install pika`

### Run simple example:
* Terminal 1: Run the plugin manager component
 * `cd cd son-mano-pluginmanager/sonmanopluginmanager/`
 * `python __main__.py`


* Terminal 2: Run the example plugin
 * `cd plugins/son-mano-example-plugin-1/sonmanoexampleplugin1/`
 * `python __main__.py`

What will happen? The example plugin will ...

1. connect to the broker
2. register itself to the plugin manager
3. periodically send heartbeat messages to the plugin manager
4. request a list of active plugins from the plugin manager
5. de-register and stop itself after a few seconds