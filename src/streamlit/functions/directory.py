import subprocess
import streamlit as st
from typing import Optional
import os


def search_directory(
    path: str,
    max_depth: Optional[int] = 4,
    pattern: Optional[str] = None,
    file_types: Optional[list[str]] = None,
) -> str:
    """
    findコマンドを使用してディレクトリツリーを取得する

    Args:
        path (str): 対象ディレクトリのパス
        max_depth (Optional[int]): 最大階層数（Noneの場合は制限なし）
        pattern (Optional[str]): 含めるファイル/ディレクトリのパターン（正規表現）
        file_types (Optional[list[str]]): 表示するファイル拡張子のリスト（例: [".py", ".txt"]）
        prune (bool): パターンに一致しないディレクトリを非表示にするかどうか

    Returns:
        str: ディレクトリ構造を表す文字列
    """

    # チルダを展開してフルパスに変換
    expanded_path = os.path.expanduser(path)

    # Check if target directory exists
    if not os.path.exists(expanded_path):
        return f"指定されたディレクトリ '{path}' は存在しません。"

    # カレントディレクトリに移動してから find を実行
    current_dir = os.getcwd()
    os.chdir(expanded_path)

    # パスを '.' に変更（カレントディレクトリを基準にする）
    cmd = ["find", "."]

    # 隠しファイルを除外
    cmd.extend(["-not", "-path", "*/.*"])

    # 最大階層の指定
    if max_depth is not None:
        cmd.extend(["-maxdepth", str(max_depth)])

    # ファイルタイプとパターンの処理
    if file_types or pattern:
        expressions = []

        if file_types:
            expressions.append("(")
            expressions.append("-type")
            expressions.append("d")  # ディレクトリ
            expressions.append("-o")
            expressions.append("-type")
            expressions.append("f")  # ファイル
            for ext in file_types:
                expressions.extend(["-iname", f"*{ext}"])
                if ext != file_types[-1]:
                    expressions.append("-o")
            expressions.append(")")

        if pattern:
            if len(expressions) > 0:
                expressions.append("-a")
            expressions.extend(["-iregex", f".*{pattern}.*"])

        if expressions:
            cmd.extend(expressions)

    print(" ".join(cmd))
    print(cmd)

    # シェルを使用せずにコマンドを実行
    result = subprocess.run(cmd, capture_output=True, text=True)

    # 元のディレクトリに戻る
    os.chdir(current_dir)

    result_str = f"root: {path}" + "\n" + result.stdout if result.stdout else "No files found"

    return result_str


if __name__ == "__main__":
    target_dir = input("探索するディレクトリを入力してください: ")
    print(
        search_directory(
            target_dir,
            file_types=["py", "md"],
            max_depth=4,
            pattern="*log*",
        )
    )
