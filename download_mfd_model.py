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
        
        # weights.pt 파일 찾기
        weights_path = os.path.join(mfd_path, "weights.pt")
        if os.path.exists(weights_path):
            print(f"MFD 모델 weights 경로: {weights_path}")
            
            # smartnougat_standalone.py 수정 안내
            print("\n다음 경로를 smartnougat_standalone.py의 possible_paths에 추가하세요:")
            print(f'"{os.path.abspath(weights_path)}"')
        else:
            print("weights.pt 파일을 찾을 수 없습니다.")
            
except Exception as e:
    print(f"오류 발생: {e}")
    sys.exit(1)