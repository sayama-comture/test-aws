# コード解析ドキュメント

## 1. 概要
このLambda関数は、S3バケット内の特定のフォルダにあるファイルを処理し、Bedrock AIを使用してコード解析を行います。解析結果はMarkdownファイルとして同じS3バケット内の'output/'フォルダに保存されます。

## 2. 詳細説明

### 環境変数
関数は以下の環境変数を使用します：
- `FLOW_ID`: BedrockのフローID
- `FLOW_ALIAS_ID`: BedrockのフローエイリアスID
- `TARGET_EXTENSIONS`: 処理対象のファイル拡張子（カンマ区切り）

### 主要な関数

1. `is_target_file(file_name)`
   - 指定されたファイルが処理対象の拡張子かどうかをチェックします。
   ```python
   def is_target_file(file_name):
       target_extensions_str = os.environ.get('TARGET_EXTENSIONS')
       target_extensions = [ext.strip() for ext in target_extensions_str.split(',')]
       return any(file_name.lower().endswith(ext) for ext in target_extensions)
   ```

2. `analyze_with_bedrock(bedrock_runtime, code_content, file_path)`
   - Bedrock AIを使用してコードを解析します。
   - エラー発生時は最大3回リトライします（指数バックオフ使用）。
   ```python
   def analyze_with_bedrock(bedrock_runtime, code_content, file_path):
       try:
           flow_response = bedrock_runtime.invoke_flow(
               flowIdentifier=os.environ['FLOW_ID'],
               flowAliasIdentifier=os.environ['FLOW_ALIAS_ID'],
               inputs=[{
                   'content': {'document': code_content},
                   'nodeName': 'FlowInputNode',
                   'nodeOutputName': 'document'
               }]
           )
           # 省略: レスポンスの処理とリトライロジック
   ```

3. `list_files_in_folder(s3, bucket, prefix)`
   - S3バケット内の指定されたフォルダ内のファイルを再帰的に取得します。
   ```python
   def list_files_in_folder(s3, bucket, prefix):
       files = []
       paginator = s3.get_paginator('list_objects_v2')
       for page in paginator.paginate(Bucket=bucket, Prefix=prefix):
           if 'Contents' in page:
               for obj in page['Contents']:
                   if not obj['Key'].endswith('/'):
                       files.append(obj['Key'])
       return files
   ```

4. `lambda_handler(event, context)`
   - Lambda関数のメインハンドラー。
   - S3イベントからバケットとキー情報を取得し、フォルダ内のファイルを処理します。
   - 各ファイルに対して以下の処理を行います：
     1. ファイルが対象拡張子かチェック
     2. ファイルの内容を読み込み
     3. Bedrockで解析
     4. 解析結果をS3に保存
   - 処理結果をJSONで返します。

### エラーハンドリング
- 必須環境変数のチェック
- 各ファイル処理時の例外キャッチ
- 全体的な例外キャッチとスタックトレースのログ出力

## 3. 動作仕様
1. S3バケット内の特定フォルダにファイルが追加されると、Lambda関数がトリガーされます。
2. 関数は、そのフォルダ内のすべてのファイルをリストアップします。
3. 各ファイルに対して：
   - 対象拡張子かどうかをチェック
   - 対象の場合、ファイルの内容を読み込み
   - Bedrock AIを使用してコード解析を実行
   - 解析結果をMarkdownファイルとしてS3の'output/'フォルダに保存
4. 処理結果（成功/失敗）を含むJSONレスポンスを返します。

この関数は、大量のコードファイルを自動的に解析し、その結果を整理された形で保存することができます。エラーハンドリングとリトライメカニズムにより、一時的な問題にも対応できる堅牢な設計となっています。