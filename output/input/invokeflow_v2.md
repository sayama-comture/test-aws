# コード解析ドキュメント

## 1. 概要
このLambda関数は、S3バケット内の特定のフォルダにあるファイルを処理し、Bedrock AIを使用してコード解析を行います。解析結果はMarkdownファイルとして同じS3バケット内の'output/'フォルダに保存されます。

## 2. 詳細説明

### 環境変数
関数は以下の環境変数を使用します：
- `FLOW_ID`: Bedrock FlowのID
- `FLOW_ALIAS_ID`: Bedrock Flow AliasのID
- `TARGET_EXTENSIONS`: 処理対象のファイル拡張子（カンマ区切り）

### 主要な関数

#### is_target_file(file_name)
```python
def is_target_file(file_name):
    target_extensions_str = os.environ.get('TARGET_EXTENSIONS')
    target_extensions = [ext.strip() for ext in target_extensions_str.split(',')]
    return any(file_name.lower().endswith(ext) for ext in target_extensions)
```
この関数は、与えられたファイル名が処理対象の拡張子を持つかどうかをチェックします。環境変数`TARGET_EXTENSIONS`から対象拡張子のリストを取得し、ファイル名がいずれかの拡張子で終わるかを確認します。

#### analyze_with_bedrock(bedrock_runtime, code_content, file_path)
この関数はBedrockを使用してコードを解析します。主な特徴：
- Bedrock FlowをAWS SDKを使用して呼び出します。
- エラーハンドリングとリトライロジックが実装されています。
- 最大3回のリトライを行い、指数バックオフを使用します。

#### list_files_in_folder(s3, bucket, prefix)
S3バケット内の指定されたプレフィックス（フォルダ）以下のファイルを再帰的にリストアップします。ページネーションを使用して大量のファイルを扱えるようになっています。

#### lambda_handler(event, context)
Lambda関数のメインハンドラーです。主な処理フロー：
1. 環境変数のチェック
2. S3イベントからバケットとキー情報を取得
3. フォルダ内のファイルをリストアップ
4. 各ファイルに対して：
   - 対象拡張子かチェック
   - ファイルの内容を読み込み
   - Bedrockで解析
   - 結果をS3に保存
5. 処理結果をまとめてレスポンス

エラーハンドリング：
- 各ステップでのエラーをキャッチし、適切にログ出力
- 全体的なtry-exceptブロックで未捕捉のエラーを処理

## 3. 動作仕様
1. S3バケット内の特定フォルダにファイルが追加されると、このLambda関数がトリガーされます。
2. 関数は、そのフォルダ内のすべてのファイルをリストアップします。
3. 各ファイルに対して：
   a. ファイルの拡張子が対象拡張子リストに含まれているかチェックします。
   b. 対象ファイルの場合、内容を読み込みます。
   c. Bedrock AIを使用してコード解析を行います。
   d. 解析結果をMarkdownファイルとして、'output/'フォルダに保存します。
4. 処理結果（成功したファイル、失敗したファイルの情報）をJSON形式でレスポンスとして返します。

注意点：
- Bedrockの呼び出しに失敗した場合、最大3回のリトライを行います。
- 環境変数が適切に設定されていない場合、関数は早期にエラーを返します。
- 大量のファイルを効率的に処理するため、S3のページネーションを使用しています。