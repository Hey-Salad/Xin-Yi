'use client';

import { useRef, useState } from 'react';
import SignatureCanvas from 'react-signature-canvas';
import { X, Pen, Check } from 'lucide-react';

interface SignatureModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSave: (signatureData: string, signerName: string) => void;
  documentName: string;
}

export default function SignatureModal({ 
  isOpen, 
  onClose, 
  onSave, 
  documentName 
}: SignatureModalProps) {
  const sigCanvas = useRef<SignatureCanvas>(null);
  const [isEmpty, setIsEmpty] = useState(true);
  const [signerName, setSignerName] = useState('');

  const clear = () => {
    sigCanvas.current?.clear();
    setIsEmpty(true);
  };

  const save = () => {
    if (sigCanvas.current && !isEmpty && signerName.trim()) {
      const signatureData = sigCanvas.current.toDataURL('image/png');
      onSave(signatureData, signerName);
      clear();
      setSignerName('');
      onClose();
    }
  };

  if (!isOpen) return null;

  return (
    <div 
      className="fixed inset-0 bg-black/70 z-50 flex items-center justify-center p-4"
      onClick={onClose}
    >
      <div 
        className="bg-zinc-900 border border-zinc-800 rounded-xl max-w-2xl w-full p-6"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="flex justify-between items-center mb-4">
          <div className="flex items-center gap-2">
            <Pen className="w-5 h-5 text-[#ed4c4c]" />
            <h2 className="text-xl font-bold">Sign Document</h2>
          </div>
          <button 
            onClick={onClose} 
            className="p-2 hover:bg-zinc-800 rounded-lg transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Document Name */}
        <div className="bg-zinc-800/50 rounded-lg p-3 mb-4">
          <p className="text-sm text-gray-400">Document:</p>
          <p className="font-semibold">{documentName}</p>
        </div>

        {/* Signer Name Input */}
        <div className="mb-4">
          <label className="block text-sm font-semibold text-gray-400 mb-2">
            Your Name *
          </label>
          <input
            type="text"
            value={signerName}
            onChange={(e) => setSignerName(e.target.value)}
            placeholder="Enter your full name"
            className="w-full px-4 py-2 bg-zinc-800 border border-zinc-700 rounded-lg focus:outline-none focus:border-[#ed4c4c]"
          />
        </div>

        {/* Signature Canvas */}
        <div className="mb-4">
          <label className="block text-sm font-semibold text-gray-400 mb-2">
            Signature *
          </label>
          <div className="border-2 border-zinc-700 rounded-lg bg-white overflow-hidden">
            <SignatureCanvas
              ref={sigCanvas}
              canvasProps={{
                className: 'w-full h-64 cursor-crosshair',
              }}
              onEnd={() => setIsEmpty(false)}
              backgroundColor="white"
              penColor="black"
            />
          </div>
          <p className="text-xs text-gray-500 mt-2">
            Sign above using your mouse or touchscreen
          </p>
        </div>

        {/* Action Buttons */}
        <div className="flex gap-3 justify-end">
          <button
            onClick={clear}
            className="px-4 py-2 bg-zinc-800 hover:bg-zinc-700 rounded-lg transition-colors"
          >
            Clear Signature
          </button>
          <button
            onClick={save}
            disabled={isEmpty || !signerName.trim()}
            className="flex items-center gap-2 px-4 py-2 bg-[#ed4c4c] hover:bg-[#d93d3d] rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <Check className="w-4 h-4" />
            Save & Sign
          </button>
        </div>
      </div>
    </div>
  );
}
