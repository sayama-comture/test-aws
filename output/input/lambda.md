# コード解析ドキュメント

## 1. 概要
このPythonスクリプトは、指定されたディレクトリ内のファイルを処理し、Amazon Bedrock APIを使用してコード解析を行うプログラムです。主な機能として、.gitignoreファイルの考慮、特定の拡張子を持つファイルの処理、Bedrock APIを使用したコード解析、結果のMarkdownファイルへの出力があります。

## 2. 詳細説明

### 主要なライブラリとモジュール
- `json`: JSON形式のデータ処理
- `os`: ファイルシステム操作
- `pathspec`: .gitignoreパターンの処理
- `logging`: ログ出力
- `boto3`: AWS SDKを使用したBedrock APIとの通信
- `time`: リトライ時の待機時間制御

### 主要な関数

1. `find_nearest_gitignore(file_path)`
   - 指定されたファイルパスから最も近い.gitignoreファイルを探索します。
   - 戻り値: .gitignoreの内容とそのディレクトリパス

2. `should_process_file(file_path, base_path, gitignore_spec)`
   - ファイルが.gitignoreのパターンに該当するかチェックします。
   - 戻り値: 処理すべきかどうかのブール値

3. `generate_output_path(input_path, output_dir)`
   - 入力ファイルパスから出力ファイルパスを生成します。
   - 戻り値: 出力ファイルのパス

4. `analyze_with_bedrock(bedrock_runtime, code_content, file_path)`
   - Bedrock APIを使用してコードの解析を実行します。
   - エラー時は最大3回のリトライを行います。
   - 戻り値: 解析結果の文字列

5. `process_directory(input_dir, output_dir, target_extensions)`
   - 指定されたディレクトリ内のファイルを処理します。
   - .gitignoreの考慮、ファイル拡張子のチェック、Bedrock APIによる解析を行います。
   - 戻り値: 処理結果の辞書

6. `main()`
   - プログラムのエントリーポイントです。
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
このコードは、Bedrock APIを呼び出してコード解析を実行します。`flowIdentifier`と`flowAliasIdentifier`は特定のBedrock Agentを指定し、`inputs`にはコンテンツを含む辞書を渡します。

エラーハンドリングとリトライロジック:
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
このコードは、Bedrock API呼び出し時のエラーに対して、指数バックオフを使用したリトライロジックを実装しています。

## 3. 動作仕様
1. プログラムは`main()`関数から開始し、環境変数から設定を読み込みます。
2. `process_directory()`関数が呼び出され、指定されたディレクトリ内のファイルを処理します。
3. 各ファイルに対して:
   a. .gitignoreファイルをチェックし、無視すべきファイルをスキップします。
   b. 指定された拡張子を持つファイルのみを処理します。
   c. Bedrock APIを使用してコード解析を実行します。
   d. 解析結果をMarkdownファイルとして出力ディレクトリに保存します。
4. 処理結果の概要をJSON形式で出力します。

このプログラムは、大規模なコードベースの自動解析や、コードレビューの補助ツールとして使用できます。Bedrock APIとの連携により、高度なコード解析が可能となっています。