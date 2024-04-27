import database.mysql_connector
import database.interface
import auth.service
import user.service
from dependency_injector import containers, providers


class Container(containers.DeclarativeContainer):

    config = providers.Configuration()

    db_semaphore = providers.Singleton(
        database.mysql_connector.ConnectionSemaphore,
        host=config.database.host,
        port=config.database.port,
        user=config.database.user,
        password=config.database.password,
        name=config.database.name,
        connection_limit=config.database.connection_limit,
    )

    db_connection = providers.Factory(
        database.mysql_connector.acquire_database_connection,
        connection_semaphore=db_semaphore,
    )

    auth_service = providers.Factory(
        auth.service.AuthorizationService,
        signing=config.authorization.algorithm,
        hash_key=config.authorization.secret_key,
        token_expiration_time=config.authorization.token_expire_time,
    )

    user_service = providers.Factory(
        user.service.UserService,
        auth=auth_service,
    )
