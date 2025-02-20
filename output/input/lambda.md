# コード解析ドキュメント

## 1. 概要
このPythonスクリプトは、指定されたディレクトリ内のコードファイルを解析し、Bedrock APIを使用して各ファイルの解析結果をMarkdownファイルとして出力するツールです。主な機能には、.gitignoreパターンに基づくファイルのフィルタリング、Bedrock APIを使用したコード解析、エラー処理とリトライロジックが含まれています。

## 2. 詳細説明

### 主要なライブラリとモジュール
- `json`: JSON形式のデータ処理に使用
- `os`: ファイルシステム操作に使用
- `pathspec`: .gitignoreパターンの処理に使用
- `logging`: ログ出力の管理に使用
- `boto3`: AWS Bedrock APIとの通信に使用
- `time`: リトライ時の待機時間制御に使用

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
この関数は、指定されたファイルパスから最も近い.gitignoreファイルを探し、その内容と見つかったディレクトリのパスを返します。

#### `should_process_file(file_path, base_path, gitignore_spec)`
ファイルが.gitignoreのパターンに該当するかチェックします。
```python
def should_process_file(file_path, base_path, gitignore_spec):
    if gitignore_spec is None:
        return True
    relative_path = os.path.relpath(file_path, base_path)
    return not gitignore_spec.match_file(relative_path)
```
この関数は、指定されたファイルが.gitignoreパターンにマッチするかどうかを判断し、処理すべきかどうかをブール値で返します。

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
この関数は、Bedrock APIを呼び出してコードの解析を行い、結果を返します。エラー発生時にはリトライロジックも実装されています。

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

### メイン実行関数
```python
def main():
    input_dir = "input"
    output_dir = "output"
    target_extensions = [ext.strip() for ext in os.environ.get('TARGET_EXTENSIONS', '.py,.js,.java,.cpp').split(',')]
    os.makedirs(output_dir, exist_ok=True)
    try:
        result = process_directory(input_dir, output_dir, target_extensions)
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return 0
    except Exception as e:
        logger.error(f"Error in main: {str(e)}")
        return 1
```
メイン関数は、環境変数から設定を読み込み、`process_directory`関数を呼び出してディレクトリ処理を実行します。処理結果はJSON形式で出力されます。

## 3. 動作仕様
1. スクリプトは、指定された入力ディレクトリ内のファイルを再帰的に走査します。
2. 各ファイルに対して、以下の処理を行います：
   a. ファイルの拡張子が対象拡張子リストに含まれているかチェック
   b. 最も近い.gitignoreファイルを探し、そのパターンに基づいてファイルをフィルタリング
   c. Bedrock APIを使用してコードの解析を実行
   d. 解析結果を指定された出力ディレクトリにMarkdownファイルとして保存
3. 処理中のエラーはログに記録され、可能な場合はリトライが行われます。
4. すべてのファイルの処理が完了すると、総処理ファイル数と各ファイルの処理結果を含む要約がJSON形式で出力されます。

このスクリプトは、大規模なコードベースの自動ドキュメント生成や、コード解析タスクの自動化に適しています。エラー処理とリトライメカニズムにより、安定した動作が期待できます。