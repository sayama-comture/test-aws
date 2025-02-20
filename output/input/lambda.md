# コード解析ドキュメント

## 1. 概要
このPythonスクリプトは、指定されたディレクトリ内のコードファイルを解析し、Bedrock APIを使用して各ファイルの解析結果をMarkdownファイルとして出力するツールです。主な機能には、.gitignoreファイルの考慮、特定の拡張子を持つファイルの処理、Bedrock APIを使用したコード解析、エラー処理とリトライロジックが含まれています。

## 2. 詳細説明

### 主要なライブラリとモジュール
- `json`: JSON データの処理
- `os`: ファイルシステム操作
- `pathspec`: .gitignoreパターンの処理
- `logging`: ログ記録
- `boto3`: AWS SDK for Python、Bedrock APIとの通信に使用
- `time`: リトライ時の待機時間制御

### 主要な関数

#### `find_nearest_gitignore(file_path)`
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
        # ... (親ディレクトリへの移動ロジック)
    return None, None
```

この関数は、指定されたファイルパスから親ディレクトリを遡って.gitignoreファイルを探します。見つかった場合、その内容と場所を返します。

#### `should_process_file(file_path, base_path, gitignore_spec)`
ファイルが.gitignoreのパターンに該当するかチェックします。

```python
def should_process_file(file_path, base_path, gitignore_spec):
    if gitignore_spec is None:
        return True
    relative_path = os.path.relpath(file_path, base_path)
    return not gitignore_spec.match_file(relative_path)
```

この関数は、ファイルが.gitignoreパターンにマッチするかどうかを判断し、処理すべきかどうかを返します。

#### `analyze_with_bedrock(bedrock_runtime, code_content, file_path)`
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
        # ... (レスポンス処理とエラーハンドリング)
    except Exception as e:
        logger.error(f"Error analyzing {file_path}: {str(e)}")
        return None
```

この関数は、Bedrock APIを呼び出してコードを解析し、結果を返します。エラー発生時にはリトライロジックも実装されています。

#### `process_directory(input_dir, output_dir, target_extensions)`
指定されたディレクトリ内のファイルを処理します。

```python
def process_directory(input_dir, output_dir, target_extensions):
    processed_files = set()
    all_results = []
    for root, _, files in os.walk(input_dir):
        for file_name in files:
            # ... (ファイル処理ロジック)
    return {
        'message': 'Processing complete',
        'total_processed': len(processed_files),
        'results': all_results
    }
```

この関数は、入力ディレクトリ内のすべてのファイルを走査し、対象の拡張子を持つファイルを処理します。各ファイルに対して、.gitignoreチェック、Bedrock APIによる解析、結果の保存を行います。

### メイン実行フロー
`main()` 関数がスクリプトの主要なエントリーポイントとなっています。環境変数から設定を読み込み、`process_directory()` 関数を呼び出してディレクトリ処理を実行し、結果をJSON形式で出力します。

## 3. 動作仕様
1. スクリプトは環境変数から入力ディレクトリ、出力ディレクトリ、対象ファイル拡張子の設定を読み込みます。
2. 入力ディレクトリ内のファイルを再帰的に走査します。
3. 各ファイルに対して:
   a. ファイル拡張子が対象リストに含まれているかチェックします。
   b. 最も近い.gitignoreファイルを探し、ファイルが無視すべきかどうかを判断します。
   c. Bedrock APIを使用してファイルの内容を解析します。
   d. 解析結果を出力ディレクトリ内の対応するMarkdownファイルに保存します。
4. 処理結果の要約（総処理ファイル数、成功/失敗状態）をJSON形式で出力します。
5. エラーが発生した場合、ログに記録し、可能な場合はリトライを試みます。

このスクリプトは、大規模なコードベースの自動ドキュメント生成や、コード解析タスクの自動化に適しています。Bedrock APIとの連携により、高度なコード解析機能を提供しつつ、.gitignoreの考慮やエラーハンドリングなど、実用的な機能も備えています。