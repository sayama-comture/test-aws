# コード解析ドキュメント

## 1. 概要
このPythonスクリプトは、指定されたディレクトリ内のファイルを処理し、Bedrock APIを使用してコード解析を行うプログラムです。主な機能として、.gitignoreファイルの考慮、特定の拡張子を持つファイルの処理、Bedrock APIを使用したコード解析、結果の保存があります。

## 2. 詳細説明

### 主要なライブラリとセットアップ
```python
import json
import os
from pathspec import PathSpec
from pathspec.patterns import GitWildMatchPattern
import logging
import boto3
import time
from botocore.exceptions import ClientError
```
- 標準ライブラリ（json, os, logging, time）と外部ライブラリ（pathspec, boto3）を使用しています。
- loggingを設定し、boto3を使用してBedrock clientを初期化しています。

### .gitignore処理
```python
def find_nearest_gitignore(file_path):
    # ...

def should_process_file(file_path, base_path, gitignore_spec):
    # ...
```
- `find_nearest_gitignore`関数は、指定されたファイルパスから最も近い.gitignoreファイルを探索します。
- `should_process_file`関数は、ファイルが.gitignoreのパターンに該当するかチェックします。

### ファイル処理と出力パス生成
```python
def generate_output_path(input_path, output_dir):
    # ...
```
- 入力ファイルパスから出力ファイルパスを生成します。

### Bedrock APIを使用したコード解析
```python
def analyze_with_bedrock(bedrock_runtime, code_content, file_path):
    # ...
```
- Bedrock APIを呼び出してコード解析を実行します。
- エラー発生時には最大3回のリトライを行います。

### ディレクトリ処理
```python
def process_directory(input_dir, output_dir, target_extensions):
    # ...
```
- 指定されたディレクトリ内のファイルを再帰的に処理します。
- .gitignoreパターンのチェック、ファイル拡張子の確認、Bedrock APIによる解析を行います。

### メイン実行関数
```python
def main():
    # ...

if __name__ == "__main__":
    exit(main())
```
- 環境変数から設定を読み込み、`process_directory`関数を呼び出してディレクトリ処理を実行します。

## 3. 動作仕様
1. 環境変数から入力ディレクトリ、出力ディレクトリ、対象ファイル拡張子を読み込みます。
2. 入力ディレクトリ内のファイルを再帰的に処理します。
3. 各ファイルに対して:
   a. 最も近い.gitignoreファイルを探索し、パターンをチェックします。
   b. ファイル拡張子が対象拡張子リストに含まれているか確認します。
   c. Bedrock APIを使用してコード解析を実行します。
   d. 解析結果を出力ディレクトリに保存します。
4. 処理結果の概要（総処理ファイル数、各ファイルの処理状況）をJSON形式で出力します。

このスクリプトは、大規模なコードベースの自動解析や、コードレビューの補助ツールとして活用できます。