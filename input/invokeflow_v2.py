import json
import boto3
import os
from urllib.parse import unquote_plus
from botocore.exceptions import ClientError
import time

def is_target_file(file_name):
    """処理対象の拡張子かどうかをチェック"""
    # 環境変数から対象拡張子を取得
    target_extensions_str = os.environ.get('TARGET_EXTENSIONS')
    target_extensions = [ext.strip() for ext in target_extensions_str.split(',')]
    
    return any(file_name.lower().endswith(ext) for ext in target_extensions)

def analyze_with_bedrock(bedrock_runtime, code_content, file_path):
    """Bedrockを使用してコードを解析"""
    print(f"Analyzing: {file_path}")
    
    try:
        try:
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
            
            final_output = ""
            for event in flow_response['responseStream']:
                if 'flowOutputEvent' in event:
                    output_content = event['flowOutputEvent']['content'].get('document', '')
                    if output_content:
                        final_output = output_content

        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code in ['AccessDeniedException', 'internalServerException']:
                # リトライ可能なエラーの場合
                for attempt in range(3):  # 最大3回リトライ
                    try:
                        time.sleep(2 ** attempt)  # 指数バックオフ
                        
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
                        
                        final_output = ""
                        for event in flow_response['responseStream']:
                            if 'flowOutputEvent' in event:
                                output_content = event['flowOutputEvent']['content'].get('document', '')
                                if output_content:
                                    final_output = output_content
                                    
                        if final_output:
                            break
                            
                    except ClientError as retry_error:
                        if attempt == 2:  # 最後のリトライでも失敗
                            raise retry_error
                        continue
            else:
                raise e

        if not final_output:
            raise Exception("Empty output from Bedrock")

        return final_output

    except Exception as e:
        print(f"Error analyzing {file_path}: {str(e)}")
        return None

def list_files_in_folder(s3, bucket, prefix):
    """フォルダ内のファイルを再帰的に取得"""
    files = []
    paginator = s3.get_paginator('list_objects_v2')
    
    try:
        for page in paginator.paginate(Bucket=bucket, Prefix=prefix):
            if 'Contents' in page:
                for obj in page['Contents']:
                    if not obj['Key'].endswith('/'):  # フォルダを除外
                        files.append(obj['Key'])
    except Exception as e:
        print(f"Error listing files: {str(e)}")
        raise
        
    return files

def lambda_handler(event, context):
    # 必須環境変数のチェック
    required_envs = ['FLOW_ID', 'FLOW_ALIAS_ID', 'TARGET_EXTENSIONS']
    missing_envs = [env for env in required_envs if not os.environ.get(env)]
    if missing_envs:
        error_msg = f"Missing required environment variables: {', '.join(missing_envs)}"
        print(error_msg)
        return {
            'statusCode': 500,
            'body': json.dumps({'error': error_msg})
        }

    s3 = boto3.client('s3')
    bedrock_runtime = boto3.client(
        service_name='bedrock-agent-runtime',
        region_name='ap-northeast-1'
    )
    
    try:
        # S3イベントからフォルダ情報を取得
        bucket = event['Records'][0]['s3']['bucket']['name']
        key = unquote_plus(event['Records'][0]['s3']['object']['key'])
        
        # フォルダパスを取得（末尾のファイル名を除去）
        folder_path = os.path.dirname(key) + '/'
        print(f"Processing folder: {folder_path}")
        
        # フォルダ内のすべてのファイルを取得
        files = list_files_in_folder(s3, bucket, folder_path)
        print(f"Found {len(files)} files in folder")
        
        results = []
        for file_path in files:
            try:
                if not is_target_file(file_path):
                    print(f"Skipping non-target file: {file_path}")
                    continue
                    
                print(f"Processing file: {file_path}")
                
                # ファイルを読み込む
                response = s3.get_object(Bucket=bucket, Key=file_path)
                code_content = response['Body'].read().decode('utf-8')
                
                # 出力ファイル名を定義
                file_name = os.path.basename(file_path)
                output_key = f'output/{os.path.splitext(file_name)[0]}.md'
                
                # Bedrockで解析
                analysis_result = analyze_with_bedrock(bedrock_runtime, code_content, file_path)
                
                if analysis_result:
                    # S3に保存
                    s3.put_object(
                        Bucket=bucket,
                        Key=output_key,
                        Body=analysis_result.encode('utf-8'),
                        ContentType='text/markdown'
                    )
                    
                    results.append({
                        'file': file_path,
                        'output': output_key,
                        'status': 'success'
                    })
                    print(f"Analysis saved to {bucket}/{output_key}")
                else:
                    results.append({
                        'file': file_path,
                        'status': 'failed',
                        'error': 'Analysis failed'
                    })
                    
            except Exception as e:
                print(f"Error processing file {file_path}: {str(e)}")
                results.append({
                    'file': file_path,
                    'status': 'failed',
                    'error': str(e)
                })
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Folder processing complete',
                'results': results
            })
        }
        
    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback
        print("Details:", traceback.format_exc())
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': str(e),
                'trace': traceback.format_exc()
            })
        }