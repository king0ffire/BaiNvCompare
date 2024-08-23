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
        elif line=="":
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
            elif line=="":
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
            elif line=="":
                continue
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
    for numb,line in enumerate(lines):
        line = line.strip()
        logger.debug(f"line has {line}")
        if line.startswith("[") and line.endswith("]"):
            if current_section in opponent_dict:
                for key, value in opponent_dict[current_section].items():
                    logger.debug(f"missing:{current_section},key:{key},value:{value}")
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
        elif line=="":
            continue
        else:
            logger.error(f"Error parsing line {numb}: {line}")
            raise InvaildInputError(numb)
    if current_section in opponent_dict:
        for key, value in opponent_dict[current_section].items():
            logger.debug(f"missing:{current_section},key:{key},value:{value}")
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
) -> list[tuple[str, str, str, enumtypes.DiffType]]:
    # opponent_dict should be a copy
    opponent_dict = copy.deepcopy(opponent_dict)
    diff_list = []

    logger.info("start diff_by_stringindict")
    lines = content.split("\n")
    current_section = None
    for numb,line in enumerate(lines):
        line = line.strip()
        logger.debug(f"line has {line}")
        if line.startswith("[") and line.endswith("]"):
            if current_section in opponent_dict:
                for key, value in opponent_dict[current_section].items():
                    logger.debug(f"missing:{current_section},key:{key},value:{value}")
                    diff_list.append(
                        (current_section, key, value, enumtypes.DiffType.REMOVED)
                    )
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
                    diff_list.append(
                        (current_section, key, value, enumtypes.DiffType.MODIFIED)
                    )
                del opponent_dict[current_section][key]
            else:
                logger.debug(
                    f"insert green: section:{current_section},key:{key},value:{value}"
                )
                diff_list.append(
                    (current_section, key, value, enumtypes.DiffType.ADDED)
                )
        elif line=="":
            continue
        else:
            logger.error(f"Error parsing line {numb}: {line}")
            raise InvaildInputError(numb)
    if current_section in opponent_dict:
        for key, value in opponent_dict[current_section].items():
            logger.debug(f"missing section:{current_section},key:{key},value:{value}")
            diff_list.append((current_section, key, value, enumtypes.DiffType.REMOVED))
        del opponent_dict[current_section]
    current_section = None

    logger.debug(f"missing sections:{opponent_dict}")
    for current_section in opponent_dict:
        logger.debug(f"currrent missing section:[{current_section}]")
        for key, value in opponent_dict[current_section].items():
            diff_list.append((current_section, key, value, enumtypes.DiffType.REMOVED))
    return diff_list


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


def detect_diff_dict_modifications(
    originaldict: dict[str, dict[str, tuple]], editeddict: dict[str, dict[str, str]]
) -> dict[str, dict[str, tuple]]:  # 想要对文件做什么改动
    # dict[section][key]=(value,type)
    logger.debug("start diff_diff_dict")
    logger.debug(f"original={originaldict}")
    logger.debug(f"edited={editeddict}")
    result = {}
    for section in set(editeddict.keys()).union(set(originaldict.keys())):
        result[section] = {}
        if section in originaldict and section in editeddict:
            for key in set(editeddict[section].keys()).union(
                set(originaldict[section].keys())
            ):
                if key in editeddict[section] and key in originaldict[section]:
                    if (
                        originaldict[section][key][1] == enumtypes.DiffType.REMOVED
                    ):  # missing changed to existing
                        result[section][key] = (
                            editeddict[section][key],
                            enumtypes.DiffType.ADDED,
                        )
                        logger.debug(
                            f"current modi: section:{section}, key={key}, newvalue={result[section][key][0]}, type={result[section][key][1]}"
                        )
                    elif originaldict[section][key][0] != editeddict[section][key]:
                        result[section][key] = (
                            editeddict[section][key],
                            enumtypes.DiffType.MODIFIED,
                        )
                        logger.debug(
                            f"current modi: section:{section}, key={key}, newvalue={result[section][key][0]}, type={result[section][key][1]}"
                        )
                elif key in editeddict[section]:
                    result[section][key] = (
                        editeddict[section][key],
                        enumtypes.DiffType.ADDED,
                    )
                    logger.debug(
                        f"current modi: section:{section}, key={key}, newvalue={result[section][key][0]}, type={result[section][key][1]}"
                    )
                elif key in originaldict[section]:
                    if (
                        originaldict[section][key][1] == enumtypes.DiffType.REMOVED
                    ):  # still missing
                        continue
                    result[section][key] = (
                        originaldict[section][key][0],
                        enumtypes.DiffType.REMOVED,
                    )
                    logger.debug(
                        f"current modi: section:{section}, key={key}, newvalue={result[section][key][0]}, type={result[section][key][1]}"
                    )
        elif section in originaldict:
            for key, value in originaldict[section].items():
                result[section][key] = (value, enumtypes.DiffType.REMOVED)
        elif section in editeddict:
            for key, value in editeddict[section].items():
                result[section][key] = (value, enumtypes.DiffType.ADDED)
        if result[section] == {}:  # no change
            del result[section]
    return result
