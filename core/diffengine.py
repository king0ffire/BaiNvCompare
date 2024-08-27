from PyQt6.QtGui import QTextCharFormat, QColor, QTextCursor
import logging
from util import helper
import util.enumtypes as enumtypes
from typing import Callable
import copy

logger = logging.getLogger(__name__)


class DiffEngine:
    def output_diff_dict(
        self,
        diff_dict: dict[str, dict[str, tuple]],
        insert_handle: Callable[[str, QTextCharFormat], None],
    )->int:
        numberofmodification=0
        green_format = QTextCharFormat()
        green_format.setBackground(QColor("green"))
        yellow_format = QTextCharFormat()
        yellow_format.setBackground(QColor("yellow"))
        red_format = QTextCharFormat()
        red_format.setBackground(QColor("red"))
        normal_format = QTextCharFormat()
        logger.info(f"output by using dict: orderless")
        for section, configs in diff_dict.items():
            logger.debug(f"section:{section}")
            insert_handle(f"[{section}]\n", normal_format)
            for key, status in configs.items():
                numberofmodification+=1
                if status[1] == enumtypes.DiffType.ADDED:
                    logger.debug(
                        f"insert green: section:{section},key:{key},value:{status[0]}"
                    )
                    insert_handle(f"{key} = {status[0]}\n", green_format)
                elif status[1] == enumtypes.DiffType.REMOVED:
                    logger.debug(
                        f"insert red: section:{section},key:{key},value:{status[0]}"
                    )
                    insert_handle(f"missing:{key} = {status[0]}\n", red_format)
                elif status[1] == enumtypes.DiffType.MODIFIED:
                    logger.debug(
                        f"insert yellow: section:{section},key:{key},value:{status[0]}"
                    )
                    insert_handle(f"{key} = {status[0]}\n", yellow_format)
        return numberofmodification

    def diff_dict_by_dict(self,
        content: str, opponent_dict: dict[str, dict[str, str]],alias=""
    ) -> dict[str, dict[str, tuple]]:
        # opponent_dict should be a copy
        opponent_dict = copy.deepcopy(opponent_dict)
        diff_dict = {}

        logger.info(f"start {alias} diff_by_stringindict")
        lines = content.split("\n")
        current_section = None
        diff_dict[current_section] = {}
        for numb, line in enumerate(lines):
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
            elif line == "":
                continue
            else:
                logger.error(f"Error parsing line {numb}: {line}")
                raise helper.InvaildInputError(numb)
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
        for numb, line in enumerate(lines):
            line = line.strip()
            logger.debug(f"line has {line}")
            if line.startswith("[") and line.endswith("]"):
                if current_section in opponent_dict:
                    for key, value in opponent_dict[current_section].items():
                        logger.debug(
                            f"missing:{current_section},key:{key},value:{value}"
                        )
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
            elif line == "":
                continue
            else:
                logger.error(f"Error parsing line {numb}: {line}")
                raise helper.InvaildInputError(numb)
        if current_section in opponent_dict:
            for key, value in opponent_dict[current_section].items():
                logger.debug(
                    f"missing section:{current_section},key:{key},value:{value}"
                )
                diff_list.append(
                    (current_section, key, value, enumtypes.DiffType.REMOVED)
                )
            del opponent_dict[current_section]
        current_section = None

        logger.debug(f"missing sections:{opponent_dict}")
        for current_section in opponent_dict:
            logger.debug(f"currrent missing section:[{current_section}]")
            for key, value in opponent_dict[current_section].items():
                diff_list.append(
                    (current_section, key, value, enumtypes.DiffType.REMOVED)
                )
        return diff_list

    """
    def output_diff_by_stringindict(
        textedit: DrapDropTextEdit, opponent_dict: dict[str, dict[str, str]]
    ):
        textedit.editbyuser = False
        textedit.clear()
        textedit.diff_dict = {}
        green_format = QTextCharFormat()
        green_format.setBackground(QColor("green"))
        yellow_format = QTextCharFormat()
        yellow_format.setBackground(QColor("yellow"))
        red_format = QTextCharFormat()
        red_format.setBackground(QColor("red"))
        normal_format = QTextCharFormat()

        logger.info("start compare diff by string")
        lines = textedit.originalcontent.split("\n")
        current_section = None
        textedit.diff_dict[current_section] = {}
        sectionhasdifference = False
        cursor = textedit.textCursor()
        for line in lines:
            line = line.strip()
            logger.debug(f"line has {line}; section has value:{sectionhasdifference}")
            if line.startswith("[") and line.endswith("]"):
                if current_section in opponent_dict:
                    for key, value in opponent_dict[current_section].items():
                        logger.debug(
                            f"missing section:{current_section},key:{key},value:{value}"
                        )
                        cursor.insertText(f"missing:{key} = {value}\n", red_format)
                        textedit.diff_dict[current_section][key] = (
                            value,
                            enumtypes.DiffType.REMOVED,
                        )
                    del opponent_dict[current_section]
                if sectionhasdifference == False:
                    cursor.movePosition(
                        QtGui.QTextCursor.MoveOperation.PreviousBlock,
                        cursor.MoveMode.KeepAnchor,
                    )
                    logger.debug(f"clearing {cursor.block().text()}")
                    cursor.removeSelectedText()
                    logger.debug(f"after clearing {cursor.block().text()}")
                current_section = line[1:-1]
                logger.debug(f"current section={current_section}")
                textedit.diff_dict[current_section] = {}
                sectionhasdifference = False
                logger.debug(f"new section:{current_section}")
                cursor.insertText(f"{line}\n", normal_format)
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
                        cursor.insertText(f"{line}\n", yellow_format)
                        textedit.diff_dict[current_section][key] = (
                            value,
                            enumtypes.DiffType.MODIFIED,
                        )
                        sectionhasdifference = True
                    del opponent_dict[current_section][key]
                else:
                    logger.debug(
                        f"insert green: section:{current_section},key:{key},value:{value}"
                    )
                    cursor.insertText(f"{line}\n", green_format)
                    textedit.diff_dict[current_section][key] = (
                        value,
                        enumtypes.DiffType.ADDED,
                    )
                    sectionhasdifference = True
        if current_section in opponent_dict:
            for key, value in opponent_dict[current_section].items():
                logger.debug(
                    f"missing section:{current_section},key:{key},value:{value}"
                )
                cursor.insertText(f"missing:{key} = {value}\n", red_format)
                textedit.diff_dict[current_section][key] = (
                    value,
                    enumtypes.DiffType.REMOVED,
                )
            del opponent_dict[current_section]
        if sectionhasdifference == False:
            cursor.movePosition(
                QtGui.QTextCursor.MoveOperation.PreviousBlock,
                cursor.MoveMode.KeepAnchor,
            )
            logger.debug(f"clearing {cursor.block().text()}")
            cursor.removeSelectedText()
            logger.debug(f"after clearing {cursor.block().text()}")
        current_section = None

        logger.debug(f"missing sections:{opponent_dict}")
        cursor.movePosition(cursor.MoveOperation.End, cursor.MoveMode.MoveAnchor)
        logger.debug(
            f"cursor line number:{cursor.block().lineCount()},cursor block content:{cursor.block().text()}"
        )
        for missing_section in opponent_dict:
            logger.debug(
                f"cursor position:{cursor.position()},cursor block content:{cursor.block().text()}"
            )
            cursor.insertText(f"missing section:[{missing_section}]\n", red_format)
            current_section = missing_section
            textedit.diff_dict[missing_section] = {}
            logger.debug(f"currrent missing section:[{missing_section}]")
            for key, value in opponent_dict[missing_section].items():
                logger.debug(f"=========missing start=========")
                logger.debug(
                    f"cursor position:{cursor.position()},cursor block content:{cursor.block().text()}"
                )
                cursor.insertText(f"missing:{key} = {value}\n", red_format)
                textedit.diff_dict[current_section][key] = (
                    value,
                    enumtypes.DiffType.REMOVED,
                )
                logger.debug(
                    f"cursor position:{cursor.position()},cursor block content:{cursor.block().text()}"
                )
                logger.debug(f"=========missing stop=========")

        logger.debug("switch to DIFF MODE")
        textedit.textmode = enumtypes.TextMode.DIFF
        textedit.savebutton.setText(
            textedit._translate("MainWindow", f"同步差异到文件(功能未完成)")
        )
        textedit.label.setText(
            textedit._translate(
                "MainWindow", f"差异编辑模式: {textedit.fileoriginalfullpath}"
            )
        )
        textedit.editbyuser = True
    """
