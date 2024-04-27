from random import randint
import dependencies
import configuration

container = dependencies.Container()

container.config.from_dict(configuration.config)
       
container.wire(modules=[__name__])
