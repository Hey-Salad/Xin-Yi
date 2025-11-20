'use client';

import { useState } from 'react';
import { X, Pen, Download, Check } from 'lucide-react';
import SignatureModal from './SignatureModal';

interface DocumentViewerProps {
  isOpen: boolean;
  onClose: () => void;
  documentName: string;
  documentUrl: string;
  onSign: (signatureData: string, signerName: string) => void;
  canSign?: boolean;
}

export default function DocumentViewer({
  isOpen,
  onClose,
  documentName,
  documentUrl,
  onSign,
  canSign = true,
}: DocumentViewerProps) {
  const [showSignatureModal, setShowSignatureModal] = useState(false);

  if (!isOpen) return null;

  const handleSignClick = () => {
    setShowSignatureModal(true);
  };

  const handleSaveSignature = (signatureData: string, signerName: string) => {
    onSign(signatureData, signerName);
    setShowSignatureModal(false);
  };

  return (
    <>
      <div
        className="fixed inset-0 bg-black/80 z-50 flex items-center justify-center p-4"
        onClick={onClose}
      >
        <div
          className="bg-zinc-900 rounded-xl w-full max-w-6xl h-[90vh] flex flex-col"
          onClick={(e) => e.stopPropagation()}
        >
          {/* Header */}
          <div className="flex items-center justify-between p-6 border-b border-zinc-800">
            <div>
              <h2 className="text-xl font-bold">{documentName}</h2>
              <p className="text-sm text-gray-400 mt-1">Review and sign this document</p>
            </div>
            <div className="flex items-center gap-3">
              {canSign && (
                <button
                  onClick={handleSignClick}
                  className="flex items-center gap-2 px-4 py-2 bg-[#ed4c4c] hover:bg-[#d93d3d] rounded-lg transition-colors"
                >
                  <Pen className="w-4 h-4" />
                  Sign Document
                </button>
              )}
              <button
                onClick={onClose}
                className="p-2 hover:bg-zinc-800 rounded-lg transition-colors"
              >
                <X className="w-5 h-5" />
              </button>
            </div>
          </div>

          {/* PDF Viewer */}
          <div className="flex-1 overflow-hidden bg-zinc-950 p-4">
            <iframe
              src={documentUrl}
              className="w-full h-full rounded-lg border border-zinc-800"
              title={documentName}
            />
          </div>

          {/* Footer */}
          <div className="p-6 border-t border-zinc-800 flex items-center justify-between">
            <div className="flex items-center gap-2 text-sm text-gray-400">
              <Check className="w-4 h-4" />
              <span>Scroll through the document to review all pages</span>
            </div>
            <div className="flex gap-3">
              <a
                href={documentUrl}
                download={documentName}
                className="flex items-center gap-2 px-4 py-2 bg-zinc-800 hover:bg-zinc-700 rounded-lg transition-colors"
              >
                <Download className="w-4 h-4" />
                Download
              </a>
            </div>
          </div>
        </div>
      </div>

      {/* Signature Modal */}
      <SignatureModal
        isOpen={showSignatureModal}
        onClose={() => setShowSignatureModal(false)}
        onSave={handleSaveSignature}
        documentName={documentName}
      />
    </>
  );
}
