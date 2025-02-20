# コード解析ドキュメント

## 1. 概要
このPythonスクリプトは、指定されたディレクトリ内のファイルを処理し、Amazon Bedrock APIを使用してコード解析を行うものです。主な機能として、.gitignoreファイルの考慮、特定の拡張子を持つファイルの処理、Bedrock APIを使用したコード解析、結果のMarkdownファイルへの出力があります。

## 2. 詳細説明

### 主要なライブラリとモジュール
- `json`: JSON形式のデータ処理
- `os`: ファイルシステム操作
- `pathspec`: .gitignoreパターンの処理
- `logging`: ログ出力
- `boto3`: AWS SDKを使用したBedrock APIとの通信
- `time`: リトライ時の待機時間制御

### 主要な関数

#### find_nearest_gitignore(file_path)
最も近い.gitignoreファイルを探索します。
```python
def find_nearest_gitignore(file_path):
    current_dir = os.path.dirname(os.path.abspath(file_path))
    while current_dir:
        gitignore_path = os.path.join(current_dir, '.gitignore')
        if os.path.exists(gitignore_path):
            with open(gitignore_path, 'r', encoding='utf-8') as f:
                content = f.read()
            return content, current_dir
        # 親ディレクトリへ移動
        parent_dir = os.path.dirname(current_dir)
        if parent_dir == current_dir:
            break
        current_dir = parent_dir
    return None, None
```
この関数は、指定されたファイルパスから最も近い.gitignoreファイルを探し、その内容とディレクトリを返します。

#### should_process_file(file_path, base_path, gitignore_spec)
ファイルが.gitignoreのパターンに該当するかチェックします。
```python
def should_process_file(file_path, base_path, gitignore_spec):
    if gitignore_spec is None:
        return True
    relative_path = os.path.relpath(file_path, base_path)
    return not gitignore_spec.match_file(relative_path)
```
この関数は、ファイルが.gitignoreパターンにマッチするかどうかを判断し、処理すべきかどうかを返します。

#### analyze_with_bedrock(bedrock_runtime, code_content, file_path)
Bedrock APIを使用してコードの解析を実行します。
```python
def analyze_with_bedrock(bedrock_runtime, code_content, file_path):
    try:
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
        # レスポンスの処理
    except ClientError as e:
        # エラー処理とリトライロジック
```
この関数は、Bedrock APIを呼び出してコード解析を行い、結果を返します。エラー発生時にはリトライロジックも実装されています。

#### process_directory(input_dir, output_dir, target_extensions)
指定されたディレクトリ内のファイルを処理します。
```python
def process_directory(input_dir, output_dir, target_extensions):
    processed_files = set()
    all_results = []
    for root, _, files in os.walk(input_dir):
        for file_name in files:
            # ファイル処理ロジック
```
この関数は、入力ディレクトリ内のファイルを走査し、対象の拡張子を持つファイルに対してコード解析を実行します。

### メイン実行フロー
`main()` 関数で全体の実行フローを制御しています。環境変数から設定を読み込み、`process_directory()` を呼び出してディレクトリ処理を実行します。

## 3. 動作仕様
1. 環境変数から入力ディレクトリ、出力ディレクトリ、対象ファイル拡張子を読み込みます。
2. 入力ディレクトリ内のファイルを再帰的に走査します。
3. 各ファイルに対して:
   a. .gitignoreパターンをチェックし、無視すべきファイルをスキップします。
   b. 対象拡張子を持つファイルのみを処理します。
   c. Bedrock APIを使用してコード解析を実行します。
   d. 解析結果をMarkdownファイルとして出力ディレクトリに保存します。
4. 処理結果の概要をJSON形式で出力します。

このスクリプトは、大規模なコードベースの自動解析や、コードレビューの補助ツールとして活用できます。エラーハンドリングとリトライメカニズムにより、安定した動作を実現しています。