# コード解析ドキュメント

## 1. 概要
このPythonスクリプトは、指定されたディレクトリ内のコードファイルを解析し、Bedrock APIを使用して各ファイルの解析結果をMarkdownファイルとして出力するツールです。主な機能には、.gitignoreパターンに基づくファイルのフィルタリング、Bedrock APIを使用したコード解析、エラー処理とリトライロジックが含まれています。

## 2. 詳細説明

### 主要なライブラリとモジュール
- `json`: JSON データの処理
- `os`: ファイルシステム操作
- `pathspec`: .gitignoreパターンの処理
- `logging`: ログ記録
- `boto3`: AWS SDK for Python
- `time`: 時間関連の操作

### 重要な関数

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

この関数は、ファイルパスから親ディレクトリを遡って.gitignoreファイルを探し、見つかった場合はその内容と親ディレクトリのパスを返します。

#### `should_process_file(file_path, base_path, gitignore_spec)`
この関数は、ファイルが.gitignoreのパターンに該当するかをチェックします。

```python
def should_process_file(file_path, base_path, gitignore_spec):
    if gitignore_spec is None:
        return True
    relative_path = os.path.relpath(file_path, base_path)
    if gitignore_spec.match_file(relative_path):
        return False
    return True
```

gitignore_specがNoneでない場合、相対パスを使用してファイルが.gitignoreパターンにマッチするかを確認します。

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
        # ... (エラー処理とリトライロジック)
        return final_output
    except Exception as e:
        logger.error(f"Error analyzing {file_path}: {str(e)}")
        return None
```

この関数は、Bedrock APIを呼び出してコード解析を行い、結果を返します。エラーが発生した場合は最大3回のリトライを行います。

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

この関数は、入力ディレクトリ内のすべてのファイルを走査し、対象の拡張子を持つファイルを処理します。各ファイルに対して.gitignoreチェック、Bedrock APIによる解析、結果の保存を行います。

### メイン実行関数
`main()` 関数は、環境変数から設定を読み込み、`process_directory()` 関数を呼び出してディレクトリ処理を実行します。

## 3. 動作仕様
1. 環境変数から入力ディレクトリ、出力ディレクトリ、対象ファイル拡張子を読み込みます。
2. 入力ディレクトリ内のファイルを再帰的に走査します。
3. 各ファイルに対して:
   a. ファイル拡張子が対象リストに含まれているかチェックします。
   b. 最も近い.gitignoreファイルを探し、ファイルが無視パターンにマッチするかチェックします。
   c. Bedrock APIを使用してコード解析を実行します。
   d. 解析結果をMarkdownファイルとして出力ディレクトリに保存します。
4. 処理結果の要約（総処理ファイル数、成功/失敗状況）をJSON形式で出力します。

このスクリプトは、大規模なコードベースの自動ドキュメント生成や、コードレビューの補助ツールとして活用できます。