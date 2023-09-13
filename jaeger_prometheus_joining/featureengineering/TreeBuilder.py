import os
from pathlib import Path

import polars as pl
from contest_tree.model.Node import Node
from contest_tree.model.Root import Root
from polars import col

from controlflow.ParseSettings import ParseSettings


class TreeBuilder:
    def __init__(self, settings: ParseSettings):
        self.settings = settings

    def start(self, source_path: Path, output_path):
        df = pl.read_csv(source_path)

        final_df = self.__parse_and_build_tree(df)
        self.__write_to_disk(final_df, output_path)

    def __parse_and_build_tree(self, df: pl.DataFrame) -> pl.DataFrame:
        def __build_tree(cur_node: Node):
            lookup = cur_node.data[1]
            found_spans = df.filter(col("childSpanId") == lookup)
            for span in found_spans.iter_rows():
                node = Node(data=span)
                cur_node.add_children([node])
                __build_tree(node)

        root_spans = df.filter(col("childSpanId") == None)
        final_df_list = []

        for cur_root in root_spans.iter_rows():
            root = Root(data=cur_root)

            __build_tree(root)
            tree = root.init_tree()

            tree.settings.print_data_with_accessing_field = True
            tree.settings.accessing_field = 1

            print(tree)

            final_df_list.append(pl.from_dicts(tree.to_polars_readable_format()))

        return pl.concat(final_df_list)

    def __write_to_disk(self, df: pl.DataFrame, output_path: Path):
        if not os.path.exists(output_path.parents[0]):
            os.makedirs(output_path.parents[0])

        df.write_csv(output_path)