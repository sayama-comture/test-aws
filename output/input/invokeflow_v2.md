# コード解析ドキュメント

## 1. 概要
このコードは、AWS Lambda関数として実装されており、S3バケット内のフォルダにあるファイルを処理し、Amazon Bedrockを使用してコード解析を行います。解析結果はMarkdownファイルとして同じS3バケット内の'output/'フォルダに保存されます。

## 2. 詳細説明

### 主要な関数

1. `is_target_file(file_name)`
   - 指定されたファイルが処理対象の拡張子かどうかをチェックします。
   - 環境変数`TARGET_EXTENSIONS`から対象拡張子のリストを取得します。

2. `analyze_with_bedrock(bedrock_runtime, code_content, file_path)`
   - Amazon Bedrockを使用してコードを解析します。
   - Bedrockのフローを呼び出し、結果を取得します。
   - エラー発生時は最大3回のリトライを行います（指数バックオフ使用）。

3. `list_files_in_folder(s3, bucket, prefix)`
   - S3バケット内の指定されたフォルダ（プレフィックス）にあるすべてのファイルを再帰的に取得します。

4. `lambda_handler(event, context)`
   - Lambda関数のメインハンドラーです。
   - S3イベントからバケットとキー情報を取得し、フォルダ内のファイルを処理します。

### 主要なライブラリとサービス

- `boto3`: AWS SDKを使用してS3やBedrock-agent-runtimeとやり取りします。
- `os`: 環境変数の取得やパス操作に使用します。
- `json`: JSONデータの処理に使用します。
- Amazon S3: ファイルの保存と取得に使用します。
- Amazon Bedrock: コード解析に使用します。

### 処理フロー

1. 環境変数のチェック
   ```python
   required_envs = ['FLOW_ID', 'FLOW_ALIAS_ID', 'TARGET_EXTENSIONS']
   missing_envs = [env for env in required_envs if not os.environ.get(env)]
   if missing_envs:
       # エラーレスポンスを返す
   ```

2. S3イベントからフォルダ情報を取得
   ```python
   bucket = event['Records'][0]['s3']['bucket']['name']
   key = unquote_plus(event['Records'][0]['s3']['object']['key'])
   folder_path = os.path.dirname(key) + '/'
   ```

3. フォルダ内のすべてのファイルを取得
   ```python
   files = list_files_in_folder(s3, bucket, folder_path)
   ```

4. 各ファイルを処理
   - 対象外の拡張子のファイルはスキップ
   - ファイルの内容を読み込み
   - Bedrockを使用してコード解析
   - 解析結果をS3に保存

5. 処理結果をJSONで返す

### エラーハンドリング

- 各ファイルの処理で発生したエラーは個別に捕捉され、全体の処理は続行されます。
- Bedrock APIのエラーに対しては、リトライロジックが実装されています。

## 3. 動作仕様

1. Lambda関数がS3イベントをトリガーに実行されます。
2. 指定されたS3フォルダ内のすべてのファイルがリストアップされます。
3. 各ファイルに対して以下の処理が行われます：
   a. ファイルの拡張子が対象外の場合、スキップされます。
   b. ファイルの内容がS3から読み込まれます。
   c. Amazon Bedrockを使用してコード解析が実行されます。
   d. 解析結果がMarkdownファイルとしてS3の'output/'フォルダに保存されます。
4. 全ファイルの処理結果がJSONフォーマットで返されます。

この Lambda 関数は、S3 バケット内の特定のフォルダにあるコードファイルを自動的に解析し、その結果を保存するための効率的な方法を提供します。エラーハンドリングとリトライロジックにより、耐障害性が高められています。