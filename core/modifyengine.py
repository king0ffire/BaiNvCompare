import logging
from util import enumtypes, helper


logger = logging.getLogger(__name__)


class ModifyEngine:
    def process_diff_modification(
        self, original_content, current_diff_str, old_diff_dict
    ) -> str:  # 获得已经修改好的string，该str直接用于保存
        newdiffdict = helper.parse_diffcontent_todict(current_diff_str)
        modification_dict = helper.detect_diff_dict_modifications(
            old_diff_dict, newdiffdict
        )
        return modify_str_by_dict(original_content, modification_dict)

    def compare_diff_dict_2comparedto1(file1_data: dict, file2_data: dict):
        result = {}
        logger.info("start compare diff by dict")
        # Compare sections and keys
        for section in set(file1_data.keys()).union(file2_data.keys()):
            result[section] = {}
            if section in file1_data and section in file2_data:
                for key in set(file1_data[section].keys()).union(
                    file2_data[section].keys()
                ):
                    if key in file1_data[section] and key in file2_data[section]:
                        if file1_data[section][key] == file2_data[section][key]:
                            pass
                            # result[section][key] = (enumerate.DiffType.SAME, file1_data[section][key])
                        else:
                            result[section][key] = (
                                enumtypes.DiffType.MODIFIED,
                                file1_data[section][key],
                                file2_data[section][key],
                            )
                    elif key in file1_data[section]:
                        result[section][key] = (
                            enumtypes.DiffType.REMOVED,
                            file1_data[section][key],
                        )
                    elif key in file2_data[section]:
                        result[section][key] = (
                            enumtypes.DiffType.ADDED,
                            file2_data[section][key],
                        )
            elif section in file1_data:
                for key in file1_data[section]:
                    result[section][key] = (
                        enumtypes.DiffType.REMOVED,
                        file1_data[section][key],
                    )
            elif section in file2_data:
                for key in file2_data[section]:
                    result[section][key] = (
                        enumtypes.DiffType.ADDED,
                        file2_data[section][key],
                    )
        # logger.debug(result)
        return result


def modify_str_by_dict(content: str, modifydict: dict[str, dict[str]]) -> str:
    result = []
    lines = content.splitlines()
    current_section = None
    logger.debug(
        f"start to construct sync file, modification needed to be made:{modifydict}"
    )
    for line in lines:
        stripedline = line.strip()
        
        logger.debug(f"line has {stripedline}")
        if stripedline.startswith("[") and stripedline.endswith("]"):
            if current_section in modifydict:
                for key, status in modifydict[current_section].items():
                    newvalue, state = status
                    logger.debug(
                        f"adding new config section:{current_section},key:{key},value:{newvalue}"
                    )
                    result.append(f"{key} = {newvalue}")
                del modifydict[current_section]
            else:
                logger.debug(f"no modification needed for section:{current_section}")
            current_section = stripedline[1:-1]
            logger.debug(f"new section:{current_section}")
            result.append(f"{line}")
        elif "=" in stripedline:
            key, value = stripedline.split("=", 1)
            key = key.strip()
            value = value.strip()
            if current_section in modifydict and key in modifydict[current_section]:
                newvalue, state = modifydict[current_section][key]
                if state == enumtypes.DiffType.ADDED:
                    logger.error(
                        f"unexpected add:section={current_section},key={key},value={newvalue}"
                    )
                elif state == enumtypes.DiffType.REMOVED:
                    logger.debug(
                        f"file removed :section={current_section},key={key},value={newvalue}"
                    )
                elif state == enumtypes.DiffType.MODIFIED:
                    result.append(f"{key} = {newvalue}")
                    logger.debug(
                        f"file modified :section={current_section},key={key},value={newvalue}"
                    )
                else:
                    logger.critical(f"unexpacted type")
                del modifydict[current_section][key]
            else:  # config项没有任何修改
                result.append(line)
    if current_section in modifydict:
        for key, status in modifydict[current_section].items():
            newvalue, state = status
            logger.debug(
                f"adding new config section:{current_section},key:{key},value:{newvalue}"
            )
            result.append(f"{key} = {newvalue}")
        del modifydict[current_section]
    current_section = None

    for missing_section, status in modifydict.items():
        result.append(f"[{missing_section}]")
        logger.debug(f"currrent missing section:[{missing_section}]")
        for key, status in status.items():
            newvalue, state = status
            logger.debug(
                f"adding new config section:{current_section},key:{key},value:{newvalue}"
            )
            result.append(f"{key} = {newvalue}")

    return "\n".join(result)
