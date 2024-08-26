import os
import logging
from util import enumtypes

logger = logging.getLogger(__name__)


class InvaildInputError(Exception):
    pass


def split_filename(filename):
    base_name = os.path.basename(filename)
    root, ext = os.path.splitext(base_name)
    if ext == ".gz" and root.endswith(".tar"):
        root, ext2 = os.path.splitext(root)
        ext = ext2 + ext
    return root, ext


def parse_string(content) -> dict[str, dict[str, str]]:
    result = {}
    current_category = None
    result[current_category] = {}
    lines = content.splitlines()
    for numb, line in enumerate(lines):
        line = line.strip()
        if line.startswith("[") and line.endswith("]"):
            current_category = line[1:-1]
            result[current_category] = {}
        elif "=" in line:
            key, value = line.split("=", 1)
            result[current_category][key.strip()] = value.strip()
        elif line == "":
            continue
        else:
            logger.error(f"Error parsing line {numb}: {line}")
            raise InvaildInputError(numb)
    return result


def parse_diffcontent_todict(content) -> dict[str, dict[str, str]]:
    result = {}
    current_category = None
    result[current_category] = {}
    lines = content.splitlines()
    for numb, line in enumerate(lines):
        line = line.strip()
        if line.startswith("missing"):
            line = line.split(":", 1)[1].strip()
            if line.startswith("[") and line.endswith("]"):
                if result[current_category] == {}:
                    del result[current_category]
                current_category = line[1:-1]
                result[current_category] = {}
            elif "=" in line:
                pass
            elif line == "":
                continue
            else:
                logger.error(f"Error parsing line {numb}: {line}")
                raise InvaildInputError(numb)
        else:
            if line.startswith("[") and line.endswith("]"):
                current_category = line[1:-1]
                result[current_category] = {}
            elif "=" in line:
                key, value = line.split("=", 1)
                result[current_category][key.strip()] = value.strip()
            elif line == "":
                continue
            else:
                logger.error(f"Error parsing line {numb}: {line}")
                raise InvaildInputError(numb)
    return result


def diff_diff_dict(
    originaldict: dict[str, dict[str, tuple]], editeddict: dict[str, dict[str, str]]
) -> dict[str, dict[str, tuple]]:  # 想要对文件做什么改动
    # dict[section][key]=(value,type)
    logger.debug("start diff_diff_dict")
    logger.debug(f"original={originaldict}")
    logger.debug(f"edited={editeddict}")
    result = {}
    for section, keys in editeddict.items():
        result[section] = {}
        if section in originaldict:
            for key, value in keys.items():
                if key in originaldict[section]:
                    if originaldict[section][key][1] == enumtypes.DiffType.REMOVED:
                        result[section][key] = (value, enumtypes.DiffType.ADD)
                        logger.debug(
                            f"current modi: section:{section}, key={key}, newvalue={value}, type={result[section][key][1]}"
                        )
                    elif originaldict[section][key][0] != editeddict[section][key]:
                        result[section][key] = (value, enumtypes.DiffType.MODIFIED)
                        logger.debug(
                            f"current modi: section:{section}, key={key}, newvalue={value}, type={result[section][key][1]}"
                        )
                    del originaldict[section][key]
                else:
                    result[section][key] = (value, enumtypes.DiffType.ADDED)
                    logger.debug(
                        f"current modi: section:{section}, key={key}, newvalue={value}, type={result[section][key][1]}"
                    )

            for key, status in originaldict[section].items():
                value, state = status
                if state == enumtypes.DiffType.REMOVED:
                    continue
                result[section][key] = (value, enumtypes.DiffType.REMOVED)
                logger.debug(
                    f"current modi: section:{section}, key={key}, newvalue={value}, type={result[section][key][1]}"
                )
            del originaldict[section]
        else:
            # new section and new config
            for key, value in keys.items():
                result[section][key] = (value, enumtypes.DiffType.ADDED)
                logger.debug(
                    f"current modi: section:{section}, key={key}, newvalue={value}, type={result[section][key][1]}"
                )
    for section, keys in originaldict.items():
        result[section] = {}
        for key, status in keys.items():
            value, _ = status
            result[section][key] = (value, enumtypes.DiffType.REMOVED)
            logger.debug(
                f"current modi: section:{section}, key={key}, newvalue={value}, type={result[section][key][1]}"
            )
    logger.debug(f"this should be empty:{originaldict}")
    return result
