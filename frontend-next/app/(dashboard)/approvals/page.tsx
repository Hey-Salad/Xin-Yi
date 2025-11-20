'use client';

import { useState, useEffect } from 'react';
import { FileText, Eye, Pen, Check, Clock, Download, X } from 'lucide-react';
import { useLanguage } from '@/lib/LanguageContext';
import { getTranslation } from '@/lib/i18n';
import SignatureModal from '@/components/SignatureModal';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:2124/api';

interface PendingDocument {
  id: string;
  name: string;
  type: string;
  category: string;
  generatedDate: string;
  status: 'pending' | 'signed' | 'rejected';
  requiredSigners: string[];
  signatures: Array<{
    signer: string;
    signedAt: string;
  }>;
  pdfUrl?: string;
}

// Dummy data for pending documents
const DUMMY_DOCUMENTS: PendingDocument[] = [
  {
    id: 'DOC-001',
    name: 'PO Receipt - November 2025',
    type: 'po-receipt',
    category: 'receiving',
    generatedDate: '2025-11-20T10:30:00',
    status: 'pending',
    requiredSigners: ['Warehouse Manager', 'Operations Director'],
    signatures: [],
  },
  {
    id: 'DOC-002',
    name: 'Inventory Report - Q4 2025',
    type: 'inventory-report',
    category: 'inventory',
    generatedDate: '2025-11-20T09:15:00',
    status: 'pending',
    requiredSigners: ['Inventory Manager', 'Finance Director'],
    signatures: [],
  },
  {
    id: 'DOC-003',
    name: 'Pick List - Order #12345',
    type: 'pick-list',
    category: 'fulfillment',
    generatedDate: '2025-11-20T08:00:00',
    status: 'signed',
    requiredSigners: ['Picker', 'Supervisor'],
    signatures: [
      { signer: 'John Smith', signedAt: '2025-11-20T08:30:00' },
      { signer: 'Jane Doe', signedAt: '2025-11-20T09:00:00' },
    ],
  },
  {
    id: 'DOC-004',
    name: 'Shipping Label - Delivery #789',
    type: 'shipping-label',
    category: 'fulfillment',
    generatedDate: '2025-11-19T16:45:00',
    status: 'pending',
    requiredSigners: ['Driver', 'Dispatcher'],
    signatures: [
      { signer: 'Mike Johnson', signedAt: '2025-11-19T17:00:00' },
    ],
  },
];

export default function ApprovalsPage() {
  const { language } = useLanguage();
  const [documents, setDocuments] = useState<PendingDocument[]>(DUMMY_DOCUMENTS);
  const [selectedDoc, setSelectedDoc] = useState<PendingDocument | null>(null);
  const [showSignatureModal, setShowSignatureModal] = useState(false);
  const [filter, setFilter] = useState<'all' | 'pending' | 'signed'>('all');
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);

  const filteredDocuments = documents.filter((doc) => {
    if (filter === 'all') return true;
    return doc.status === filter;
  });

  const handlePreview = async (doc: PendingDocument) => {
    // In real implementation, fetch the PDF from backend
    setSelectedDoc(doc);
    // For now, just show the modal
  };

  const handleSign = (doc: PendingDocument) => {
    setSelectedDoc(doc);
    setShowSignatureModal(true);
  };

  const handleSaveSignature = async (signatureData: string, signerName: string) => {
    if (!selectedDoc) return;

    try {
      // First generate the document, then sign it
      // Step 1: Generate the original document
      const generateResponse = await fetch(`${API_BASE_URL}/documents/${selectedDoc.category}/${selectedDoc.type}`, {
        method: 'GET',
      });

      if (!generateResponse.ok) {
        throw new Error('Failed to generate document');
      }

      const pdfBlob = await generateResponse.blob();
      
      // Step 2: Send to sign endpoint
      const signResponse = await fetch(`${API_BASE_URL}/documents/${selectedDoc.category}/${selectedDoc.type}/sign`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          signature: signatureData,
          signer_name: signerName,
        }),
      });

      if (signResponse.ok) {
        // Update local state
        setDocuments((prev) =>
          prev.map((doc) =>
            doc.id === selectedDoc.id
              ? {
                  ...doc,
                  signatures: [
                    ...doc.signatures,
                    { signer: signerName, signedAt: new Date().toISOString() },
                  ],
                  status:
                    doc.signatures.length + 1 >= doc.requiredSigners.length
                      ? 'signed'
                      : 'pending',
                }
              : doc
          )
        );

        // Download signed document
        const blob = await signResponse.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `${selectedDoc.type}_signed_${new Date().toISOString().split('T')[0]}.pdf`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);

        alert(language === 'en' ? 'Document signed successfully!' : '文档签署成功！');
      } else {
        const errorText = await signResponse.text();
        console.error('Sign error:', errorText);
        throw new Error('Failed to sign document');
      }
    } catch (error) {
      console.error('Error signing document:', error);
      alert(language === 'en' ? 'Failed to sign document. Please try again.' : '签署文档失败，请重试。');
    }
  };

  const handleDownload = async (doc: PendingDocument) => {
    try {
      const response = await fetch(`${API_BASE_URL}/documents/${doc.category}/${doc.type}`, {
        method: 'GET',
      });

      if (response.ok) {
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `${doc.type}_${new Date().toISOString().split('T')[0]}.pdf`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
      }
    } catch (error) {
      console.error('Error downloading document:', error);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'signed':
        return 'bg-green-500/10 text-green-500';
      case 'pending':
        return 'bg-yellow-500/10 text-yellow-500';
      case 'rejected':
        return 'bg-red-500/10 text-red-500';
      default:
        return 'bg-gray-500/10 text-gray-500';
    }
  };

  const stats = {
    total: documents.length,
    pending: documents.filter((d) => d.status === 'pending').length,
    signed: documents.filter((d) => d.status === 'signed').length,
  };

  return (
    <div>
      {/* Header */}
      <div className="flex justify-between items-center mb-8">
        <h1 className="text-3xl font-bold flex items-center gap-3">
          <FileText className="w-8 h-8" />
          {getTranslation(language, 'approvals')}
        </h1>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-6">
          <div className="text-3xl font-bold">{stats.total}</div>
          <div className="text-sm text-gray-400">{language === 'en' ? 'Total Documents' : '总文档数'}</div>
        </div>
        <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-6">
          <div className="text-3xl font-bold text-yellow-500">{stats.pending}</div>
          <div className="text-sm text-gray-400">{language === 'en' ? 'Pending Approval' : '待审批'}</div>
        </div>
        <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-6">
          <div className="text-3xl font-bold text-green-500">{stats.signed}</div>
          <div className="text-sm text-gray-400">{language === 'en' ? 'Signed' : '已签署'}</div>
        </div>
      </div>

      {/* Filter Tabs */}
      <div className="flex gap-2 mb-6">
        <button
          onClick={() => setFilter('all')}
          className={`px-4 py-2 rounded-lg transition-colors ${
            filter === 'all'
              ? 'bg-[#ed4c4c] text-white'
              : 'bg-zinc-900 border border-zinc-800 hover:bg-zinc-800'
          }`}
        >
          {language === 'en' ? 'All' : '全部'} ({documents.length})
        </button>
        <button
          onClick={() => setFilter('pending')}
          className={`px-4 py-2 rounded-lg transition-colors ${
            filter === 'pending'
              ? 'bg-[#ed4c4c] text-white'
              : 'bg-zinc-900 border border-zinc-800 hover:bg-zinc-800'
          }`}
        >
          {language === 'en' ? 'Pending' : '待审批'} ({stats.pending})
        </button>
        <button
          onClick={() => setFilter('signed')}
          className={`px-4 py-2 rounded-lg transition-colors ${
            filter === 'signed'
              ? 'bg-[#ed4c4c] text-white'
              : 'bg-zinc-900 border border-zinc-800 hover:bg-zinc-800'
          }`}
        >
          {language === 'en' ? 'Signed' : '已签署'} ({stats.signed})
        </button>
      </div>

      {/* Documents List */}
      <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-6">
        <div className="space-y-4">
          {filteredDocuments.map((doc) => (
            <div
              key={doc.id}
              className="bg-black border border-zinc-800 rounded-lg p-6 hover:border-zinc-700 transition-colors"
            >
              <div className="flex items-start justify-between mb-4">
                <div className="flex-1">
                  <div className="flex items-center gap-3 mb-2">
                    <h3 className="text-lg font-semibold">{doc.name}</h3>
                    <span className={`px-3 py-1 rounded-full text-xs font-semibold ${getStatusColor(doc.status)}`}>
                      {doc.status.charAt(0).toUpperCase() + doc.status.slice(1)}
                    </span>
                  </div>
                  <p className="text-sm text-gray-400 mb-1">
                    {language === 'en' ? 'Document ID:' : '文档编号:'} {doc.id}
                  </p>
                  <p className="text-sm text-gray-400">
                    {language === 'en' ? 'Generated:' : '生成时间:'}{' '}
                    {new Date(doc.generatedDate).toLocaleString()}
                  </p>
                </div>
              </div>

              {/* Signatures Progress */}
              <div className="mb-4">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm font-semibold text-gray-400">
                    {language === 'en' ? 'Signatures' : '签名'} ({doc.signatures.length}/{doc.requiredSigners.length})
                  </span>
                </div>
                <div className="space-y-2">
                  {doc.requiredSigners.map((signer, idx) => {
                    const signature = doc.signatures.find((s) => s.signer === signer);
                    return (
                      <div key={idx} className="flex items-center gap-2 text-sm">
                        {signature ? (
                          <>
                            <Check className="w-4 h-4 text-green-500" />
                            <span className="text-green-500">{signer}</span>
                            <span className="text-gray-500">
                              - {new Date(signature.signedAt).toLocaleString()}
                            </span>
                          </>
                        ) : (
                          <>
                            <Clock className="w-4 h-4 text-yellow-500" />
                            <span className="text-gray-400">{signer}</span>
                            <span className="text-gray-500">- {language === 'en' ? 'Pending' : '待签署'}</span>
                          </>
                        )}
                      </div>
                    );
                  })}
                </div>
              </div>

              {/* Actions */}
              <div className="flex gap-3">
                <button
                  onClick={() => handlePreview(doc)}
                  className="flex items-center gap-2 px-4 py-2 bg-zinc-800 hover:bg-zinc-700 rounded-lg transition-colors"
                >
                  <Eye className="w-4 h-4" />
                  {language === 'en' ? 'Preview' : '预览'}
                </button>
                <button
                  onClick={() => handleDownload(doc)}
                  className="flex items-center gap-2 px-4 py-2 bg-zinc-800 hover:bg-zinc-700 rounded-lg transition-colors"
                >
                  <Download className="w-4 h-4" />
                  {language === 'en' ? 'Download' : '下载'}
                </button>
                {doc.status === 'pending' && (
                  <button
                    onClick={() => handleSign(doc)}
                    className="flex items-center gap-2 px-4 py-2 bg-[#ed4c4c] hover:bg-[#d93d3d] rounded-lg transition-colors"
                  >
                    <Pen className="w-4 h-4" />
                    {language === 'en' ? 'Sign Document' : '签署文档'}
                  </button>
                )}
              </div>
            </div>
          ))}

          {filteredDocuments.length === 0 && (
            <div className="text-center py-12 text-gray-400">
              {language === 'en' ? 'No documents found' : '未找到文档'}
            </div>
          )}
        </div>
      </div>

      {/* Signature Modal */}
      <SignatureModal
        isOpen={showSignatureModal}
        onClose={() => {
          setShowSignatureModal(false);
          setSelectedDoc(null);
        }}
        onSave={handleSaveSignature}
        documentName={selectedDoc?.name || ''}
      />
    </div>
  );
}
