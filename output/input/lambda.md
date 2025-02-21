# コード解析ドキュメント

## 1. 概要
このPythonスクリプトは、指定されたディレクトリ内のコードファイルを解析し、Bedrock APIを使用して各ファイルの解析結果をMarkdownファイルとして出力するツールです。主な機能には、.gitignoreファイルの考慮、特定の拡張子を持つファイルの処理、Bedrock APIを使用したコード解析、エラー処理とリトライロジックが含まれています。

## 2. 詳細説明

### 主要なライブラリとモジュール
- `json`: JSON形式のデータ処理に使用
- `os`: ファイルシステム操作に使用
- `pathspec`: .gitignoreパターンの処理に使用
- `logging`: ログ出力に使用
- `boto3`: AWS Bedrock APIとの通信に使用
- `time`: リトライ時の待機時間制御に使用

### 主要な関数

1. `find_nearest_gitignore(file_path)`
   - 指定されたファイルパスから最も近い.gitignoreファイルを探索します。
   - 戻り値: .gitignoreの内容と、その.gitignoreファイルが存在するディレクトリのパス

2. `should_process_file(file_path, base_path, gitignore_spec)`
   - ファイルが.gitignoreのパターンに該当するかチェックします。
   - 戻り値: 処理すべきファイルの場合はTrue、そうでない場合はFalse

3. `generate_output_path(input_path, output_dir)`
   - 入力ファイルパスから出力ファイルパスを生成します。
   - 戻り値: 生成された出力ファイルパス

4. `analyze_with_bedrock(bedrock_runtime, code_content, file_path)`
   - Bedrock APIを使用してコードの解析を実行します。
   - エラー発生時は最大3回のリトライを行います。
   - 戻り値: Bedrockからの解析結果、またはNone（エラー時）

5. `process_directory(input_dir, output_dir, target_extensions)`
   - 指定されたディレクトリ内のファイルを処理します。
   - .gitignoreの考慮、ファイル拡張子のチェック、Bedrock APIによる解析を行います。
   - 戻り値: 処理結果の概要（辞書形式）

6. `main()`
   - スクリプトのメイン実行関数です。
   - 環境変数から設定を読み込み、`process_directory`を呼び出します。

### 重要なコードスニペット

Bedrock APIの呼び出し:
```python
flow_response = bedrock_runtime.invoke_flow(
    flowIdentifier="F9PY7W1IXS",
    flowAliasIdentifier="2EJ5QG9EI8",
    inputs=[{
        'content': {
            'document': code_content
        },
        'nodeName': 'FlowInputNode',
        'nodeOutputName': 'document'
    }]
)
```
このコードは、Bedrock APIを呼び出してコード解析を実行します。`flowIdentifier`と`flowAliasIdentifier`は特定のBedrockフローを指定し、`inputs`にはコードの内容が含まれています。

エラー処理とリトライロジック:
```python
for attempt in range(3):
    try:
        time.sleep(2 ** attempt)
        # Bedrock API呼び出し
        # ...
    except ClientError as retry_error:
        if attempt == 2:
            raise retry_error
        continue
```
このコードは、Bedrock API呼び出し時にエラーが発生した場合、最大3回のリトライを行います。各リトライの間隔は指数関数的に増加します。

## 3. 動作仕様
1. スクリプトは`input`ディレクトリ内のファイルを処理対象とします。
2. 処理対象のファイル拡張子は環境変数`TARGET_EXTENSIONS`で指定されます（デフォルトは.py, .js, .java, .cpp）。
3. 各ファイルに対して、最も近い.gitignoreファイルを探索し、そのルールに従ってファイルをスキップするかどうかを決定します。
4. 処理対象のファイルは、Bedrock APIを使用して解析されます。
5. 解析結果は`output`ディレクトリに保存され、ファイル名は元のファイル名に基づいて生成されます（拡張子は.mdに変更）。
6. 処理中にエラーが発生した場合、ログに記録され、可能な場合はリトライが行われます。
7. 全ファイルの処理が完了すると、処理結果の概要がJSON形式で出力されます。

このスクリプトは、大規模なコードベースの自動ドキュメント生成や、コードレビューの補助ツールとして活用できます。