# コード解析ドキュメント

## 1. 概要
このPythonスクリプトは、指定されたディレクトリ内のファイルを処理し、Bedrock APIを使用してコード解析を行うプログラムです。主な機能は以下の通りです：

- 指定されたディレクトリ内のファイルを再帰的に探索
- .gitignoreファイルに基づいてファイルをフィルタリング
- 特定の拡張子を持つファイルのみを処理
- Bedrock APIを使用してコードの解析を実行
- 解析結果をMarkdownファイルとして出力

## 2. 詳細説明

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
   - エラー発生時は最大3回まで再試行します。
   - 戻り値: 解析結果の文字列、エラー時はNone

5. `process_directory(input_dir, output_dir, target_extensions)`
   - 指定されたディレクトリ内のファイルを処理します。
   - .gitignoreに基づくフィルタリング、Bedrock APIによる解析、結果の保存を行います。
   - 戻り値: 処理結果の概要（辞書形式）

6. `main()`
   - プログラムのエントリーポイントとなる関数です。
   - 環境変数から設定を読み込み、`process_directory`を呼び出します。

### 重要なコンポーネント

1. ロギング設定
   ```python
   logger = logging.getLogger()
   logger.setLevel(logging.INFO)
   ```
   - ログレベルをINFOに設定し、詳細な実行ログを出力します。

2. Bedrock クライアントの初期化
   ```python
   bedrock_runtime = boto3.client(
       service_name='bedrock-agent-runtime',
       region_name='ap-northeast-1'
   )
   ```
   - AWS Bedrock APIを使用するためのクライアントを初期化します。

3. .gitignore処理
   ```python
   patterns = [line.strip() for line in gitignore_content.splitlines()
              if line.strip() and not line.startswith('#')]
   gitignore_spec = PathSpec.from_lines(GitWildMatchPattern, patterns)
   ```
   - .gitignoreファイルの内容を解析し、PathSpecオブジェクトを作成してファイルフィルタリングに使用します。

4. Bedrock API呼び出し
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
   - Bedrock APIを呼び出してコード解析を実行します。
   - エラー発生時は最大3回まで再試行します。

5. 環境変数の使用
   ```python
   target_extensions = [ext.strip() for ext in os.environ.get('TARGET_EXTENSIONS', '.py,.js,.java,.cpp').split(',')]
   ```
   - 環境変数から対象とするファイル拡張子を読み込みます。

## 3. 動作仕様

1. プログラムは`main()`関数から開始します。
2. 入力ディレクトリ（"input"）と出力ディレクトリ（"output"）を設定します。
3. 環境変数から対象とするファイル拡張子を読み込みます。
4. `process_directory()`関数を呼び出して、ディレクトリ内のファイル処理を開始します。
5. 各ファイルに対して以下の処理を行います：
   a. .gitignoreファイルに基づいてファイルをフィルタリングします。
   b. 指定された拡張子を持つファイルのみを処理します。
   c. Bedrock APIを使用してコード解析を実行します。
   d. 解析結果をMarkdownファイルとして出力ディレクトリに保存します。
6. 処理結果の概要をJSON形式で出力します。

このプログラムは、大規模なコードベースに対して自動的にコード解析を行い、ドキュメントを生成するのに適しています。エラーハンドリングやリトライメカニズムも実装されており、堅牢性が高いです。