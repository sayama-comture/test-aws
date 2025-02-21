# コード解析ドキュメント

## 1. 概要
このLambda関数は、S3バケット内の特定のフォルダにあるファイルを処理し、Bedrock Agentを使用してコード解析を行います。解析結果はMarkdownファイルとして同じS3バケット内の'output/'フォルダに保存されます。

## 2. 詳細説明

### 環境変数
関数は以下の環境変数を使用します：
- `FLOW_ID`: Bedrock Agent Flowの識別子
- `FLOW_ALIAS_ID`: Bedrock Agent Flowのエイリアス識別子
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
この関数はBedrockを使用してコードを解析します。主な特徴は以下の通りです：
- Bedrock Agent Flowを呼び出してコード解析を行います。
- エラーが発生した場合、最大3回のリトライを行います（指数バックオフ方式）。
- 解析結果がない場合は例外を発生させます。

#### list_files_in_folder(s3, bucket, prefix)
```python
def list_files_in_folder(s3, bucket, prefix):
    files = []
    paginator = s3.get_paginator('list_objects_v2')
    
    try:
        for page in paginator.paginate(Bucket=bucket, Prefix=prefix):
            if 'Contents' in page:
                for obj in page['Contents']:
                    if not obj['Key'].endswith('/'):
                        files.append(obj['Key'])
    except Exception as e:
        print(f"Error listing files: {str(e)}")
        raise
        
    return files
```
この関数は、指定されたS3バケットとプレフィックス（フォルダパス）内のすべてのファイルを再帰的に取得します。ページネーションを使用して大量のファイルを効率的に処理します。

#### lambda_handler(event, context)
メイン関数であり、以下の手順で処理を行います：
1. 必要な環境変数が設定されているかチェックします。
2. S3イベントからバケット名とキー（ファイルパス）を取得します。
3. フォルダ内のすべてのファイルをリストアップします。
4. 各ファイルに対して：
   - 対象拡張子かどうかをチェック
   - ファイルの内容を読み込み
   - Bedrockを使用してコード解析
   - 解析結果をS3の'output/'フォルダに保存
5. 処理結果をJSON形式で返します。

エラーハンドリングが実装されており、各ステップでエラーが発生した場合も適切に処理されます。

## 3. 動作仕様
1. S3バケット内の特定フォルダにファイルがアップロードされると、このLambda関数がトリガーされます。
2. 関数は、アップロードされたファイルが含まれるフォルダ内のすべてのファイルを処理します。
3. 各ファイルに対して、以下の処理を行います：
   a. ファイルの拡張子が対象拡張子リストに含まれているかチェック
   b. 対象ファイルの場合、内容を読み込み
   c. Bedrock Agent Flowを使用してコード解析を実行
   d. 解析結果をMarkdownファイルとしてS3の'output/'フォルダに保存
4. 処理結果（成功したファイル、失敗したファイル、エラー内容など）がJSON形式で返されます。
5. エラーが発生した場合、詳細なエラー情報とスタックトレースがログに記録されます。

この関数は、大量のファイルを効率的に処理し、エラーに対して堅牢に設計されています。Bedrock Agent Flowを使用したコード解析の結果を自動的にS3に保存することで、コードレビューや文書化プロセスを効率化することができます。