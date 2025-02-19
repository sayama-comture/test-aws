import json
import os
from pathspec import PathSpec
from pathspec.patterns import GitWildMatchPattern
import logging
import boto3
import time
from botocore.exceptions import ClientError

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize Bedrock client
bedrock_runtime = boto3.client(
    service_name='bedrock-agent-runtime',
    region_name='ap-northeast-1'
)

def find_nearest_gitignore(file_path):
    """
    ファイルパスから最も近い.gitignoreファイルを探索します。
    """
    current_dir = os.path.dirname(os.path.abspath(file_path))
    
    while current_dir:
        gitignore_path = os.path.join(current_dir, '.gitignore')
        logger.info(f"Looking for .gitignore at: {gitignore_path}")
        
        if os.path.exists(gitignore_path):
            with open(gitignore_path, 'r', encoding='utf-8') as f:
                content = f.read()
            logger.info(f"Found .gitignore at {gitignore_path}")
            return content, current_dir
            
        parent_dir = os.path.dirname(current_dir)
        if parent_dir == current_dir:
            break
        current_dir = parent_dir
    
    logger.info("No .gitignore found in any parent directory.")
    return None, None

def should_process_file(file_path, base_path, gitignore_spec):
    """
    ファイルが.gitignoreのパターンに該当するかチェックする関数です。
    """
    if gitignore_spec is None:
        return True

    relative_path = os.path.relpath(file_path, base_path)
    logger.info(f"Checking gitignore for path: {relative_path}")

    if gitignore_spec.match_file(relative_path):
        logger.info(f"Matched gitignore pattern: {relative_path}")
        return False

    return True

def generate_output_path(input_path, output_dir):
    """
    入力ファイルパスから出力ファイルパスを生成する関数です。
    """
    rel_path = os.path.relpath(input_path)
    base_name = os.path.splitext(os.path.basename(input_path))[0]
    dir_path = os.path.dirname(rel_path)
    
    output_path = os.path.join(output_dir, dir_path) if dir_path else output_dir
    os.makedirs(output_path, exist_ok=True)
    
    return os.path.join(output_path, f"{base_name}.md")

def analyze_with_bedrock(bedrock_runtime, code_content, file_path):
    """
    Bedrock APIを使用してコードの解析を実行する関数です。
    """
    logger.info(f"Analyzing: {file_path}")

    try:
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

            final_output = ""
            for event in flow_response['responseStream']:
                if 'flowOutputEvent' in event:
                    output_content = event['flowOutputEvent']['content'].get('document', '')
                    if output_content:
                        final_output = output_content

        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code in ['AccessDeniedException', 'internalServerException']:
                for attempt in range(3):
                    try:
                        time.sleep(2 ** attempt)
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

                        final_output = ""
                        for event in flow_response['responseStream']:
                            if 'flowOutputEvent' in event:
                                output_content = event['flowOutputEvent']['content'].get('document', '')
                                if output_content:
                                    final_output = output_content

                        if final_output:
                            break

                    except ClientError as retry_error:
                        if attempt == 2:
                            raise retry_error
                        continue
            else:
                raise e

        if not final_output:
            raise Exception("Empty output from Bedrock")

        return final_output

    except Exception as e:
        logger.error(f"Error analyzing {file_path}: {str(e)}")
        return None

def process_directory(input_dir, output_dir, target_extensions):
    """
    指定されたディレクトリ内のファイルを処理する関数です。
    """
    processed_files = set()
    all_results = []

    for root, _, files in os.walk(input_dir):
        for file_name in files:
            file_path = os.path.join(root, file_name)
            
            if file_path in processed_files:
                logger.info(f"Skipping already processed file: {file_path}")
                continue

            if not any(file_name.lower().endswith(ext) for ext in target_extensions):
                logger.info(f"Skipping non-target extension file: {file_path}")
                continue

            gitignore_content, base_path = find_nearest_gitignore(file_path)
            if gitignore_content:
                patterns = [line.strip() for line in gitignore_content.splitlines()
                           if line.strip() and not line.startswith('#')]
                gitignore_spec = PathSpec.from_lines(GitWildMatchPattern, patterns)

                if not should_process_file(file_path, base_path, gitignore_spec):
                    logger.info(f"File {file_path} matches gitignore pattern, skipping")
                    continue

            processed_files.add(file_path)

            try:
                logger.info(f"Processing file: {file_path}")
                output_path = generate_output_path(file_path, output_dir)

                with open(file_path, 'r', encoding='utf-8') as f:
                    code_content = f.read()

                analysis_result = analyze_with_bedrock(bedrock_runtime, code_content, file_path)

                if analysis_result:
                    os.makedirs(os.path.dirname(output_path), exist_ok=True)
                    with open(output_path, 'w', encoding='utf-8') as f:
                        f.write(analysis_result)

                    all_results.append({
                        'file': file_path,
                        'output': output_path,
                        'status': 'success'
                    })
                    logger.info(f"Analysis saved to {output_path}")
                else:
                    all_results.append({
                        'file': file_path,
                        'status': 'failed',
                        'error': 'Analysis failed'
                    })

            except Exception as e:
                logger.error(f"Error processing file {file_path}: {str(e)}")
                all_results.append({
                    'file': file_path,
                    'status': 'failed',
                    'error': str(e)
                })

    return {
        'message': 'Processing complete',
        'total_processed': len(processed_files),
        'results': all_results
    }

def main():
    """
    メイン実行関数
    """
    # 環境変数から設定を読み込み
    input_dir = "input"
    output_dir = "output"
    target_extensions = [ext.strip() for ext in os.environ.get('TARGET_EXTENSIONS', '.py,.js,.java,.cpp').split(',')]

    # 出力ディレクトリの作成
    os.makedirs(output_dir, exist_ok=True)

    try:
        # ディレクトリの処理を実行
        result = process_directory(input_dir, output_dir, target_extensions)
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return 0
    except Exception as e:
        logger.error(f"Error in main: {str(e)}")
        return 1

if __name__ == "__main__":
    exit(main())