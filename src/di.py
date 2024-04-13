import dependencies
import os

container = dependencies.Container()
if os.path.isfile("/.deploy"):
    container.config.from_yaml("./deploy_config.yml")
else:
    container.config.from_yaml("./config.yml")
container.wire(modules=[__name__])
