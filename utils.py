from typing import Optional
import re


def insert_string_at_index(original_string, insert_string, index):
    """
    在指定索引處向字符串中插入另一個字符串。

    Args:
        original_string (_type_): 原始字符串。
        insert_string (_type_): 要插入的字符串。
        index (_type_): 插入位置的索引。

    Returns:
        _type_: 修改後的新字符串。
    """
    return original_string[:index] + insert_string + original_string[index:]


def add_special_token(text, ent):
    x = insert_string_at_index(text, " $ ", ent["start"])
    x = insert_string_at_index(x, " $", ent["end"] + 3)
    x = re.sub(r"\s+", " ", x).strip()
    return x


class AnalysisExample:
    def __init__(self) -> None:
        self.text: str = None
        self.entities: list[dict] = []

    def add_re_event(
        self,
        re_output,
        special_start_index: Optional[int] = None,
        special_end_index: Optional[int] = None
    ):
        for ent in re_output["entities"]:
            if special_start_index is not None and special_end_index is not None:
                if special_start_index < ent["start"] and ent["start"] < special_end_index:
                    ent["start"] -= 2
                    ent["end"] -= 2
                elif special_end_index < ent["start"]:
                    ent["start"] -= 4
                    ent["end"] -= 4
            if ent["start"] == 0:  # 開頭的 start index 不計算空白，所不用往右偏移一位
                continue
            ent["start"] += 1  # 因為 deberta tokenizer 的特性會計算空白，所以 start index 要往右偏移一位
        event_text = re.sub(r"\s*\$\s*", " ", re_output["text"])
        if self.text is None:
            self.text = event_text
            self.entities.extend(re_output["entities"])
        else:
            point = len(self.text) + len("\n\n")
            for ent in re_output["entities"]:
                ent["start"] += point
                ent["end"] += point

            self.text = self.text + "\n\n" + event_text
            self.entities.extend(re_output["entities"])
