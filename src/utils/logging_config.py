import logging
from logging.handlers import TimedRotatingFileHandler

from colorlog import ColoredFormatter


def setup_logging():
    """
    Configuração do sistema de logs.
    """
    from .resource_finder import get_project_root

    # Usando resource_finder para obter diretório de logs
    project_root = get_project_root()
    log_dir = project_root / "logs"
    log_dir.mkdir(exist_ok=True)

    # Caminho do arquivo de log
    log_file = log_dir / "app.log"

    # Configurar logger raiz
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)

    # Limpar handlers existentes
    if root_logger.handlers:
        root_logger.handlers.clear()

    # Handler para console
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)

    # Handler para arquivo com rotação diária
    file_handler = TimedRotatingFileHandler(
        log_file,
        when="midnight",
        interval=1,
        backupCount=30,
        encoding="utf-8",
    )
    file_handler.setLevel(logging.INFO)
    file_handler.suffix = "%Y-%m-%d.log"

    # Formato para arquivo
    formatter = logging.Formatter(
        "%(asctime)s[%(name)s] - %(levelname)s - %(message)s - %(threadName)s"
    )

    # Formato colorido para console
    color_formatter = ColoredFormatter(
        "%(green)s%(asctime)s%(reset)s[%(blue)s%(name)s%(reset)s] - "
        "%(log_color)s%(levelname)s%(reset)s - %(green)s%(message)s%(reset)s - "
        "%(cyan)s%(threadName)s%(reset)s",
        log_colors={
            "DEBUG": "cyan",
            "INFO": "white",
            "WARNING": "yellow",
            "ERROR": "red",
            "CRITICAL": "red,bg_white",
        },
        secondary_log_colors={"asctime": {"green": "green"}, "name": {"blue": "blue"}},
    )
    console_handler.setFormatter(color_formatter)
    file_handler.setFormatter(formatter)

    # Adicionar handlers ao logger raiz
    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)

    # Exibir informação de inicialização
    logging.info("Log inicializado - Arquivo de log: %s", log_file)

    return log_file


def get_logger(name):
    """Obter logger configurado para um módulo.

    Args:
        name: Nome do módulo (tipicamente __name__)

    Returns:
        logging.Logger: Logger configurado para o módulo

    Example:
        logger = get_logger(__name__)
        logger.info("Informação")
        logger.error_exc("Erro: %s", error_msg)
    """
    logger = logging.getLogger(name)

    def log_error_with_exc(msg, *args, **kwargs):
        """
        Registrar erro com informações de exceção automaticamente.
        """
        kwargs["exc_info"] = True
        logger.error(msg, *args, **kwargs)

    # Anexar método customizado para logging com exceção
    logger.error_exc = log_error_with_exc

    return logger
