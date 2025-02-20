# コード解析ドキュメント

## 1. 概要
このPythonスクリプトは、指定されたディレクトリ内のファイルを処理し、Amazon Bedrock APIを使用してコード解析を行うプログラムです。主な機能として、.gitignoreファイルの考慮、特定の拡張子を持つファイルの処理、Bedrock APIを使用したコード解析、結果のMarkdownファイルへの出力があります。

## 2. 詳細説明

### ライブラリのインポートと初期設定
```python
import json
import os
from pathspec import PathSpec
from pathspec.patterns import GitWildMatchPattern
import logging
import boto3
import time
from botocore.exceptions import ClientError

logger = logging.getLogger()
logger.setLevel(logging.INFO)

bedrock_runtime = boto3.client(
    service_name='bedrock-agent-runtime',
    region_name='ap-northeast-1'
)
```
- 必要なライブラリをインポートし、ロギングの設定を行います。
- boto3を使用してAmazon Bedrockのクライアントを初期化します。

### .gitignoreファイルの処理
```python
def find_nearest_gitignore(file_path):
    # ...

def should_process_file(file_path, base_path, gitignore_spec):
    # ...
```
- `find_nearest_gitignore`関数は、指定されたファイルパスから最も近い.gitignoreファイルを探索します。
- `should_process_file`関数は、ファイルが.gitignoreのパターンに該当するかチェックします。

### 出力パスの生成
```python
def generate_output_path(input_path, output_dir):
    # ...
```
- 入力ファイルパスから対応する出力ファイルパスを生成します。

### Bedrock APIを使用したコード解析
```python
def analyze_with_bedrock(bedrock_runtime, code_content, file_path):
    # ...
```
- Bedrock APIを呼び出してコード解析を実行します。
- エラーが発生した場合、最大3回まで再試行します。

### ディレクトリ処理
```python
def process_directory(input_dir, output_dir, target_extensions):
    # ...
```
- 指定されたディレクトリ内のファイルを再帰的に処理します。
- .gitignoreパターンに一致するファイルをスキップします。
- 指定された拡張子を持つファイルのみを処理します。
- 各ファイルに対してBedrock APIを使用して解析を行い、結果をMarkdownファイルとして保存します。

### メイン実行関数
```python
def main():
    # ...

if __name__ == "__main__":
    exit(main())
```
- 環境変数から設定を読み込み、`process_directory`関数を呼び出してディレクトリ処理を実行します。
- 処理結果をJSON形式で出力します。

## 3. 動作仕様
1. スクリプトは指定された入力ディレクトリ内のファイルを再帰的に探索します。
2. 各ファイルに対して、最も近い.gitignoreファイルを探し、そのパターンに一致するファイルをスキップします。
3. 指定された拡張子（デフォルトは.py, .js, .java, .cpp）を持つファイルのみを処理します。
4. 各対象ファイルの内容をBedrock APIに送信し、コード解析を実行します。
5. 解析結果を指定された出力ディレクトリ内にMarkdownファイルとして保存します。
6. 処理結果の概要（総処理ファイル数、各ファイルの処理状況）をJSON形式で出力します。
7. エラーが発生した場合、ログに記録し、処理を継続します。

このスクリプトは、大規模なコードベースの自動解析や、コードレビューの補助ツールとして使用できます。