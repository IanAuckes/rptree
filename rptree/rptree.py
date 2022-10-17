"""This module provides RP Tree main module."""

import os
import pathlib
import sys
from collections import deque

PIPE = "│"
ELBOW = "└──"
TEE = "├──"
PIPE_PREFIX = "│   "
SPACE_PREFIX = "    "


class DirectoryTree:
    def __init__(self, root_dir, dir_only=False, skip_hidden=False, depth=1000, output_file=sys.stdout):
        self._output_file = output_file
        self._generator = _TreeGenerator(root_dir, dir_only, skip_hidden, depth)

    def generate(self):
        tree = self._generator.build_tree()
        if self._output_file != sys.stdout:
            # Wrap the tree in a markdown code block
            tree.appendleft("```")
            tree.append("```")
            self._output_file = open(
                self._output_file, mode="w", encoding="UTF-8"
            )
        with self._output_file as stream:
            for entry in tree:
                print(entry, file=stream)


class _TreeGenerator:
    def __init__(self, root_dir, dir_only=False, skip_hidden=False, depth=1000):
        self._root_dir = pathlib.Path(root_dir)
        self._dir_only = dir_only
        self._skip_hidden = skip_hidden
        self._depth = int(depth)
        self._depth_count = 0
        self._tree = deque()

    def build_tree(self):
        self._tree_head()
        self._tree_body(self._root_dir)
        return self._tree

    def _tree_head(self):
        self._tree.append(f"{self._root_dir}{os.sep}")

    def _tree_body(self, directory, prefix=""):
        entries = self._prepare_entries(directory)
        last_index = len(entries) - 1
        # local variable to reset depth_count per call
        depth_count = self._depth_count
        for index, entry in enumerate(entries):
            # Skip hidden files and folders
            if self._skip_hidden:
                if str(entry)[0] == '.' or '/.' in str(entry):
                    continue
            connector = ELBOW if index == last_index else TEE
            if self._depth_count >= self._depth:
                break
            if entry.is_dir():
                self._depth_count += 1
                self._add_directory(
                    entry, index, last_index, prefix, connector
                )
            else:
                self._add_file(entry, prefix, connector)
        # resetting the global depth_count
        self._depth_count = depth_count-1

    def _prepare_entries(self, directory):
        entries = sorted(
            directory.iterdir(), key=lambda entry: str(entry)
        )
        if self._dir_only:
            return [entry for entry in entries if entry.is_dir()]
        return sorted(entries, key=lambda entry: entry.is_file())

    def _add_directory(
        self, directory, index, last_index, prefix, connector
    ):
        self._tree.append(f"{prefix}{connector} {directory.name}{os.sep}")
        if index != last_index:
            prefix += PIPE_PREFIX
        else:
            prefix += SPACE_PREFIX
        self._tree_body(
            directory=directory,
            prefix=prefix,
        )

    def _add_file(self, file, prefix, connector):
        self._tree.append(f"{prefix}{connector} {file.name}")
