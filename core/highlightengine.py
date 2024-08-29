from PyQt6.QtGui import QTextCharFormat, QColor
from PyQt6 import QtWidgets, QtCore, QtGui
import util.enumtypes as enumtypes
import logging
from typing import Callable,Iterable

logger = logging.getLogger(__name__)

""" 
def apply_format_to_line(text_edit, line_num, format):
    cursor = text_edit.textCursor()
    cursor.movePosition(cursor.MoveOperation.Start)
    for _ in range(line_num):
        cursor.movePosition(cursor.MoveOperation.Down)
    cursor.movePosition(cursor.MoveOperation.EndOfLine, cursor.MoveMode.KeepAnchor)
    cursor.mergeCharFormat(format)


  
def highlight_text(text_edit, comparison_result):
    green_format = QTextCharFormat()
    green_format.setBackground(QColor("green"))

    yellow_format = QTextCharFormat()
    yellow_format.setBackground(QColor("yellow"))

    red_format = QTextCharFormat()
    red_format.setBackground(QColor("red"))

    text_lines = text_edit.toPlainText().splitlines()

    line_num = 0
    for section, keys in comparison_result.items():
        apply_format_to_line(text_edit, line_num, QTextCharFormat())  # Reset format for section line
        line_num += 1

        for key, status in keys.items():
            if status[0] == enumerate.DiffType.ADDED:
                apply_format_to_line(text_edit, line_num, green_format)
            elif status[0] == enumerate.DiffType.MODIFIED:
                apply_format_to_line(text_edit, line_num, yellow_format)
            line_num += 1
        
        # Handle missing keys from the comparison
        for key, status in keys.items():
            if status[0] == enumerate.DiffType.REMOVED:
                cursor = text_edit.textCursor()
                cursor.movePosition(cursor.MoveOperation.End)
                cursor.insertText(f"missing:{key}={status[1]}\n", red_format)
"""


class HighLightEngine:
    def __init__(self):
        self._red_format = QtGui.QTextCharFormat()
        self._red_format.setBackground(QColor("red"))
        self._yellow_format = QtGui.QTextCharFormat()
        self._yellow_format.setBackground(QColor("yellow"))
        self._lighter_yellow_format = QtGui.QTextCharFormat()
        self._lighter_yellow_format.setBackground(QColor("yellow").lighter(160))
        self._green_format = QtGui.QTextCharFormat()
        self._green_format.setBackground(QColor("green"))
        self._cyan_format = QtGui.QTextCharFormat()
        self._cyan_format.setBackground(QColor("cyan"))
        self._normal_format = QtGui.QTextCharFormat()

    def clearExtraselections(self, text_edit: QtWidgets.QPlainTextEdit):
        text_edit.setExtraSelections([])

        
    def highlightCurrentLine(
        self,
        cursor: QtGui.QTextCursor,
        setExtraSelections_handle: Callable[[Iterable['QtWidgets.QTextEdit.ExtraSelection']], None],
    ):
        extraSelections = []
        selection = QtWidgets.QTextEdit.ExtraSelection()

        selection.format.setBackground(QColor("yellow").lighter(160))
        selection.format.setProperty(
            QtGui.QTextFormat.Property.FullWidthSelection, True
        )
        selection.cursor = cursor
        selection.cursor.clearSelection()
        extraSelections.append(selection)

        setExtraSelections_handle(extraSelections)

    def extraselectCurrentLine(
        self,
        text_edit: QtWidgets.QPlainTextEdit,
    )->QtWidgets.QTextEdit.ExtraSelection:
        selection=QtWidgets.QTextEdit.ExtraSelection()
        selection.format.setProperty( QtGui.QTextFormat.Property.FullWidthSelection, True      )
        selection.format.setBackground(QColor("cyan"))
        cursor=text_edit.textCursor()
        cursor.movePosition(cursor.MoveOperation.StartOfBlock)
        selection.cursor=cursor
        return selection

    def extraselectLine(
        self,
        text_edit: QtWidgets.QPlainTextEdit,
        block_number:int,
    )->QtWidgets.QTextEdit.ExtraSelection:  
        selection=QtWidgets.QTextEdit.ExtraSelection()
        selection.format.setProperty( QtGui.QTextFormat.Property.FullWidthSelection, True)
        selection.format.setBackground(QColor("cyan"))
        cursor=QtGui.QTextCursor(text_edit.document().findBlockByNumber(block_number))
        cursor.clearSelection()
        selection.cursor=cursor
        return selection
    
    def extraselectLines(
        self,
        list_of_diff_lines: list[tuple[str, enumtypes.DiffType]],
        text_edit: QtWidgets.QPlainTextEdit,
        is_slave=False,
        alias="",
    )->list[QtWidgets.QTextEdit.ExtraSelection]:  
        extraSelections = []
        doc=text_edit.document()
        if not is_slave:
            add_color=QColor("green")
            remove_color=QColor("red")
        else:
            add_color=QColor("red")
            remove_color=QColor("green")
        for line in list_of_diff_lines:
            block=doc.findBlockByLineNumber(int(line[0])-1)
            if block.isValid():
                selection=QtWidgets.QTextEdit.ExtraSelection()
                selection.format.setProperty(
            QtGui.QTextFormat.Property.FullWidthSelection, True
                )
                if line[1] == enumtypes.DiffType.ADDED:
                    selection.format.setBackground(add_color)
                elif line[1] == enumtypes.DiffType.MODIFIED:
                    selection.format.setBackground(QColor("yellow"))
                elif line[1]==enumtypes.DiffType.REMOVED:
                    selection.format.setBackground(remove_color)
                cursor=QtGui.QTextCursor(block)
                cursor.clearSelection()
                selection.cursor=cursor
                extraSelections.append(selection)
            else:
                logger.error(f"{alias} line {line[0]} is invalid")
                continue
        text_edit.setExtraSelections(extraSelections)
        return extraSelections

    def highlight_cursor_with_selection(self, cursor: QtGui.QTextCursor):
        cursor.setCharFormat(self._cyan_format)

    def highlight_cursor(self, document: QtWidgets.QPlainTextEdit, color="cyan"):
        if color is None or color == "":
            return
        if color == "cyan":
            format = self._cyan_format
        elif color == "yellow":
            format = self._yellow_format
        elif color == "red":
            format = self._red_format
        elif color == "green":
            format = self._green_format
        elif color == "normal":
            format = self._normal_format
        else:
            logger.error(f"unknown color")
            return        
        document.setCurrentCharFormat(format)

    def highlight_line(self, cursor, format):
        # logger.debug(f"Current block content:{cursor.block().text()},Position in Block: {cursor.positionInBlock()}")
        # cursor.movePosition(cursor.MoveOperation.StartOfBlock)
        logger.debug(
            f"before highlight the line: Current block content:{cursor.block().text()},Position in Block: {cursor.positionInBlock()}"
        )
        cursor.movePosition(cursor.MoveOperation.EndOfBlock, cursor.MoveMode.KeepAnchor)

        logger.debug(
            f"after moveright: Current block content:{cursor.block().text()},Position in Block: {cursor.positionInBlock()}"
        )
        cursor.mergeCharFormat(format)

    def highlight_text(
        self, text_edit: QtWidgets.QPlainTextEdit, comparison_result, is_opposite=False
    ):
        green_format = QTextCharFormat()
        green_format.setBackground(QColor("green"))

        yellow_format = QTextCharFormat()
        yellow_format.setBackground(QColor("yellow"))

        red_format = QTextCharFormat()
        red_format.setBackground(QColor("red"))

        text_lines = text_edit.fileoriginalcontent.split("\n")

        cursor = text_edit.textCursor()
        cursor.movePosition(cursor.MoveOperation.Start)
        cursor.movePosition(cursor.MoveOperation.StartOfBlock)
        current_section = None
        for line in text_lines:
            logger.debug("=============================")
            logger.debug(f"current line from file source:{line}")
            # 游标应在第一个字母前，上一个\n后
            if line.startswith("[") and line.endswith("]"):
                logger.debug("section line")
                if current_section is not None:
                    for key, status in comparison_result[current_section].items():
                        logger.debug(
                            f"section:{current_section},key:{key},status:{status}"
                        )
                        if status[0] == enumtypes.DiffType.REMOVED:
                            cursor.insertText(
                                f"missing:{key}={status[1]}\n", red_format
                            )
                            logger.debug(f"missing:{key}={status[1]}")
                    del comparison_result[current_section]
                current_section = line[1:-1]
                cursor.movePosition(cursor.MoveOperation.NextBlock)
            else:
                logger.debug("key-value line")
                key = line.split("=")[0].strip()
                if current_section is None:
                    logger.critical(f"No section found for line: {line}")
                    continue

                if key in comparison_result[current_section]:
                    if (
                        comparison_result[current_section][key][0]
                        == enumtypes.DiffType.REMOVED
                    ):
                        logger.critical(f"Key {key} found in comparison")
                    elif (
                        comparison_result[current_section][key][0]
                        == enumtypes.DiffType.ADDED
                    ):
                        self.highlight_line(cursor, green_format)
                        logger.debug(f"{key} change to green")
                    elif (
                        comparison_result[current_section][key][0]
                        == enumtypes.DiffType.MODIFIED
                    ):
                        logger.debug(
                            f"cursor selection:{cursor.hasSelection()},cursor line:{cursor.blockNumber()},cursor position:{cursor.positionInBlock()},cursor block content:{cursor.block().text()}"
                        )
                        self.highlight_line(cursor, yellow_format)
                        logger.debug(f"{key} change to yellow")
                cursor.movePosition(cursor.MoveOperation.NextBlock)
            logger.debug(
                f"after highlight: cursor position:{cursor.position()},cursor block content:{cursor.block().text()}"
            )

        if current_section is None:
            logger.critical("No section found for last line")
            return
        if current_section is not None:
            for key, status in comparison_result[current_section].items():
                logger.debug(f"section:{current_section},key:{key},status:{status}")
                if status[0] == enumtypes.DiffType.REMOVED:
                    cursor.insertText(f"missing:{key}={status[1]}\n", red_format)
                    logger.debug(f"missing:{key}={status[1]}")
            del comparison_result[current_section]
        current_section = None

        logger.debug(f"missing sections:{comparison_result}")
        cursor.movePosition(cursor.MoveOperation.End, cursor.MoveMode.MoveAnchor)
        logger.debug(
            f"cursor line number:{cursor.block().lineCount()},cursor block content:{cursor.block().text()}"
        )
        for missing_section in comparison_result:
            logger.debug(
                f"cursor position:{cursor.position()},cursor block content:{cursor.block().text()}"
            )
            cursor.insertText(f"missing section:[{missing_section}]\n", red_format)
            logger.debug(f"currrent missing section:[{missing_section}]")
            for key, status in comparison_result[missing_section].items():
                logger.debug(f"=========missing start=========")
                if status[0] == enumtypes.DiffType.REMOVED:
                    logger.debug(
                        f"cursor position:{cursor.position()},cursor block content:{cursor.block().text()}"
                    )
                    cursor.insertText(f"{key}={status[1]}\n", red_format)
                    logger.debug(
                        f"cursor position:{cursor.position()},cursor block content:{cursor.block().text()}"
                    )
                    logger.debug(
                        f"cursor position:{cursor.position()},cursor block content:{cursor.block().text()}"
                    )
                else:
                    logger.critical(
                        f"Key {key}: Status other, found in missing_section{missing_section}"
                    )
                logger.debug(
                    f"cursor position:{cursor.position()},cursor block content:{cursor.block().text()}"
                )
                logger.debug(f"=========missing stop=========")
        """
            cursor = text_edit.textCursor()
            cursor.movePosition(cursor.MoveOperation.Start)
            while cursor.movePosition(cursor.MoveOperation.NextBlock):
                cursor.select(cursor.SelectionType.BlockUnderCursor)
                format = cursor.charFormat()
                logger.debug(
                    f"block number:{cursor.block().blockNumber()}\ncursor block content:{cursor.block().text()}\n \
                    isvisiable:{cursor.block().isVisible()}\ncursor position:{cursor.position()}\n \
                    background:{format.background().color().name()}\n \
                    foreground:{format.foreground().color().name()}\n \
                    format:{format}\n \
                    ----------------\n"
                )
        """

    def highlight_text_opposite(
        self, text_edit: QtWidgets.QTextEdit, comparison_result
    ):
        green_format = QTextCharFormat()
        green_format.setBackground(QColor("green"))

        yellow_format = QTextCharFormat()
        yellow_format.setBackground(QColor("yellow"))

        red_format = QTextCharFormat()
        red_format.setBackground(QColor("red"))

        text_lines = text_edit.fileoriginalcontent.split("\n")

        line_num = 0
        cursor = text_edit.textCursor()
        cursor.movePosition(cursor.MoveOperation.Start)
        cursor.movePosition(cursor.MoveOperation.StartOfBlock)
        current_section = None
        for line in text_lines:
            logger.debug("=============================")
            logger.debug(f"current line from file source:{line}")
            # 游标应在第一个字母前，上一个\n后
            if line.startswith("[") and line.endswith("]"):
                logger.debug("section line")
                if current_section is not None:
                    for key, status in comparison_result[current_section].items():
                        logger.debug(
                            f"section:{current_section},key:{key},status:{status}"
                        )
                        if status[0] == enumtypes.DiffType.REMOVED:
                            cursor.insertText(
                                f"missing:{key}={status[1]}\n", red_format
                            )
                            logger.debug(f"missing:{key}={status[1]}")
                    del comparison_result[current_section]
                current_section = line[1:-1]
                cursor.movePosition(cursor.MoveOperation.NextBlock)
            else:
                logger.debug("key-value line")
                key = line.split("=")[0].strip()
                if current_section is None:
                    logger.critical(f"No section found for line: {line}")
                    continue

                if key in comparison_result[current_section]:
                    if (
                        comparison_result[current_section][key][0]
                        == enumtypes.DiffType.ADDED
                    ):
                        logger.critical(f"Key {key} found in comparison")
                    elif (
                        comparison_result[current_section][key][0]
                        == enumtypes.DiffType.REMOVED
                    ):
                        self.highlight_line(cursor, green_format)
                        logger.debug(f"{key} change to green")
                    elif (
                        comparison_result[current_section][key][0]
                        == enumtypes.DiffType.MODIFIED
                    ):
                        logger.debug(
                            f"cursor selection:{cursor.hasSelection()},cursor line:{cursor.blockNumber()},cursor position:{cursor.positionInBlock()},cursor block content:{cursor.block().text()}"
                        )
                        self.highlight_line(cursor, yellow_format)
                        logger.debug(f"{key} change to yellow")
                cursor.movePosition(cursor.MoveOperation.NextBlock)
            logger.debug(
                f"after highlight: cursor position:{cursor.position()},cursor block content:{cursor.block().text()}"
            )

        if current_section is None:
            logger.critical("No section found for last line")
            return
        if current_section is not None:
            for key, status in comparison_result[current_section].items():
                logger.debug(f"section:{current_section},key:{key},status:{status}")
                if status[0] == enumtypes.DiffType.REMOVED:
                    cursor.insertText(f"missing:{key}={status[1]}\n", red_format)
                    logger.debug(f"missing:{key}={status[1]}")
            del comparison_result[current_section]
        current_section = None

        logger.debug(f"missing sections:{comparison_result}")
        cursor.movePosition(cursor.MoveOperation.End, cursor.MoveMode.MoveAnchor)
        logger.debug(
            f"cursor line number:{cursor.block().lineCount()},cursor block content:{cursor.block().text()}"
        )
        for missing_section in comparison_result:
            logger.debug(
                f"cursor position:{cursor.position()},cursor block content:{cursor.block().text()}"
            )
            cursor.insertText(f"missing section:[{missing_section}]\n", red_format)
            logger.debug(f"currrent missing section:[{missing_section}]")
            for key, status in comparison_result[missing_section].items():
                logger.debug(f"=========missing start=========")
                if status[0] == enumtypes.DiffType.REMOVED:
                    logger.debug(
                        f"cursor position:{cursor.position()},cursor block content:{cursor.block().text()}"
                    )
                    cursor.insertText(f"{key}={status[1]}\n", red_format)
                    logger.debug(
                        f"cursor position:{cursor.position()},cursor block content:{cursor.block().text()}"
                    )
                    logger.debug(
                        f"cursor position:{cursor.position()},cursor block content:{cursor.block().text()}"
                    )
                else:
                    logger.critical(
                        f"Key {key}: Status other, found in missing_section{missing_section}"
                    )
                logger.debug(
                    f"cursor position:{cursor.position()},cursor block content:{cursor.block().text()}"
                )
                logger.debug(f"=========missing stop=========")
        """
            cursor = text_edit.textCursor()
            cursor.movePosition(cursor.MoveOperation.Start)
            while cursor.movePosition(cursor.MoveOperation.NextBlock):
                cursor.select(cursor.SelectionType.BlockUnderCursor)
                format = cursor.charFormat()
                logger.debug(
                    f"block number:{cursor.block().blockNumber()}\ncursor block content:{cursor.block().text()}\n \
                    isvisiable:{cursor.block().isVisible()}\ncursor position:{cursor.position()}\n \
                    background:{format.background().color().name()}\n \
                    foreground:{format.foreground().color().name()}\n \
                    format:{format}\n \
                    ----------------\n"
                )
        """
