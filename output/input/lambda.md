# コード解析ドキュメント

## 1. 概要
このPythonスクリプトは、指定されたディレクトリ内のファイルを処理し、Amazon Bedrock APIを使用してコード解析を行うものです。主な機能は以下の通りです：

- 指定されたディレクトリ内のファイルを再帰的に探索
- .gitignoreファイルに基づいてファイルをフィルタリング
- 特定の拡張子を持つファイルのみを処理
- Amazon Bedrock APIを使用してコードを解析
- 解析結果をMarkdownファイルとして出力

## 2. 詳細説明

### 主要な関数

1. `find_nearest_gitignore(file_path)`:
   - 指定されたファイルパスから最も近い.gitignoreファイルを探索します。
   - 戻り値: .gitignoreの内容と、その.gitignoreファイルが存在するディレクトリのパス

2. `should_process_file(file_path, base_path, gitignore_spec)`:
   - ファイルが.gitignoreのパターンに該当するかチェックします。
   - 戻り値: ファイルを処理すべきかどうかのブール値

3. `generate_output_path(input_path, output_dir)`:
   - 入力ファイルパスから出力ファイルパスを生成します。
   - 戻り値: 出力ファイルの完全パス

4. `analyze_with_bedrock(bedrock_runtime, code_content, file_path)`:
   - Bedrock APIを使用してコードの解析を実行します。
   - エラー発生時は最大3回まで再試行します。
   - 戻り値: 解析結果の文字列

5. `process_directory(input_dir, output_dir, target_extensions)`:
   - 指定されたディレクトリ内のファイルを処理します。
   - .gitignoreに基づくフィルタリング、Bedrock APIによる解析、結果の保存を行います。
   - 戻り値: 処理結果の概要を含む辞書

6. `main()`:
   - スクリプトのエントリーポイントとなる関数です。
   - 環境変数から設定を読み込み、`process_directory`を呼び出します。

### 重要なコンポーネント

1. ロギング設定:
   ```python
   logger = logging.getLogger()
   logger.setLevel(logging.INFO)
   ```
   詳細なログ出力を可能にします。

2. Bedrock クライアントの初期化:
   ```python
   bedrock_runtime = boto3.client(
       service_name='bedrock-agent-runtime',
       region_name='ap-northeast-1'
   )
   ```
   Amazon Bedrock APIを使用するためのクライアントを初期化します。

3. gitignore処理:
   ```python
   patterns = [line.strip() for line in gitignore_content.splitlines()
              if line.strip() and not line.startswith('#')]
   gitignore_spec = PathSpec.from_lines(GitWildMatchPattern, patterns)
   ```
   .gitignoreファイルの内容を解析し、PathSpecオブジェクトを作成してファイルフィルタリングに使用します。

4. Bedrock API呼び出し:
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
   Bedrock APIを呼び出してコード解析を実行します。エラー発生時は再試行ロジックが実装されています。

5. 環境変数の使用:
   ```python
   target_extensions = [ext.strip() for ext in os.environ.get('TARGET_EXTENSIONS', '.py,.js,.java,.cpp').split(',')]
   ```
   環境変数から対象とするファイル拡張子を読み込みます。

## 3. 動作仕様

1. スクリプトは`main()`関数から開始します。
2. 入力ディレクトリ（"input"）と出力ディレクトリ（"output"）が設定されます。
3. 環境変数から対象とするファイル拡張子のリストを取得します。
4. `process_directory()`関数が呼び出され、以下の処理が行われます：
   a. 入力ディレクトリ内のファイルを再帰的に探索
   b. 各ファイルに対して:
      - .gitignoreパターンに基づくフィルタリング
      - 指定された拡張子を持つファイルのみを処理
      - Bedrock APIを使用したコード解析
      - 解析結果をMarkdownファイルとして出力ディレクトリに保存
5. 処理結果の概要がJSON形式で出力されます。
6. エラーが発生した場合、ログに記録され、エラーコードが返されます。

このスクリプトは、大規模なコードベースの自動解析や、コードレビューの補助ツールとして活用できます。