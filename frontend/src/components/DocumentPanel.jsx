import { useState, useEffect, useRef } from 'react';

const API_BASE = 'http://localhost:8000';

export default function DocumentPanel() {
  const [documents, setDocuments] = useState([]);
  const [isDragging, setIsDragging] = useState(false);
  const [uploadStatus, setUploadStatus] = useState(null);
  const [isLoadingDocs, setIsLoadingDocs] = useState(true);
  const fileInputRef = useRef(null);

  // Fetch documents on mount
  useEffect(() => {
    fetchDocuments();
  }, []);

  const fetchDocuments = async () => {
    try {
      const response = await fetch(`${API_BASE}/api/documents`);
      if (response.ok) {
        const data = await response.json();
        setDocuments(data);
      }
    } catch (error) {
      console.error('Failed to fetch documents:', error);
    } finally {
      setIsLoadingDocs(false);
    }
  };

  const handleUpload = async (file) => {
    if (!file) return;

    const ext = file.name.split('.').pop().toLowerCase();
    if (!['txt', 'pdf'].includes(ext)) {
      setUploadStatus({ type: 'error', message: `Unsupported file type: .${ext}. Use .txt or .pdf` });
      return;
    }

    setUploadStatus({ type: 'loading', message: `Uploading and processing ${file.name}...` });

    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await fetch(`${API_BASE}/api/documents/upload`, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) throw new Error('Upload failed');

      const data = await response.json();
      setUploadStatus({
        type: 'success',
        message: `✅ "${data.doc_name}" uploaded successfully (${data.chunk_count} chunks created)`,
      });
      fetchDocuments();
    } catch (error) {
      setUploadStatus({
        type: 'error',
        message: `❌ Failed to upload: ${error.message}. Is the backend running?`,
      });
    }

    // Clear status after 5 seconds
    setTimeout(() => setUploadStatus(null), 5000);
  };

  const handleDelete = async (docId, docName) => {
    if (!confirm(`Delete "${docName}" from the knowledge base?`)) return;

    try {
      const response = await fetch(`${API_BASE}/api/documents/${docId}`, {
        method: 'DELETE',
      });

      if (response.ok) {
        setUploadStatus({
          type: 'success',
          message: `🗑️ "${docName}" deleted successfully`,
        });
        fetchDocuments();
      } else {
        throw new Error('Delete failed');
      }
    } catch (error) {
      setUploadStatus({
        type: 'error',
        message: `❌ Failed to delete: ${error.message}`,
      });
    }

    setTimeout(() => setUploadStatus(null), 5000);
  };

  // Drag and drop handlers
  const handleDragOver = (e) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    setIsDragging(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragging(false);
    const file = e.dataTransfer.files[0];
    if (file) handleUpload(file);
  };

  const handleFileSelect = (e) => {
    const file = e.target.files[0];
    if (file) handleUpload(file);
    e.target.value = '';
  };

  const getDocIcon = (name) => {
    if (name.endsWith('.pdf')) return '📕';
    if (name.endsWith('.txt')) return '📄';
    return '📎';
  };

  return (
    <div className="document-panel">
      <div className="doc-header">
        <h2>📄 Knowledge Base</h2>
        <p>Upload equity documents to expand the AI assistant's knowledge</p>
      </div>

      <div className="doc-content">
        {/* Upload Zone */}
        <div
          className={`upload-zone ${isDragging ? 'dragging' : ''}`}
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
          onClick={() => fileInputRef.current?.click()}
        >
          <div className="upload-icon">📤</div>
          <h3>Drop files here or click to upload</h3>
          <p>Supports PDF and TXT files</p>
          <input
            ref={fileInputRef}
            type="file"
            accept=".pdf,.txt"
            onChange={handleFileSelect}
          />
        </div>

        {/* Upload Status */}
        {uploadStatus && (
          <div className={`upload-status ${uploadStatus.type}`}>
            {uploadStatus.message}
          </div>
        )}

        {/* Document List */}
        <div className="doc-list-title">
          Ingested Documents ({documents.length})
        </div>

        <div className="doc-list">
          {isLoadingDocs ? (
            <div style={{ textAlign: 'center', padding: '20px', color: 'var(--text-muted)' }}>
              Loading documents...
            </div>
          ) : documents.length === 0 ? (
            <div style={{ textAlign: 'center', padding: '20px', color: 'var(--text-muted)' }}>
              No documents yet. Upload files or start the backend to load sample documents.
            </div>
          ) : (
            documents.map((doc) => (
              <div key={doc.doc_id} className="doc-item">
                <span className="doc-icon">{getDocIcon(doc.doc_name)}</span>
                <div className="doc-item-info">
                  <h4>{doc.doc_name}</h4>
                  <span>{doc.chunk_count} chunks indexed</span>
                </div>
                <button
                  className="doc-delete-btn"
                  onClick={() => handleDelete(doc.doc_id, doc.doc_name)}
                >
                  Delete
                </button>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
}
