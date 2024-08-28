import logging
from util import enumtypes, helper
import copy
logger = logging.getLogger(__name__)


class ModifyEngine:
    def record_modification(self,original_dict:dict[str,dict[str,str]],current_content:str)->tuple[int,int]:
        original_dict=copy.deepcopy(original_dict)
        keyvaluecount=0
        sectioncount=0
        current_section=None
        lines = current_content.splitlines()
        logger.info("start to record how many key-value and how many sections are changed compared to original file")
        for numb,line in enumerate(lines):
            line = line.strip()
            logger.debug(f"current line: {line}")
            if line.startswith("[") and line.endswith("]"):
                if current_section in original_dict:
                    for key,value in original_dict[current_section].items():
                        keyvaluecount+=1
                        logger.debug(f"{current_section}.{key} is {enumtypes.DiffType.REMOVED}")
                    del original_dict[current_section]
                current_section=line[1:-1]
                if current_section not in original_dict:
                    sectioncount+=1
                    logger.debug(f"new section for file: {current_section}")
            elif "=" in line:
                key, value = line.split("=", 1)
                key=key.strip()
                value=value.strip()
                if current_section in original_dict and key in original_dict[current_section]:
                    if original_dict[current_section][key] == value:
                        pass
                    else:
                        keyvaluecount+=1
                        logger.debug(f"{current_section}.{key} is {enumtypes.DiffType.MODIFIED}")
                    del original_dict[current_section][key]
                else:
                    keyvaluecount+=1
                    logger.debug(f"{current_section}.{key} is {enumtypes.DiffType.ADDED}")
            elif line == "":
                pass
            else:
                logger.error(f"Error parsing line {numb}: {line}")
                raise helper.InvaildInputError(numb)
        if current_section in original_dict:
            for key,value in original_dict[current_section].items():
                keyvaluecount+=1
                logger.debug(f"{current_section}.{key} is {enumtypes.DiffType.REMOVED}")
            del original_dict[current_section]
        for section in original_dict:
            sectioncount+=1
            logger.debug(f"section {section} is {enumtypes.DiffType.REMOVED}")
            for key, value in original_dict[section].items():
                keyvaluecount+=1
                logger.debug(f"{section}.{key} is {enumtypes.DiffType.REMOVED}")

        return keyvaluecount,sectioncount
    
    def process_diff_modification(
        self, original_content, current_diff_str, old_diff_dict,alias=""
    ) -> tuple[str,int]:  # 获得已经修改好的string，该str直接用于保存
        newdiffdict = helper.parse_diffcontent_todict(current_diff_str)
        modification_dict = self.detect_diff_dict_modifications(
            old_diff_dict, newdiffdict
        )
        return self.modify_str_by_dict(original_content, modification_dict)

    def compare_diff_dict_2comparedto1(self, file1_data: dict, file2_data: dict):
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

    def detect_diff_dict_modifications(
        self,
        originaldict: dict[str, dict[str, tuple]],
        editeddict: dict[str, dict[str, str]],
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

    def modify_str_by_dict(self, content: str, modifydict: dict[str, dict[str,tuple]]) -> tuple[str,int]:
        result = []
        numberofmodification=0
        lines = content.splitlines()
        current_section = None
        logger.info(
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
                        numberofmodification+=1
                    del modifydict[current_section]
                else:
                    logger.debug(
                        f"no modification needed for section:{current_section}"
                    )
                current_section = stripedline[1:-1]
                logger.debug(f"next section:{current_section}")
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
                        numberofmodification+=1
                    elif state == enumtypes.DiffType.MODIFIED:
                        result.append(f"{key} = {newvalue}")
                        numberofmodification+=1
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
                numberofmodification+=1
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
                numberofmodification+=1

        return "\n".join(result),numberofmodification
