"""

批量操作路由
"""


from flask import Blueprint, request, jsonify, send_file

from flask_login import login_required

from utils.config_manager import ConfigManager

from utils.cpa_client import CPAClient

from concurrent.futures import ThreadPoolExecutor, as_completed

from datetime import datetime

import zipfile

import io

import json


bp = Blueprint('operations', __name__, url_prefix='/api/operations')

config_manager = ConfigManager()



@bp.route('/<server_id>/download', methods=['POST'])

@login_required

def download_accounts(server_id):

    """批量下载账号"""

    server = config_manager.get_server(server_id)
    

    if not server:

        return jsonify({"error": "服务器不存在"}), 404
    

    try:

        client = CPAClient(server["base_url"], server["token"], server["name"])

        files = client.get_auth_files()
        

        # 过滤活跃账号

        active_files = [f for f in files if not f.get("disabled")]
        

        settings = config_manager.get_settings()

        max_workers = settings.get("max_workers", 10)
        

        downloaded_files = []
        

        def download_single(file_info):

            filename = file_info.get("name")

            if not filename:

                return None
            

            ok, auth_data = client.download_auth_file(filename)

            if ok and auth_data:

                return (filename, json.dumps(auth_data, indent=2))

            return None
        

        # 并发下载

        with ThreadPoolExecutor(max_workers=max_workers) as executor:

            futures = {executor.submit(download_single, f): f for f in active_files}
            

            for future in as_completed(futures):

                result = future.result()

                if result:

                    downloaded_files.append(result)
        

        # 创建 ZIP

        memory_file = io.BytesIO()

        with zipfile.ZipFile(memory_file, 'w', zipfile.ZIP_DEFLATED) as zf:

            for filename, content in downloaded_files:

                zf.writestr(filename, content)
        

        memory_file.seek(0)
        

        # 生成文件名

        date_str = datetime.now().strftime("%Y%m%d")

        zip_filename = f"{server['name']}_{date_str}_{len(downloaded_files)}.zip"
        
        return send_file(

            memory_file,

            mimetype='application/zip',

            as_attachment=True,

            download_name=zip_filename
        )
    

    except Exception as e:

        return jsonify({

            "success": False,

            "error": str(e)

        }), 500



@bp.route('/<server_id>/upload', methods=['POST'])

@login_required

def upload_accounts(server_id):

    """批量上传账号"""

    server = config_manager.get_server(server_id)
    

    if not server:

        return jsonify({"error": "服务器不存在"}), 404
    

    if 'file' not in request.files:

        return jsonify({"error": "未上传文件"}), 400
    

    file = request.files['file']
    

    if file.filename == '':

        return jsonify({"error": "文件名为空"}), 400
    

    try:

        client = CPAClient(server["base_url"], server["token"], server["name"])

        settings = config_manager.get_settings()

        max_workers = settings.get("max_workers", 10)
        

        success_count = 0

        failed_count = 0
        

        # 如果是 ZIP 文件

        if file.filename.endswith('.zip'):

            with zipfile.ZipFile(file, 'r') as zf:

                json_files = [name for name in zf.namelist() if name.endswith('.json')]
                

                def upload_single(filename):

                    try:

                        content = zf.read(filename)

                        auth_data = json.loads(content)

                        ok, msg = client.upload_auth_file(auth_data, filename)

                        return ok

                    except:

                        return False
                

                with ThreadPoolExecutor(max_workers=max_workers) as executor:

                    futures = {executor.submit(upload_single, f): f for f in json_files}
                    

                    for future in as_completed(futures):

                        if future.result():

                            success_count += 1

                        else:

                            failed_count += 1
        

        # 如果是单个 JSON 文件

        elif file.filename.endswith('.json'):

            auth_data = json.load(file)

            ok, msg = client.upload_auth_file(auth_data, file.filename)
            

            if ok:

                success_count = 1

            else:

                failed_count = 1
        

        else:

            return jsonify({"error": "不支持的文件格式"}), 400
        

        return jsonify({

            "success": True,

            "success_count": success_count,

            "failed_count": failed_count,

            "total": success_count + failed_count

        })
    

    except Exception as e:

        return jsonify({

            "success": False,

            "error": str(e)

        }), 500



@bp.route('/<server_id>/batch-revive', methods=['POST'])

@login_required

def batch_refresh(server_id):

    """批量复活 Token"""

    server = config_manager.get_server(server_id)
    

    if not server:

        return jsonify({"error": "服务器不存在"}), 404
    

    data = request.get_json()

    accounts = data.get("accounts", [])
    

    if not accounts:

        return jsonify({"error": "未指定账号"}), 400
    

    try:

        client = CPAClient(server["base_url"], server["token"], server["name"])

        settings = config_manager.get_settings()

        max_workers = settings.get("max_workers", 10)

        max_attempts = settings.get("token_revive_max_attempts", 3)
        

        results = []
        

        def revive_single(account):

            email = account.get("email", "")

            filename = account.get("filename", "")
            

            ok, message = client.revive_token(email, filename, max_attempts)
            

            return {

                "email": email,

                "filename": filename,

                "success": ok,

                "message": message

            }
        

        with ThreadPoolExecutor(max_workers=max_workers) as executor:

            futures = {executor.submit(revive_single, acc): acc for acc in accounts}
            

            for future in as_completed(futures):

                results.append(future.result())
        

        success_count = sum(1 for r in results if r["success"])

        failed_count = len(results) - success_count
        

        return jsonify({

            "success": True,

            "results": results,

            "success_count": success_count,

            "failed_count": failed_count,

            "total": len(results)

        })
    

    except Exception as e:

        return jsonify({

            "success": False,

            "error": str(e)

        }), 500

