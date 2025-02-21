# コード解析ドキュメント

## 1. 概要
このPythonスクリプトは、指定されたディレクトリ内のファイルを処理し、AWS Bedrock APIを使用してコード解析を行うプログラムです。主な機能として、.gitignoreファイルの考慮、特定の拡張子を持つファイルの処理、Bedrock APIを使用したコード解析、結果のMarkdownファイルへの出力があります。

## 2. 詳細説明

### 2.1 ライブラリとセットアップ
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
- `pathspec`は.gitignoreパターンの処理に使用されます。
- `boto3`はAWS Bedrockとの通信に使用されます。

### 2.2 ロギング設定
```python
logger = logging.getLogger()
logger.setLevel(logging.INFO)
```
- ロギングレベルをINFOに設定し、詳細な実行ログを出力します。

### 2.3 AWS Bedrock クライアントの初期化
```python
bedrock_runtime = boto3.client(
    service_name='bedrock-agent-runtime',
    region_name='ap-northeast-1'
)
```
- AWS Bedrock Agent Runtimeクライアントを初期化します。リージョンは東京（ap-northeast-1）に設定されています。

### 2.4 .gitignore処理
```python
def find_nearest_gitignore(file_path):
    # ...

def should_process_file(file_path, base_path, gitignore_spec):
    # ...
```
- `find_nearest_gitignore`関数は、指定されたファイルパスから最も近い.gitignoreファイルを探索します。
- `should_process_file`関数は、ファイルが.gitignoreのパターンに該当するかチェックします。

### 2.5 出力パス生成
```python
def generate_output_path(input_path, output_dir):
    # ...
```
- 入力ファイルパスから対応する出力ファイルパスを生成します。

### 2.6 Bedrock APIを使用したコード解析
```python
def analyze_with_bedrock(bedrock_runtime, code_content, file_path):
    # ...
```
- Bedrock APIを呼び出してコード解析を実行します。
- エラー発生時は最大3回まで再試行します。

### 2.7 ディレクトリ処理
```python
def process_directory(input_dir, output_dir, target_extensions):
    # ...
```
- 指定されたディレクトリ内のファイルを再帰的に処理します。
- .gitignoreパターン、ファイル拡張子、既処理ファイルのチェックを行います。
- 各ファイルに対してBedrock APIによる解析を実行し、結果をMarkdownファイルとして保存します。

### 2.8 メイン実行関数
```python
def main():
    # ...

if __name__ == "__main__":
    exit(main())
```
- 環境変数から設定を読み込み、`process_directory`関数を呼び出してディレクトリ処理を実行します。
- 処理結果をJSON形式で出力します。

## 3. 動作仕様
1. スクリプトは、環境変数から入力ディレクトリ、出力ディレクトリ、対象ファイル拡張子の設定を読み込みます。
2. 入力ディレクトリ内のファイルを再帰的に探索します。
3. 各ファイルに対して以下の処理を行います：
   a. .gitignoreパターンに該当するかチェック
   b. 指定された拡張子を持つかチェック
   c. 既に処理済みでないかチェック
4. 条件を満たすファイルに対して、Bedrock APIを使用してコード解析を実行します。
5. 解析結果をMarkdownファイルとして出力ディレクトリに保存します。
6. 全ファイルの処理が完了したら、処理結果の概要をJSON形式で出力します。

このスクリプトは、大規模なコードベースの自動解析や、コードレビューの補助ツールとして活用できます。AWS Bedrockの機能を利用することで、高度なコード解析が可能となっています。