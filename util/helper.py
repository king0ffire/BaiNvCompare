import copy
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
        else:
            logger.error(f"Error parsing line {numb}: {line}")
            raise InvaildInputError(numb)
    return result


def parse_diffcontent_todict(content) -> dict[str, dict[str]]:
    result = {}
    current_category = None
    result[current_category] = {}
    lines = content.splitlines()
    for numb, line in enumerate(lines):
        line = line.strip()
        if line.startswith("missing"):
            line = line.split(":", 1)[1].strip()
            if line.startswith("[") and line.endswith("]"):
                current_category = line[1:-1]
                result[current_category] = {}
            elif "=" in line:
                pass
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
            else:
                logger.error(f"Error parsing line {numb}: {line}")
                raise InvaildInputError(numb)
    return result

def diff_dict_by_dict(
    content: str, opponent_dict: dict[str, dict[str, str]]
) -> dict[str, dict[str, tuple]]:
    # opponent_dict should be a copy
    opponent_dict = copy.deepcopy(opponent_dict)
    diff_dict = {}

    logger.info("start diff_by_stringindict")
    lines = content.split("\n")
    current_section = None
    diff_dict[current_section] = {}
    for line in lines:
        line = line.strip()
        logger.debug(f"line has {line}")
        if line.startswith("[") and line.endswith("]"):
            if current_section in opponent_dict:
                for key, value in opponent_dict[current_section].items():
                    logger.debug(
                        f"missing:{current_section},key:{key},value:{value}"
                    )
                    diff_dict[current_section][key] = (
                        value,
                        enumtypes.DiffType.REMOVED,
                    )
                del opponent_dict[current_section]
            if diff_dict[current_section] == {}:
                del diff_dict[current_section]
            current_section = line[1:-1]
            logger.debug(f"current section={current_section}")
            diff_dict[current_section] = {}
            logger.debug(f"new section:{current_section}")
        elif "=" in line:
            key, value = line.split("=", 1)
            key = key.strip()
            value = value.strip()
            if (
                current_section in opponent_dict
                and key in opponent_dict[current_section]
            ):
                if value != opponent_dict[current_section][key]:
                    logger.debug(
                        f"insert yellow: section:{current_section},key:{key},value:{value}"
                    )
                    diff_dict[current_section][key] = (
                        value,
                        enumtypes.DiffType.MODIFIED,
                    )
                del opponent_dict[current_section][key]
            else:
                logger.debug(
                    f"insert green: section:{current_section},key:{key},value:{value}"
                )
                diff_dict[current_section][key] = (
                    value,
                    enumtypes.DiffType.ADDED,
                )
    if current_section in opponent_dict:
        for key, value in opponent_dict[current_section].items():
            logger.debug(
                f"missing:{current_section},key:{key},value:{value}"
            )
            diff_dict[current_section][key] = (
                value,
                enumtypes.DiffType.REMOVED,
            )
        del opponent_dict[current_section]
    if diff_dict[current_section] == {}:
        del diff_dict[current_section]
    current_section = None

    logger.debug(f"missing sections:{opponent_dict}")
    for current_section in opponent_dict:
        diff_dict[current_section] = {}
        logger.debug(f"currrent missing section:[{current_section}]")
        for key, value in opponent_dict[current_section].items():
            diff_dict[current_section][key] = (
                value,
                enumtypes.DiffType.REMOVED,
            )
    return diff_dict




def diff_list_by_dict(
    content: str, opponent_dict: dict[str, dict[str, str]]
) -> list[tuple[str,str,str,enumtypes.DiffType]]:
    # opponent_dict should be a copy
    opponent_dict = copy.deepcopy(opponent_dict)
    diff_list = []

    logger.info("start diff_by_stringindict")
    lines = content.split("\n")
    current_section = None
    for line in lines:
        line = line.strip()
        logger.debug(f"line has {line}")
        if line.startswith("[") and line.endswith("]"):
            if current_section  in opponent_dict:
                for key, value in opponent_dict[current_section].items():
                    logger.debug(
                        f"missing:{current_section},key:{key},value:{value}"
                    )
                    diff_list.append((current_section,key,value,enumtypes.DiffType.REMOVED))
                del opponent_dict[current_section]
            current_section = line[1:-1]
            logger.debug(f"new section:{current_section}")
        elif "=" in line:
            key, value = line.split("=", 1)
            key = key.strip()
            value = value.strip()
            if (
                current_section in opponent_dict
                and key in opponent_dict[current_section]
            ):
                if value != opponent_dict[current_section][key]:
                    logger.debug(
                        f"insert yellow: section:{current_section},key:{key},value:{value}"
                    )
                    diff_list.append((current_section,key,value,enumtypes.DiffType.MODIFIED))
                del opponent_dict[current_section][key]
            else:
                logger.debug(
                    f"insert green: section:{current_section},key:{key},value:{value}"
                )
                diff_list.append((current_section,key,value,enumtypes.DiffType.ADDED))
    if current_section in opponent_dict:  
        for key, value in opponent_dict[current_section].items():
            logger.debug(f"missing section:{current_section},key:{key},value:{value}")
            diff_list.append((current_section,key,value,enumtypes.DiffType.REMOVED))
        del opponent_dict[current_section]
    current_section = None

    logger.debug(f"missing sections:{opponent_dict}")
    for current_section in opponent_dict:
        logger.debug(f"currrent missing section:[{current_section}]")
        for key, value in opponent_dict[current_section].items():
            diff_list.append((current_section,key,value,enumtypes.DiffType.REMOVED))
    return diff_list


