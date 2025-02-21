# コード解析ドキュメント

## 1. 概要
このLambda関数は、S3バケット内の特定のフォルダにあるファイルを処理し、Bedrock APIを使用してコード解析を行います。解析結果はMarkdownファイルとして同じS3バケット内の'output/'フォルダに保存されます。

## 2. 詳細説明

### 環境変数
関数は以下の環境変数を使用します：
- `FLOW_ID`: Bedrock flowのID
- `FLOW_ALIAS_ID`: Bedrock flow aliasのID
- `TARGET_EXTENSIONS`: 処理対象のファイル拡張子（カンマ区切り）

### 主要な関数

1. `is_target_file(file_name)`
   - 引数のファイル名が処理対象の拡張子かどうかをチェックします。
   - 環境変数`TARGET_EXTENSIONS`から対象拡張子のリストを取得し、ファイル名と照合します。

2. `analyze_with_bedrock(bedrock_runtime, code_content, file_path)`
   - Bedrock APIを使用してコードを解析します。
   - エラー発生時は最大3回まで指数バックオフを使用してリトライします。

   ```python
   flow_response = bedrock_runtime.invoke_flow(
       flowIdentifier=os.environ['FLOW_ID'],
       flowAliasIdentifier=os.environ['FLOW_ALIAS_ID'],
       inputs=[{
           'content': {
               'document': code_content
           },
           'nodeName': 'FlowInputNode',
           'nodeOutputName': 'document'
       }]
   )
   ```

3. `list_files_in_folder(s3, bucket, prefix)`
   - S3バケット内の指定されたプレフィックス（フォルダ）以下のファイルを再帰的に取得します。
   - S3のページネーションを使用して大量のファイルにも対応します。

4. `lambda_handler(event, context)`
   - Lambda関数のメインハンドラー。S3イベントを受け取り、処理を開始します。
   - フォルダ内の各ファイルに対して以下の処理を行います：
     1. 対象拡張子かチェック
     2. ファイルの内容を読み込み
     3. Bedrockで解析
     4. 結果をS3に保存

### エラーハンドリング
- 必須環境変数のチェック
- ファイル処理中のエラーをキャッチし、個別に報告
- 全体的な例外をキャッチし、詳細なトレースバックを含むエラーレスポンスを返す

## 3. 動作仕様
1. S3バケットの特定フォルダにファイルが追加されると、Lambda関数がトリガーされます。
2. 関数は、トリガーとなったフォルダ内のすべてのファイルをリストアップします。
3. 各ファイルに対して：
   - 対象拡張子かどうかをチェック
   - 対象の場合、ファイルの内容を読み込み
   - Bedrock APIを使用してコード解析を実行
   - 解析結果をMarkdownファイルとしてS3の'output/'フォルダに保存
4. 処理結果（成功/失敗）を含むサマリーをJSON形式で返します。

この関数は、大量のファイルを効率的に処理し、エラーに対して堅牢な設計になっています。Bedrockの一時的な障害に対してもリトライメカニズムを実装しており、信頼性の高い処理を実現しています。