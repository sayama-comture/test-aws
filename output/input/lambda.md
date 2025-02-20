# コード解析ドキュメント

## 1. 概要
このPythonスクリプトは、指定されたディレクトリ内のコードファイルを解析し、Bedrock APIを使用して各ファイルの解析結果をMarkdownファイルとして出力するツールです。主な機能には、.gitignoreファイルの処理、特定の拡張子を持つファイルの選択的処理、Bedrock APIを使用したコード解析、そしてエラー処理と再試行ロジックが含まれています。

## 2. 詳細説明

### 主要なライブラリとモジュール
- `json`: JSON データの処理に使用
- `os`: ファイルシステム操作に使用
- `pathspec`: .gitignoreパターンの処理に使用
- `logging`: ログ出力に使用
- `boto3`: AWS Bedrock APIとの通信に使用
- `time`: 再試行ロジックでの待機時間制御に使用

### 主要な関数

#### `find_nearest_gitignore(file_path)`
この関数は、指定されたファイルパスから最も近い.gitignoreファイルを探索します。

```python
def find_nearest_gitignore(file_path):
    current_dir = os.path.dirname(os.path.abspath(file_path))
    while current_dir:
        gitignore_path = os.path.join(current_dir, '.gitignore')
        if os.path.exists(gitignore_path):
            with open(gitignore_path, 'r', encoding='utf-8') as f:
                content = f.read()
            return content, current_dir
        parent_dir = os.path.dirname(current_dir)
        if parent_dir == current_dir:
            break
        current_dir = parent_dir
    return None, None
```

この関数は、ファイルパスから親ディレクトリを辿り、.gitignoreファイルを探します。見つかった場合、その内容と親ディレクトリのパスを返します。

#### `should_process_file(file_path, base_path, gitignore_spec)`
この関数は、ファイルが.gitignoreのパターンに該当するかをチェックします。

```python
def should_process_file(file_path, base_path, gitignore_spec):
    if gitignore_spec is None:
        return True
    relative_path = os.path.relpath(file_path, base_path)
    return not gitignore_spec.match_file(relative_path)
```

gitignore_specがNoneでない場合、ファイルの相対パスがgitignoreパターンにマッチするかをチェックし、マッチしない場合にTrueを返します。

#### `analyze_with_bedrock(bedrock_runtime, code_content, file_path)`
この関数は、Bedrock APIを使用してコードの解析を実行します。

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
        # ... (エラー処理と再試行ロジック)
        return final_output
    except Exception as e:
        logger.error(f"Error analyzing {file_path}: {str(e)}")
        return None
```

この関数は、Bedrock APIを呼び出してコード解析を行い、結果を返します。エラーが発生した場合は再試行ロジックを実装しています。

#### `process_directory(input_dir, output_dir, target_extensions)`
この関数は、指定されたディレクトリ内のファイルを処理します。

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

この関数は、指定されたディレクトリ内のファイルを再帰的に処理し、各ファイルに対して解析を実行し、結果を保存します。

### メイン実行関数
`main()` 関数は、環境変数から設定を読み込み、`process_directory()` 関数を呼び出してディレクトリ処理を実行します。

## 3. 動作仕様
1. スクリプトは指定された入力ディレクトリ内のファイルを再帰的に探索します。
2. 各ファイルに対して、以下の処理を行います：
   a. ファイルの拡張子が指定された対象拡張子リストに含まれているかチェック
   b. 最も近い.gitignoreファイルを探し、ファイルがgitignoreパターンにマッチするかチェック
   c. Bedrock APIを使用してファイルの内容を解析
   d. 解析結果を指定された出力ディレクトリにMarkdownファイルとして保存
3. 処理結果（成功したファイル、失敗したファイル、エラー内容など）をJSON形式で出力します。
4. エラーが発生した場合、ログに記録し、可能な場合は処理を継続します。

このスクリプトは、大規模なコードベースの自動ドキュメント生成や、コード解析タスクの自動化に適しています。