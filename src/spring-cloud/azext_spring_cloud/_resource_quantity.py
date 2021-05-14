import re
from knack.util import CLIError
from knack.log import get_logger

logger = get_logger(__name__)

def validate_cpu(cpu):
    if cpu is None:
        return None

    if not re.match(r"^\d+m?$", cpu):
        raise CLIError("CPU quantity should be millis (500m) or integer (1, 2, ...)")

    return cpu


def validate_memory(memory):
    if memory is None:
        return None

    unified = memory
    try:
        # For backward compatibility, to convert integer value to value with Gi unit
        int(memory)
        logger.warning("Memory quantity [--memory] should be specified with unit, such as 512Mi, 1Gi. "
                       "Support for integer quantity will be dropped in future release.")
        unified = memory + "Gi"
    except ValueError:
        pass

    if not re.match(r"^\d+[MG]i$", unified):
        raise CLIError("Memory quantity should be integer followed by unit (Mi/Gi)")

    return unified
