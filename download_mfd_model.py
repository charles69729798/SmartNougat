#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MFD YOLO 모델 다운로드 스크립트
"""

import os
import sys

# huggingface_hub 설치 확인
try:
    from huggingface_hub import snapshot_download
except ImportError:
    print("huggingface_hub 설치 중...")
    os.system(f"{sys.executable} -m pip install huggingface_hub")
    from huggingface_hub import snapshot_download

print("PDF-Extract-Kit MFD YOLO 모델 다운로드 시작...")

try:
    # 모델 다운로드
    local_dir = snapshot_download(
        repo_id='opendatalab/pdf-extract-kit-1.0',
        local_dir='./pdf-extract-kit-models',
        allow_patterns='models/MFD/YOLO/*',
        resume_download=True
    )
    
    print(f"모델이 다음 위치에 다운로드되었습니다: {local_dir}")
    
    # 다운로드된 파일 확인
    mfd_path = os.path.join(local_dir, "models", "MFD", "YOLO")
    if os.path.exists(mfd_path):
        files = os.listdir(mfd_path)
        print(f"다운로드된 파일들: {files}")
        
        # weights.pt 또는 yolo_v8_ft.pt 파일 찾기
        weights_found = False
        for filename in files:
            if filename.endswith('.pt'):
                weights_path = os.path.join(mfd_path, filename)
                print(f"MFD 모델 파일 발견: {weights_path}")
                weights_found = True
                
                # weights.pt로 복사 (필요한 경우)
                if filename != "weights.pt":
                    weights_dest = os.path.join(mfd_path, "weights.pt")
                    import shutil
                    try:
                        shutil.copy2(weights_path, weights_dest)
                        print(f"weights.pt로 복사 완료: {weights_dest}")
                    except Exception as e:
                        print(f"복사 중 오류: {e}")
                
        if not weights_found:
            print("YOLO 모델 파일(.pt)을 찾을 수 없습니다.")
            
except Exception as e:
    print(f"오류 발생: {e}")
    sys.exit(1)