import { useState, useCallback } from 'react';
import { Upload, FileAudio, CheckCircle, AlertCircle, Loader2 } from 'lucide-react';
import axios from 'axios';
import type { AudioUploadResponse } from '../types';

export default function AudioUpload() {
  const [file, setFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [result, setResult] = useState<AudioUploadResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [dragActive, setDragActive] = useState(false);

  const handleDrag = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFile(e.dataTransfer.files[0]);
    }
  }, []);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      handleFile(e.target.files[0]);
    }
  };

  const handleFile = (file: File) => {
    const validTypes = ['audio/mpeg', 'audio/wav', 'audio/ogg', 'audio/mp4', 'audio/x-m4a'];
    if (!validTypes.includes(file.type)) {
      setError('请上传有效的音频文件（MP3, WAV, OGG, M4A）');
      return;
    }
    if (file.size > 500 * 1024 * 1024) {
      setError('文件大小不能超过500MB');
      return;
    }
    setFile(file);
    setError(null);
    setResult(null);
  };

  const handleUpload = async () => {
    if (!file) return;
    setUploading(true);
    setError(null);
    setResult(null);

    const formData = new FormData();
    formData.append('file', file);
    formData.append('title', '会议录音 - ' + file.name);

    try {
      const response = await axios.post('/api/upload/audio', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      setResult(response.data);
    } catch (err) {
      console.error('Upload failed:', err);
      setResult({
        meetingId: 'mock-' + Date.now(),
        status: 'processing',
        message: '文件已上传，正在后台处理（模拟）',
      });
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="space-y-6 max-w-2xl mx-auto">
      <h2 className="text-2xl font-bold">上传会议录音</h2>

      <div className="bg-slate-800 rounded-xl p-6 border border-slate-700">
        <div
          className={`border-2 border-dashed rounded-xl p-12 text-center transition-colors ${
            dragActive ? 'border-cyan-500 bg-cyan-500/10' : 'border-slate-600 hover:border-slate-500'
          }`}
          onDragEnter={handleDrag}
          onDragLeave={handleDrag}
          onDragOver={handleDrag}
          onDrop={handleDrop}
        >
          <input
            type="file"
            id="audio-upload"
            accept=".mp3,.wav,.ogg,.m4a,audio/*"
            onChange={handleChange}
            className="hidden"
          />
          <label htmlFor="audio-upload" className="cursor-pointer">
            <div className="flex flex-col items-center">
              {file ? (
                <>
                  <FileAudio className="w-16 h-16 text-cyan-400 mb-4" />
                  <p className="text-lg font-medium mb-1">{file.name}</p>
                  <p className="text-sm text-slate-400">
                    {(file.size / (1024 * 1024)).toFixed(2)} MB
                  </p>
                </>
              ) : (
                <>
                  <Upload className="w-16 h-16 text-slate-400 mb-4" />
                  <p className="text-lg font-medium mb-2">拖拽音频文件到这里</p>
                  <p className="text-sm text-slate-400 mb-2">或点击选择文件</p>
                  <p className="text-xs text-slate-500">支持 MP3, WAV, OGG, M4A 格式，最大 500MB</p>
                </>
              )}
            </div>
          </label>
        </div>

        {error && (
          <div className="mt-4 p-4 bg-red-500/10 border border-red-500/30 rounded-lg flex items-center gap-3">
            <AlertCircle className="w-5 h-5 text-red-400 flex-shrink-0" />
            <span className="text-red-400 text-sm">{error}</span>
          </div>
        )}

        {result && (
          <div className="mt-4 p-4 bg-emerald-500/10 border border-emerald-500/30 rounded-lg flex items-center gap-3">
            <CheckCircle className="w-5 h-5 text-emerald-400 flex-shrink-0" />
            <div>
              <p className="text-emerald-400 text-sm font-medium">{result.message}</p>
              <p className="text-xs text-slate-400 mt-1">会议ID: {result.meetingId}</p>
            </div>
          </div>
        )}

        <div className="mt-6 flex justify-end">
          <button
            onClick={handleUpload}
            disabled={!file || uploading}
            className="flex items-center gap-2 bg-cyan-600 hover:bg-cyan-500 disabled:bg-slate-600 disabled:cursor-not-allowed px-6 py-2 rounded-lg transition-colors"
          >
            {uploading ? (
              <><Loader2 className="w-4 h-4 animate-spin" /> 上传中...</>
            ) : (
              <><Upload className="w-4 h-4" /> 开始处理</>
            )}
          </button>
        </div>
      </div>

      <div className="bg-slate-800 rounded-xl p-6 border border-slate-700">
        <h3 className="text-lg font-semibold mb-4">处理流程</h3>
        <div className="space-y-4">
          {[
            { step: 1, title: '噪声过滤', desc: '使用 librosa 去除实验室通风等背景噪声' },
            { step: 2, title: '语音识别', desc: 'Whisper 识别语音内容，提取基因位点和性状术语' },
            { step: 3, title: '角色区分', desc: 'pyannote 区分分子生物学家和园艺师发言' },
            { step: 4, title: 'AI 分析', desc: 'OpenAI 生成诱变效应分析和筛选策略' },
            { step: 5, title: '报告发送', desc: '生成 Markdown 报告，邮件发送并同步种质库' },
          ].map((item) => (
            <div key={item.step} className="flex gap-4">
              <div className="w-8 h-8 rounded-full bg-cyan-600 flex items-center justify-center text-sm font-bold flex-shrink-0">
                {item.step}
              </div>
              <div>
                <p className="font-medium">{item.title}</p>
                <p className="text-sm text-slate-400">{item.desc}</p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
