# コード解析ドキュメント

## 1. 概要
このPythonスクリプトは、指定されたディレクトリ内のコードファイルを解析し、Bedrock APIを使用して各ファイルの解析結果をMarkdownファイルとして出力するツールです。主な機能には、.gitignoreファイルの処理、特定の拡張子を持つファイルの選択的処理、Bedrock APIを使用したコード解析、そしてエラー処理と再試行ロジックが含まれています。

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
- `json`: 結果の JSON 形式での出力に使用
- `os`: ファイルシステム操作に使用
- `pathspec`: .gitignore パターンの処理に使用
- `logging`: ログ記録に使用
- `boto3`: AWS Bedrock API との対話に使用
- `time`: リトライ時の待機に使用
- `botocore.exceptions`: AWS 関連のエラー処理に使用

### ロギングの設定
```python
logger = logging.getLogger()
logger.setLevel(logging.INFO)
```
INFO レベルでロギングを設定し、処理の詳細を記録します。

### Bedrock クライアントの初期化
```python
bedrock_runtime = boto3.client(
    service_name='bedrock-agent-runtime',
    region_name='ap-northeast-1'
)
```
ap-northeast-1 リージョンで Bedrock Agent Runtime クライアントを初期化します。

### 主要な関数

1. `find_nearest_gitignore(file_path)`
   - 指定されたファイルパスから最も近い .gitignore ファイルを探索します。
   - 戻り値: .gitignore の内容と、その .gitignore ファイルが存在するディレクトリのパス

2. `should_process_file(file_path, base_path, gitignore_spec)`
   - ファイルが .gitignore のパターンに該当するかチェックします。
   - 戻り値: 処理すべきかどうかを示すブール値

3. `generate_output_path(input_path, output_dir)`
   - 入力ファイルパスから出力ファイルパスを生成します。
   - 戻り値: 生成された出力ファイルパス

4. `analyze_with_bedrock(bedrock_runtime, code_content, file_path)`
   - Bedrock API を使用してコードの解析を実行します。
   - エラー発生時に最大3回まで再試行します。
   - 戻り値: 解析結果の文字列、またはエラー時は None

5. `process_directory(input_dir, output_dir, target_extensions)`
   - 指定されたディレクトリ内のファイルを処理します。
   - .gitignore パターンに基づいてファイルをフィルタリングします。
   - 各ファイルに対して Bedrock 解析を実行し、結果を保存します。
   - 戻り値: 処理結果の詳細を含む辞書

6. `main()`
   - スクリプトのメイン実行関数です。
   - 環境変数から設定を読み込み、ディレクトリ処理を実行します。
   - 戻り値: 成功時は 0、エラー時は 1

### 重要なロジック
- .gitignore ファイルの処理: 最も近い .gitignore ファイルを見つけ、そのパターンに基づいてファイルをフィルタリングします。
- 拡張子ベースのファイル選択: 環境変数 `TARGET_EXTENSIONS` で指定された拡張子を持つファイルのみを処理します。
- Bedrock API 呼び出し: `invoke_flow` メソッドを使用して Bedrock Agent を呼び出し、コード解析を実行します。
- エラー処理と再試行: Bedrock API 呼び出し時のエラーに対して、最大3回まで再試行を行います。
- 結果の保存: 解析結果を Markdown ファイルとして保存し、処理の詳細を JSON 形式で出力します。

## 3. 動作仕様
1. スクリプトは `input` ディレクトリ内のファイルを処理対象とします。
2. 処理結果は `output` ディレクトリに保存されます。
3. 環境変数 `TARGET_EXTENSIONS` で指定された拡張子（デフォルトは .py, .js, .java, .cpp）を持つファイルのみが処理されます。
4. 各ファイルに対して:
   a. 最も近い .gitignore ファイルを探索し、そのパターンに基づいてファイルをフィルタリングします。
   b. Bedrock API を使用してコード解析を実行します。
   c. 解析結果を Markdown ファイルとして保存します。
5. 処理の詳細（成功したファイル、失敗したファイル、エラー内容など）が JSON 形式で出力されます。
6. ログは INFO レベルで記録され、処理の各ステップの詳細が表示されます。

このスクリプトは、大規模なコードベースの自動解析や、コードレビューの補助ツールとして活用できます。Bedrock API との連携により、高度なコード解析機能を提供しています。