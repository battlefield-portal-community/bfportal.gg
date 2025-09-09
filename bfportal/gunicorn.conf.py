from dotenv import load_dotenv

load_dotenv()

from bfportal.settings.base import setup_logging  # noqa: E402

setup_logging()

logger_class = "loguricorn.Logger"

bind = "127.0.0.1:8000"
reload = False
timeout = 120
errorlog = "-"
loglevel = "info"
wsgi_app = "bfportal.wsgi:application"
capture_output = True


def when_ready(server):
    """Called just after the master process is initialized."""
    server.log.info("Server is ready. Spawning workers")


def worker_int(worker):
    """Called when a worker receives the INT or QUIT signal."""
    worker.log.info("worker received INT or QUIT signal")

    # get traceback info
    import sys
    import threading
    import traceback

    id2name = {th.ident: th.name for th in threading.enumerate()}
    code = []
    for threadId, stack in sys._current_frames().items():
        code.append("\n# Thread: %s(%d)" % (id2name.get(threadId, ""), threadId))
        for filename, lineno, name, line in traceback.extract_stack(stack):
            code.append('File: "%s", line %d, in %s' % (filename, lineno, name))
            if line:
                code.append("  %s" % (line.strip()))
    worker.log.debug("\n".join(code))


def worker_abort(worker):
    """Called when a worker receives the SIGABRT signal."""
    worker.log.info("worker received SIGABRT signal")


print("Gunicorn config loaded")
